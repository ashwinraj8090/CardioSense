"""
models/prediction.py
---------------------
WHAT: The `risk_predictions` table. One row per time the ML model was run.
WHY:  Kept separate from vital_readings (rather than adding risk columns
      onto that table) because a reading and a prediction are different
      *kinds* of fact: a reading is a sensor measurement, a prediction is
      a model's opinion about that measurement. Keeping them separate
      means you could later re-run an improved model over historical
      readings and get new prediction rows without touching the original
      sensor data — you can't do that cleanly if they're the same row.
"""
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
