
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
