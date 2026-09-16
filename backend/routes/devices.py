
import secrets
from flask import Blueprint, request, jsonify, g
from werkzeug.security import generate_password_hash

from extensions import db
from models.device import Device
from utils.auth_utils import login_required

devices_bp = Blueprint("devices", __name__, url_prefix="/api/devices")


@devices_bp.route("", methods=["POST"])
@login_required
def register_device():
    data = request.get_json(silent=True) or {}
    device_id = (data.get("device_id") or "").strip()
    label = (data.get("label") or "My ESP32").strip()

    if not device_id:
        return jsonify({"error": "device_id is required"}), 422

    if Device.query.filter_by(device_id=device_id).first():
        return jsonify({"error": "This device_id is already registered"}), 409

    plaintext_secret = secrets.token_urlsafe(24)

    device = Device(
        user_id=g.current_user.id,
        device_id=device_id,
        device_secret_hash=generate_password_hash(plaintext_secret),
        label=label,
        status="active",
    )
    db.session.add(device)
    db.session.commit()

    return jsonify({
        "device": device.to_public_dict(),
        "device_secret": plaintext_secret,
        "warning": "Save this secret now -- it will not be shown again. Flash it onto the ESP32.",
    }), 201


@devices_bp.route("", methods=["GET"])
@login_required
def list_devices():
    devices = Device.query.filter_by(user_id=g.current_user.id).all()
    return jsonify([d.to_public_dict() for d in devices]), 200
