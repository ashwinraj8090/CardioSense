"""
routes/readings.py
-------------------
POST /api/readings         - ESP32 posts one sensor packet (device-authenticated)
GET  /api/readings/latest   - frontend polls for the newest reading+prediction (JWT-authenticated)
GET  /api/readings/history  - frontend fetches this session's/user's history (JWT-authenticated)

This route is the direct replacement for the old, unauthenticated
`/iot-update` + global `latest_vitals` dict. Every step below closes one
of the audit findings:

  OLD: anyone could POST to /iot-update.
  NEW: @device_auth_required -- only a device with a valid device_id +
       device_secret can post, and we derive the OWNING USER from that
       device row, never from anything in the request body.

  OLD: one global Python dict shared by every user (race condition, no
       isolation).
  NEW: every reading is written to `vital_readings`, scoped to a specific
       session_id -> user_id. Two devices posting "simultaneously" just
       become two independent database rows; nothing is overwritten.

  OLD: HRV/BP computed in browser JS, lost on refresh.
  NEW: computed here via services/signal_processing.py, state persisted
       on the session row.

  OLD: /predict never applied the training-time scaler.
  NEW: services/prediction_service.py always scales inside the saved
       Pipeline object -- there's no code path that can skip it.
"""
from flask import Blueprint, request, jsonify, g

from extensions import db
from models.session import MonitoringSession
from models.reading import VitalReading
from models.prediction import RiskPrediction
from utils.device_auth import device_auth_required
from utils.auth_utils import login_required
from services.signal_processing import process_sample
from services.prediction_service import predict_risk
from flask_limiter.util import get_remote_address
from extensions import db, limiter

readings_bp = Blueprint("readings", __name__, url_prefix="/api/readings")

def _device_key():
    return request.headers.get("X-Device-Id", get_remote_address())

@readings_bp.route("", methods=["POST"])
@device_auth_required
@limiter.limit("120 per minute", key_func=_device_key)
def post_reading():
    data = request.get_json(silent=True) or {}

    # --- Input validation (Part 27) ---
    try:
        ecg = float(data.get("ecg", 0))
        ppg = float(data.get("ppg", 0))
        hr = float(data.get("hr", 0))
        spo2 = float(data.get("spo2", 0))
    except (TypeError, ValueError):
        return jsonify({"error": "ecg, ppg, hr, spo2 must be numbers"}), 400

    if not (0 <= hr <= 250):
        return jsonify({"error": "hr out of realistic range"}), 422
    if not (0 <= spo2 <= 100):
        return jsonify({"error": "spo2 out of realistic range"}), 422

    device = g.current_device
    user = g.current_user

    session = MonitoringSession.query.filter_by(device_id=device.id, ended_at=None).first()
    if session is None:
        # This is intentional: we do NOT silently create a session or
        # silently drop the packet into nowhere. The dashboard must have
        # explicitly clicked "Start Monitoring" first (Part 13).
        return jsonify({"error": "No active monitoring session for this device"}), 409

    # --- Signal processing (server-side now, see services/signal_processing.py) ---
    state = session.get_signal_state()
    result = process_sample(state, ecg, ppg)
    session.set_signal_state(result["state"])

    reading = VitalReading(
        session_id=session.id,
        ecg=ecg, ppg=ppg,
        heart_rate=hr, spo2=spo2,
        hrv=result["hrv"],
        systolic_bp=result["systolic"],
        diastolic_bp=result["diastolic"],
    )
    db.session.add(reading)
    db.session.flush()  # get reading.id before commit

    prediction = None
    # Only run the ML model once we have a full, real feature vector --
    # never substitute a guessed/default HRV or BP just to produce a number.
    if result["hrv"] is not None and result["systolic"] is not None:
        pred = predict_risk(
            hr=hr, spo2=spo2, hrv=result["hrv"],
            systolic=result["systolic"], diastolic=result["diastolic"],
            age=user.age, bmi=user.bmi,
        )
        prediction = RiskPrediction(
            session_id=session.id,
            reading_id=reading.id,
            risk_probability=pred["risk"],
            risk_level=pred["risk_level"],
        )
        db.session.add(prediction)

    db.session.commit()

    return jsonify({
        "reading": reading.to_public_dict(),
        "prediction": prediction.to_public_dict() if prediction else None,
    }), 201


@readings_bp.route("/latest", methods=["GET"])
@login_required
def latest_reading():
    session = MonitoringSession.query.filter_by(
        user_id=g.current_user.id, ended_at=None
    ).order_by(MonitoringSession.started_at.desc()).first()

    if session is None:
        return jsonify({"status": "no_active_session"}), 200

    reading = VitalReading.query.filter_by(session_id=session.id).order_by(
        VitalReading.timestamp.desc()
    ).first()
    prediction = RiskPrediction.query.filter_by(session_id=session.id).order_by(
        RiskPrediction.timestamp.desc()
    ).first()

    if reading is None:
        return jsonify({"status": "awaiting_first_reading"}), 200

    return jsonify({
        "status": "ok",
        "reading": reading.to_public_dict(),
        "prediction": prediction.to_public_dict() if prediction else None,
    }), 200


@readings_bp.route("/history", methods=["GET"])
@login_required
def reading_history():
    limit = min(int(request.args.get("limit", 100)), 500)

    session_ids = [
        s.id for s in MonitoringSession.query.filter_by(user_id=g.current_user.id).all()
    ]
    readings = (
        VitalReading.query.filter(VitalReading.session_id.in_(session_ids))
        .order_by(VitalReading.timestamp.desc())
        .limit(limit)
        .all()
    )
    return jsonify([r.to_public_dict() for r in reversed(readings)]), 200

