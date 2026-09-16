
from functools import wraps
from flask import request, jsonify, g
from werkzeug.security import check_password_hash

from models.device import Device


def device_auth_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        device_id = request.headers.get("X-Device-Id")
        device_secret = request.headers.get("X-Device-Secret")

        if not device_id or not device_secret:
            return jsonify({"error": "Missing device credentials"}), 401

        device = Device.query.filter_by(device_id=device_id).first()
        if device is None or not check_password_hash(device.device_secret_hash, device_secret):
            return jsonify({"error": "Invalid device credentials"}), 401

        if device.status != "active":
            return jsonify({"error": "Device is not active"}), 403

        g.current_device = device
        g.current_user = device.owner  # the User who registered this device
        return fn(*args, **kwargs)

    return wrapper
