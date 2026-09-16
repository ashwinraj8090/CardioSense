
from datetime import datetime
from flask import Blueprint, request, jsonify, g

from extensions import db
from models.device import Device
from models.session import MonitoringSession
from utils.auth_utils import login_required

sessions_bp = Blueprint("sessions", __name__, url_prefix="/api/sessions")


@sessions_bp.route("", methods=["POST"])
@login_required
def start_session():
    data = request.get_json(silent=True) or {}
    device_id_str = data.get("device_id")

    device = Device.query.filter_by(id=device_id_str, user_id=g.current_user.id).first()
    if device is None:
        return jsonify({"error": "Device not found or not owned by you"}), 404

    # Auto-close any dangling active session on this device before starting a new one.
    existing = MonitoringSession.query.filter_by(device_id=device.id, ended_at=None).first()
    if existing:
        existing.ended_at = datetime.utcnow()

    session = MonitoringSession(user_id=g.current_user.id, device_id=device.id)
    db.session.add(session)
    db.session.commit()

    return jsonify(session.to_public_dict()), 201


@sessions_bp.route("/<int:session_id>/stop", methods=["POST"])
@login_required
def stop_session(session_id):
    session = MonitoringSession.query.filter_by(id=session_id, user_id=g.current_user.id).first()
    if session is None:
        return jsonify({"error": "Session not found"}), 404
    if not session.is_active:
        return jsonify({"error": "Session already stopped"}), 409

    session.ended_at = datetime.utcnow()
    db.session.commit()
    return jsonify(session.to_public_dict()), 200


@sessions_bp.route("/current", methods=["GET"])
@login_required
def current_session():
    session = MonitoringSession.query.filter_by(
        user_id=g.current_user.id, ended_at=None
    ).order_by(MonitoringSession.started_at.desc()).first()

    if session is None:
        return jsonify({"active_session": None}), 200
    return jsonify({"active_session": session.to_public_dict()}), 200
