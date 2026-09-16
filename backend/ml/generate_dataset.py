
import numpy as np
import pandas as pd

np.random.seed(42)
N = 3000

hr = np.random.normal(75, 12, N)
spo2 = np.random.normal(98, 1.5, N)
hrv = np.random.normal(60, 18, N)
age = np.random.randint(18, 90, N)

height_cm = np.random.normal(168, 9, N)
height_cm = np.clip(height_cm, 145, 200)


weight_kg = 0.9 * (height_cm - 100) + np.random.normal(0, 12, N)
weight_kg = np.clip(weight_kg, 40, 150)

height_m = height_cm / 100.0
bmi = weight_kg / (height_m ** 2)
bmi = np.clip(bmi, 15, 50)


systolic = 110 + (0.3 * hr) + (0.4 * age) + np.random.normal(0, 6, N)
diastolic = (0.65 * systolic) + np.random.normal(0, 4, N)

hr = np.clip(hr, 40, 190)
spo2 = np.clip(spo2, 80, 100)
hrv = np.clip(hrv, 10, 150)
systolic = np.clip(systolic, 85, 220)
diastolic = np.clip(diastolic, 50, 120)

risk_score = (
    (hr > 100).astype(int) * 0.15 +
    (spo2 < 95).astype(int) * 0.25 +
    (hrv < 40).astype(int) * 0.10 +
    (systolic >= 140).astype(int) * 0.20 +
    (systolic >= 130).astype(int) * 0.10 +
    (diastolic >= 90).astype(int) * 0.10 +
    (age > 60).astype(int) * 0.20 +
    (bmi >= 30).astype(int) * 0.15 +         
    (bmi >= 25).astype(int) * 0.07            
)

risk_score += np.random.normal(0, 0.03, N)
risk = (risk_score >= 0.40).astype(int)

df = pd.DataFrame({
    "HR": hr,
    "SpO2": spo2,
    "HRV": hrv,
    "Systolic": systolic,
    "Diastolic": diastolic,
    "Age": age,
    "BMI": bmi,
    "Risk": risk
})

df.to_csv("cardio_risk_dataset.csv", index=False)
print(f"Synthetic dataset with BMI saved. Positive rate: {risk.mean():.3f}")
