
import requests
from flask import Blueprint, request, jsonify, g, current_app

from models.session import MonitoringSession
from models.reading import VitalReading
from models.prediction import RiskPrediction
from utils.auth_utils import login_required

chat_bp = Blueprint("chat", __name__, url_prefix="/api/chat")

SYSTEM_PROMPT = (
    "You are CardioSense, an AI-powered cardiac health assistant. "
    "Use calm, medical, and reassuring language. Interpret heart rate, "
    "SpO2, HRV, blood pressure and risk score. Mention stability or "
    "trends when possible. Do NOT diagnose diseases. If risk is low, "
    "reassure. If risk is moderate, advise caution. If risk is high, be "
    "safety-focused. Always recommend consulting a healthcare "
    "professional. Limit responses to 3-5 sentences."
)


def _latest_context(user_id: int) -> str:
    session = MonitoringSession.query.filter_by(user_id=user_id).order_by(
        MonitoringSession.started_at.desc()
    ).first()
    if session is None:
        return "No monitoring data is available yet for this user."

    reading = VitalReading.query.filter_by(session_id=session.id).order_by(
        VitalReading.timestamp.desc()
    ).first()
    prediction = RiskPrediction.query.filter_by(session_id=session.id).order_by(
        RiskPrediction.timestamp.desc()
    ).first()

    if reading is None:
        return "A monitoring session is active but no readings have arrived yet."

    parts = [
        f"HR={reading.heart_rate}", f"SpO2={reading.spo2}%",
        f"HRV={reading.hrv}", f"BP={reading.systolic_bp}/{reading.diastolic_bp}",
    ]
    if prediction:
        parts.append(f"Risk={prediction.risk_probability}% ({prediction.risk_level})")
    return "Current vitals: " + ", ".join(parts)


@chat_bp.route("", methods=["POST"])
@login_required
def chat():
    data = request.get_json(silent=True) or {}
    user_message = (data.get("message") or "").strip()
    if not user_message:
        return jsonify({"reply": "Please ask something."}), 200

    api_key = current_app.config["GEMINI_API_KEY"]
    if not api_key:
        return jsonify({"reply": "AI assistant is not configured on the server."}), 503

    context = _latest_context(g.current_user.id)
    full_prompt = f"{SYSTEM_PROMPT}\n\n{context}\n\nUser question: {user_message}"

    url = (
        f"https://generativelanguage.googleapis.com/v1beta/models/"
        f"{current_app.config['GEMINI_MODEL']}:generateContent?key={api_key}"
    )
    payload = {"contents": [{"parts": [{"text": full_prompt}]}]}

    try:
        resp = requests.post(url, json=payload, timeout=15)
        resp.raise_for_status()
        result = resp.json()
        reply = (
            result.get("candidates", [{}])[0]
            .get("content", {})
            .get("parts", [{}])[0]
            .get("text", "No response")
        )
    except requests.RequestException as e:
        current_app.logger.error(f"Gemini call failed: {e}")
        return jsonify({"reply": "The AI assistant is temporarily unavailable."}), 502

    return jsonify({"reply": reply}), 200
