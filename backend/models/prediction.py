
from datetime import datetime
from extensions import db


class RiskPrediction(db.Model):
    __tablename__ = "risk_predictions"

    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey("monitoring_sessions.id"), nullable=False, index=True)
    reading_id = db.Column(db.Integer, db.ForeignKey("vital_readings.id"), nullable=True, index=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    risk_probability = db.Column(db.Float, nullable=False)   # 0-100 %
    risk_level = db.Column(db.String(10), nullable=False)    # LOW | MEDIUM | HIGH

    def to_public_dict(self):
        return {
            "timestamp": self.timestamp.isoformat(),
            "risk": self.risk_probability,
            "risk_level": self.risk_level,
        }
