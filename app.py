from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
import numpy as np

app = Flask(__name__)
# Enable CORS to allow your frontend dashboard to fetch data from this server
CORS(app)

# --- 1. Load the 6-Feature ML Model ---
# This model expects: [HR, SpO2, HRV, Systolic, Diastolic, Age]
try:
    model = joblib.load("cardio_risk_model.pkl")
    print("AI Model loaded successfully.")
except Exception as e:
    print(f"Error loading model: {e}")

# --- 2. Global Buffer for Real-Time IoT Data ---
# Stores the most recent packet sent by the ESP32
latest_vitals = {
    "hr": 0,
    "spo2": 0,
    "ecg": 0,   # Raw signal from AD8232
    "ppg": 0,   # Raw signal from MAX30100
    "status": "offline"
}

# --- 3. IoT Receiver Route ---
# The ESP32 POSTs raw sensor data here
@app.route("/iot-update", methods=["POST"])
def iot_update():
    global latest_vitals
    try:
        data = request.get_json()
        latest_vitals = {
            "hr": round(float(data.get("hr", 0)), 2),
            "spo2": round(float(data.get("spo2", 0)), 2),
            "ecg": int(data.get("ecg", 0)),
            "ppg": int(data.get("ppg", 0)),
            "status": "online"
        }
        return jsonify({"status": "received"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# --- 4. Frontend Data Route ---
# The dashboard polls this to get raw values for HRV/BP calculations
@app.route("/get-vitals", methods=["GET"])
def get_vitals():
    return jsonify(latest_vitals)

# --- 5. AI Prediction Route ---
# Processes all 6 features for the final risk assessment
@app.route("/predict", methods=["POST"])
def predict_risk():
    try:
        data = request.get_json()
        
        # Array must be in order: [HR, SpO2, HRV, Systolic, Diastolic, Age]
        features = np.array([[
            data["hr"], 
            data["spo2"], 
            data["hrv"], 
            data["systolic"], 
            data["diastolic"], 
            data["age"]
        ]])

        # Calculate high-risk probability percentage
        risk_prob = model.predict_proba(features)[0][1] * 100

        return jsonify({
            "risk": round(float(risk_prob), 2),
            "status": "success"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    # host="0.0.0.0" is required for the ESP32 to find the server on your WiFi
    app.run(host="0.0.0.0", port=5000, debug=True)