"""
models/reading.py
------------------
WHAT: The `vital_readings` table. One row per sensor packet processed.
WHY:  This is real persistent history, replacing the old
      `hrHistory_<username>` / `spo2History_<username>` localStorage
      arrays. Storing one row per reading (rather than one JSON blob per
      user) is what lets you: query by time range, join with sessions,
      aggregate/trend, and paginate — none of which are realistically
      possible if history is one growing JSON array in a browser.
"""
from datetime import datetime
from extensions import db


class VitalReading(db.Model):
    __tablename__ = "vital_readings"

    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey("monitoring_sessions.id"), nullable=False, index=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    ecg = db.Column(db.Float)
    ppg = db.Column(db.Float)
    heart_rate = db.Column(db.Float)
    spo2 = db.Column(db.Float)
    hrv = db.Column(db.Float, nullable=True)          # null until enough RR intervals collected
    systolic_bp = db.Column(db.Float, nullable=True)
    diastolic_bp = db.Column(db.Float, nullable=True)

    def to_public_dict(self):
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat(),
            "hr": self.heart_rate,
            "spo2": self.spo2,
            "hrv": self.hrv,
            "systolic": self.systolic_bp,
            "diastolic": self.diastolic_bp,
            # ecg/ppg included so the dashboard's live waveform chart has
            # something to plot per poll -- same numbers the ESP32 sent.
            "ecg": self.ecg,
            "ppg": self.ppg,
        }
