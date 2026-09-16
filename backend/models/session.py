"""
models/session.py
------------------
WHAT: The `monitoring_sessions` table. One row per "Start Monitoring" ->
      "Stop Monitoring" cycle.
WHY:  Without a session concept, all of a user's readings would just be
      one giant undifferentiated pile with no way to tell "this was
      Tuesday's 5-minute check" from "this was last week's". Sessions
      give you natural history buckets and let the same user use two
      different devices at different times without their readings mixing.

- `signal_state` stores the small amount of state needed to compute HRV
  and BP incrementally as readings stream in (last R-peak time, recent
  RR intervals, filtered ECG value). This used to live in browser
  JavaScript variables (lost on refresh); moving it server-side means the
  session survives a page reload and multiple ESP32 packets accumulate
  correctly. It's stored as JSON text — simple, no need for a separate
  table for a handful of numbers.
"""
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

    # JSON blob: {"filtered_ecg": 0, "last_r_peak_time": 0,
    #             "rr_intervals": [...], "last_ppg_peak_time": 0}
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
