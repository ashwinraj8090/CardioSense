"""
utils/device_auth.py
---------------------
WHAT: Authentication for the ESP32, which is a machine, not a human --
      it doesn't "log in" with a JWT flow. Instead it presents a
      device_id + device_secret with every request, like an API key.
WHY:  This directly answers "how does the server know which user's ESP32
      sent this data?" (see models/device.py for the full explanation).
      Without this, `/api/readings` would be exactly as broken as the old
      `/iot-update` -- open to literally anyone with curl.
HOW:  The ESP32 sends headers:
        X-Device-Id: esp32-ab12cd
        X-Device-Secret: <the secret it was provisioned with>
      We look up the device by device_id, hash-compare the secret (same
      technique as password checking), confirm status == 'active', and
      attach both the Device row and its owning User to flask.g.
"""
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
