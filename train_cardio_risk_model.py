import pandas as pd
import joblib
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    roc_auc_score
)

# 1. Load the updated dataset containing 6 features
df = pd.read_csv("cardio_risk_dataset.csv")

# 2. Update feature selection to include Systolic, Diastolic, and Age
# IMPORTANT: The order here MUST match the order in your app.py
X = df[["HR", "SpO2", "HRV", "Systolic", "Diastolic", "Age"]]
y = df["Risk"]

# Split data
X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,
    stratify=y,
    random_state=42
)

# 3. Train Logistic Regression with the expanded feature set
model = LogisticRegression(
    solver="liblinear",
    class_weight="balanced"
)

model.fit(X_train, y_train)

# Predictions
y_pred = model.predict(X_test)
y_prob = model.predict_proba(X_test)[:, 1]

# Metrics
print("\n===== UPDATED MODEL PERFORMANCE (6 FEATURES) =====\n")
print(f"Accuracy      : {accuracy_score(y_test, y_pred):.4f}")
print(f"ROC-AUC Score : {roc_auc_score(y_test, y_prob):.4f}\n")

print("Confusion Matrix:")
print(confusion_matrix(y_test, y_pred))

print("\nClassification Report:")
print(classification_report(y_test, y_pred))

# 4. Feature importance check
# This will show you which features (like BP or Age) are impacting risk most
print("\nFeature Importance:")
for feature, coef in zip(X.columns, model.coef_[0]):
    print(f"{feature}: {coef:.4f}")

# 5. Save the 6-feature model
joblib.dump(model, "cardio_risk_model.pkl")
print("\nModel saved as cardio_risk_model.pkl")