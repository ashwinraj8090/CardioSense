
import json
from datetime import datetime
from extensions import db


class MonitoringSession(db.Model):
    __tablename__ = "monitoring_sessions"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    device_id = db.Column(db.Integer, db.ForeignKey("devices.id"), nullable=False, index=True)

    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    ended_at = db.Column(db.DateTime, nullable=True)

    signal_state = db.Column(db.Text, default="{}")

    readings = db.relationship("VitalReading", backref="session", lazy=True)
    predictions = db.relationship("RiskPrediction", backref="session", lazy=True)

    @property
    def is_active(self):
        return self.ended_at is None

    def get_signal_state(self) -> dict:
        return json.loads(self.signal_state or "{}")

    def set_signal_state(self, state: dict):
        self.signal_state = json.dumps(state)

    def to_public_dict(self):
        return {
            "id": self.id,
            "device_id": self.device_id,
            "started_at": self.started_at.isoformat(),
            "ended_at": self.ended_at.isoformat() if self.ended_at else None,
            "is_active": self.is_active,
        }
