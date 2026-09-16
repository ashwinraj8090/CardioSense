"""
models/device.py
-----------------
WHAT: The `devices` table. Represents one physical ESP32 unit.
WHY:  This answers the exact interview question you listed: "How does the
      server know which user's ESP32 is sending this data?"

      Answer: the ESP32 doesn't send a username or user_id at all. It
      sends its own device_id + a secret credential. The server looks up
      *that device* in this table, finds its `user_id` foreign key, and
      that's how ownership is derived — never trusted from the request
      body itself.

Design notes:
- `device_id` is a public-ish identifier (like a serial number) — fine to
  put in an ESP32's source code.
- `device_secret_hash` is the hashed version of a secret token that is
  ALSO flashed onto the ESP32. It plays the same role a password plays
  for a human: proof the request really comes from that device. Hashed
  the same way user passwords are, for the same reason (DB leak safety).
- `status` lets us mark a device active/revoked (e.g. if a device is
  lost or compromised) without deleting its historical readings.
"""
from datetime import datetime
from extensions import db


class Device(db.Model):
    __tablename__ = "devices"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)

    device_id = db.Column(db.String(64), unique=True, nullable=False, index=True)
    device_secret_hash = db.Column(db.String(255), nullable=False)

    label = db.Column(db.String(80), default="My ESP32")
    status = db.Column(db.String(20), default="active")  # active | revoked
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    sessions = db.relationship("MonitoringSession", backref="device", lazy=True)

    def to_public_dict(self):
        return {
            "id": self.id,
            "device_id": self.device_id,
            "label": self.label,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
        }
