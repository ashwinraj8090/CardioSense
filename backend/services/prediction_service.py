
import os
import joblib
import pandas as pd

FEATURE_ORDER = ["HR", "SpO2", "HRV", "Systolic", "Diastolic", "Age", "BMI"]

_PIPELINE_PATH = os.path.join(os.path.dirname(__file__), "..", "ml", "cardio_risk_pipeline.pkl")
_pipeline = None


def _get_pipeline():
    global _pipeline
    if _pipeline is None:
        _pipeline = joblib.load(_PIPELINE_PATH)
    return _pipeline


def classify_risk_level(risk_pct: float) -> str:
    """Matches the thresholds stated in the paper: Low <30, Medium 30-60, High >60."""
    if risk_pct >= 60:
        return "HIGH"
    if risk_pct >= 30:
        return "MEDIUM"
    return "LOW"


def predict_risk(hr, spo2, hrv, systolic, diastolic, age, bmi) -> dict:
    """
    Raw feature values in -> {"risk": float 0-100, "risk_level": str}.
    Scaling happens INSIDE the pipeline (see ml/train_cardio_risk_model.py) --
    callers never scale anything themselves, which is exactly what fixes
    the original app.py bug of skipping the scaler.
    """
    pipeline = _get_pipeline()
    # Built as a DataFrame with matching column names (not a bare numpy
    # array) because the pipeline's StandardScaler was fit on a DataFrame
    # with these exact column names -- passing a raw array works but
    # triggers a sklearn warning about missing feature names, and more
    # importantly is fragile if FEATURE_ORDER and training order ever
    # drift apart silently. Naming them here makes any mismatch loud.
    feature_vector = pd.DataFrame([[hr, spo2, hrv, systolic, diastolic, age, bmi]], columns=FEATURE_ORDER)
    risk_prob = pipeline.predict_proba(feature_vector)[0][1] * 100
    risk_prob = round(float(risk_prob), 2)
    return {"risk": risk_prob, "risk_level": classify_risk_level(risk_prob)}
