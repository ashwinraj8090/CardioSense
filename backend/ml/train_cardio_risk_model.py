
import pandas as pd
import joblib

from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    roc_auc_score,
)

# 1. Load dataset
df = pd.read_csv("cardio_risk_dataset.csv")

features = ["HR", "SpO2", "HRV", "Systolic", "Diastolic", "Age", "BMI"]
X = df[features]
y = df["Risk"]

# 2. Train-test split 
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.25, random_state=42, stratify=y
)

# 3 & 4. Scaling + Model, bundled into ONE Pipeline object
pipeline = Pipeline([
    ("scaler", StandardScaler()),
    ("model", LogisticRegression(max_iter=1000, class_weight="balanced")),
])
pipeline.fit(X_train, y_train)

# 5. Predictions & evaluation (unchanged logic)
y_pred = pipeline.predict(X_test)
y_prob = pipeline.predict_proba(X_test)[:, 1]

accuracy = accuracy_score(y_test, y_pred)
roc_auc = roc_auc_score(y_test, y_prob)

print(f"Accuracy: {accuracy:.4f}")
print(f"ROC-AUC: {roc_auc:.4f}")
print("\nClassification Report:")
print(classification_report(y_test, y_pred))
print("\nConfusion Matrix:")
print(confusion_matrix(y_test, y_pred))

print("\nFeature Importance (Logistic Regression Coefficients, on scaled inputs):")
for feature, coef in zip(features, pipeline.named_steps["model"].coef_[0]):
    print(f"{feature}: {coef:.4f}")

joblib.dump(pipeline, "cardio_risk_pipeline.pkl")
print("\nSaved combined scaler+model pipeline as cardio_risk_pipeline.pkl")
