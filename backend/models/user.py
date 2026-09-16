
from datetime import datetime, date
from extensions import db


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    dob = db.Column(db.Date, nullable=False)

    height_cm = db.Column(db.Float, nullable=False)
    weight_kg = db.Column(db.Float, nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    devices = db.relationship("Device", backref="owner", lazy=True)
    sessions = db.relationship("MonitoringSession", backref="owner", lazy=True)

    @property
    def age(self) -> int:
        """Derived the same way the old dashboard did it client-side,
        just moved server-side so it can't be tampered with from the browser."""
        today = date.today()
        years = today.year - self.dob.year
        if (today.month, today.day) < (self.dob.month, self.dob.day):
            years -= 1
        return years

    @property
    def bmi(self) -> float:
        """BMI = weight(kg) / height(m)^2 — standard formula."""
        height_m = self.height_cm / 100.0
        return round(self.weight_kg / (height_m ** 2), 1)

    def to_public_dict(self):
        """What's safe to send to the frontend. NEVER include password_hash."""
        return {
            "id": self.id,
            "username": self.username,
            "age": self.age,
            "height_cm": self.height_cm,
            "weight_kg": self.weight_kg,
            "bmi": self.bmi,
        }
