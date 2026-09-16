"""
ml/train_cardio_risk_model.py
-------------------------------
Two real fixes vs your original script, plus the BMI addition:

FIX 1 (the audit's #1 finding): your old app.py called
    model.predict_proba(raw_features)
directly, with NO scaler applied, even though training used
StandardScaler. Whatever `scaler.pkl` was originally saved never shipped
with your repo, and even if it had, app.py never loaded it. That means
the live app's predictions were mathematically inconsistent with how the
model was trained.

THE FIX: instead of saving `model.pkl` and `scaler.pkl` as two separate
files that can drift apart or get separated, we bundle them into a single
scikit-learn `Pipeline([("scaler", ...), ("model", ...)])` and save THAT
one object. Calling `pipeline.predict_proba(raw_features)` now ALWAYS
scales first, then predicts -- there is no code path where scaling can be
accidentally skipped, because it's baked into the object itself.

FIX 2: BMI is added as a 7th feature, matching the updated dataset
generator.

Everything else -- algorithm choice (Logistic Regression), train/test
split, evaluation metrics -- is intentionally unchanged from your
original script.
"""
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

# --------------------------------------------------
# 1. Load dataset
# --------------------------------------------------
df = pd.read_csv("cardio_risk_dataset.csv")

# NOTE: BMI added to the feature list. Order here MUST match the order
# routes/predictions.py builds the feature vector in -- see that file's
# docstring for the single source of truth on feature order.
features = ["HR", "SpO2", "HRV", "Systolic", "Diastolic", "Age", "BMI"]
X = df[features]
y = df["Risk"]

# --------------------------------------------------
# 2. Train-test split (unchanged)
# --------------------------------------------------
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.25, random_state=42, stratify=y
)

# --------------------------------------------------
# 3 & 4. Scaling + Model, bundled into ONE Pipeline object
# --------------------------------------------------
pipeline = Pipeline([
    ("scaler", StandardScaler()),
    ("model", LogisticRegression(max_iter=1000, class_weight="balanced")),
])
pipeline.fit(X_train, y_train)

# --------------------------------------------------
# 5. Predictions & evaluation (unchanged logic)
# --------------------------------------------------
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

# --------------------------------------------------
# 6. Save ONE pipeline object -- scaler and model can never drift apart
# --------------------------------------------------
joblib.dump(pipeline, "cardio_risk_pipeline.pkl")
print("\nSaved combined scaler+model pipeline as cardio_risk_pipeline.pkl")
