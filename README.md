# 🫀 CardioSense
## Towards Intelligent and Personalized Cardiovascular Health Monitoring

CardioSense is an **ML and IoT-driven cardiovascular health monitoring system** that integrates physiological sensing, machine learning–based risk analysis, and real-time web visualization with AI assistance.

The system collects cardiac signals using wearable sensors, authenticates every device and user, processes and analyzes the data through a machine learning model, and presents personalized health insights via a secure, multi-user, database-backed dashboard and AI assistant.

CardioSense is designed as a research and academic prototype aimed at early health awareness, system experimentation, and intelligent decision support — **not clinical diagnosis**. Its dataset is synthetic and its model is not clinically validated (see Limitations below).

---

## 📌 Key Features

- Real-time acquisition of ECG, Heart Rate, and SpO₂ signals
- Wireless data transmission using ESP32 microcontroller, batched and device-authenticated
- Machine Learning–based cardiovascular risk prediction (Logistic Regression, 7 features including **BMI**)
- Secure user accounts — hashed passwords, JWT authentication, per-user data isolation
- Device registration with per-device secret credentials — no anonymous ESP32 can post data
- Persistent, relational database (not browser localStorage) — real history across sessions and devices
- Interactive web dashboard with live vitals and historical trend charts
- AI-assisted chatbot for explanations and health recommendations, powered server-side
- Rate limiting on sensitive endpoints (login, sensor ingestion)
- Modular, layered backend architecture (models / routes / services / utils)

---

## 🏗️ System Overview

### Hardware Layer (Data Acquisition)
- **MAX30100** – PPG signal, Heart Rate, and SpO₂ measurement
- **AD8232** – ECG signal acquisition
- **ESP32** – Sensor sampling, local batching, Wi-Fi communication, device-credential authentication

### Software Layer (Analysis & Interaction)
- **Flask Backend** – REST API, authentication/authorization, signal processing, ML inference
- **SQLite/PostgreSQL Database** – users, devices, monitoring sessions, readings, predictions (via SQLAlchemy)
- **Machine Learning Pipeline** – StandardScaler + Logistic Regression, bundled as one artifact
- **Web Dashboard** – live and historical visualization, session control, device management
- **Chatbot Module** – server-side Gemini integration, real health context, no exposed API key

---

## 🤖 Machine Learning Model

- **Algorithm**: Logistic Regression (`class_weight="balanced"`)
- **Input Features**:
  - Heart Rate (HR)
  - SpO₂
  - Heart Rate Variability (HRV) — RMSSD, computed server-side from raw ECG
  - Systolic Blood Pressure — estimated via Pulse Arrival Time (PAT)
  - Diastolic Blood Pressure
  - Age — derived from date of birth
  - **BMI** — derived from height (cm) and weight (kg) collected at signup
- **Output**: Probabilistic cardiovascular risk score (0–100%), categorized as Low (<30%), Medium (30–60%), or High (>60%)
- **Preprocessing**: scaler and model are trained and saved together as a single `scikit-learn Pipeline`, so inference can never accidentally skip scaling
- **Reported performance** (on a held-out 25% synthetic test split): **79.3% accuracy, 0.889 ROC-AUC**

The model is trained on a synthetic dataset with physiologically-grounded distributions and clinically-informed risk weighting (AHA/ACC hypertension staging, WHO BMI thresholds). This allows controlled, reproducible experimentation — it is **not** a substitute for clinically validated training data.

---

## 📊 Dashboard Capabilities

- Live ECG and PPG waveform visualization (updated once per second per monitoring batch)
- Continuous display of HR, SpO₂, HRV, Blood Pressure, and Risk
- Color-coded cardiovascular risk indicator
- Persistent, database-backed history of Heart Rate and Risk Score over time (not browser-local)
- AI-assisted health insights based on the user's actual stored vitals
- Integrated AI chatbot for explanations, guidance, and user interaction
- Session-based monitoring (Start/Stop), with automatic session handling per device
- Device management panel — register, view, and select ESP32 devices per account

---

## 📁 Project Structure

```
cardiosense/
├── backend/
│   ├── app.py                     # Flask app factory, registers all blueprints
│   ├── config.py                  # Reads all secrets from environment variables
│   ├── extensions.py              # Shared SQLAlchemy + rate-limiter instances
│   ├── models/                    # users, devices, sessions, readings, predictions
│   ├── routes/                    # auth, devices, sessions, readings, predictions, chat
│   ├── services/
│   │   ├── signal_processing.py   # HRV (RMSSD) + BP (PAT), batch-aware
│   │   └── prediction_service.py  # Loads the ML pipeline, runs inference
│   ├── utils/
│   │   ├── auth_utils.py          # Password hashing + JWT issue/verify
│   │   └── device_auth.py         # ESP32 device-credential verification
│   ├── ml/
│   │   ├── generate_dataset.py            # Synthetic data generator (incl. BMI)
│   │   ├── train_cardio_risk_model.py     # Trains + saves the scaler+model pipeline
│   │   └── cardio_risk_pipeline.pkl       # Trained artifact
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   └── cardiosense_dashboard.html # Dashboard UI — talks only to the backend API
└── esp32_firmware/
    └── cardiosense_esp32.ino      # Reference firmware: batched, authenticated sampling
```

---

## 🚀 How to Run the Project

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/YOUR_USERNAME/CardioSense.git
cd CardioSense/backend
```

### 2️⃣ Set Up a Virtual Environment & Install Dependencies
```bash
python -m venv venv
venv\Scripts\activate        # on Windows
source venv/bin/activate     # on macOS/Linux

pip install -r requirements.txt
```

### 3️⃣ Configure Environment Variables
```bash
copy .env.example .env       # Windows
cp .env.example .env         # macOS/Linux
```
Open `.env` and fill in `SECRET_KEY`, `JWT_SECRET` (random strings), and `GEMINI_API_KEY`.

### 4️⃣ Start the Flask Backend
```bash
python app.py
```
Runs at `http://127.0.0.1:5000` and creates the local database automatically on first run.

### 5️⃣ Launch the Dashboard
Open `frontend/cardiosense_dashboard.html` directly in a browser. Sign up, register a device, and click **Begin Real-Time Monitoring**.

---

## 🔑 API Key Configuration

This project uses an external AI service (Gemini) for chatbot-based health explanations. **The key lives only on the server, in `.env` — never in frontend code.**

### 📍 Where to add your API key

```
backend/.env
```
Fill in:
```
GEMINI_API_KEY=your_real_key_here
```
The frontend never sees or sends this key — it calls `POST /api/chat` on your own backend, which attaches the key server-side before calling Gemini.

---

## 🔐 Authentication & Device Security

- **User accounts**: passwords are hashed (never stored in plaintext), sessions are authenticated via JWT
- **Device identity**: each ESP32 is registered with a unique `device_id` and a hashed secret credential — an ESP32 must present both to submit sensor data, so anonymous or spoofed devices are rejected
- **Data isolation**: every reading, prediction, and history record is scoped to the authenticated user — one account can never see another's data
- **Rate limiting**: login attempts and sensor ingestion are both rate-limited to resist brute-force and flooding

---

## 📡 IoT Integration

The ESP32 samples ECG/PPG locally (~50 samples/sec), buffers roughly one second's worth of samples, and sends them as a single authenticated batch to the backend — rather than one HTTP request per raw sample. The backend runs R-peak detection, RMSSD (HRV), and PAT-based blood pressure estimation across each batch, then stores one summarized reading and, once enough data exists, one risk prediction.

The system supports:
- Simulated data mode for testing and development (see `README`/repo docs for a `curl` example)
- Live IoT mode for real-time, authenticated sensor integration (`esp32_firmware/cardiosense_esp32.ino`)

---

## ⚠️ Limitations

- The training dataset is **synthetic**, generated from a rule-based risk formula — not real diagnosed patient outcomes. High model accuracy reflects how well it learned that rule, not clinical validity.
- Blood pressure is an **estimate** derived from Pulse Arrival Time, not a calibrated, cuff-based measurement.
- This system is **not a medical diagnostic device** and should not be used to make real health decisions without professional medical consultation.

---

## 🔮 Future Enhancements

- Clinical validation with real-world, outcome-labeled patient data
- Real hardware validation of the ESP32 firmware against physical AD8232/MAX30100 sensors
- Automated test suite (unit, API, integration)
- Production deployment (PostgreSQL, gunicorn, HTTPS, hosted environment)
- WebSocket-based push updates for smoother live waveform visualization
- Advanced ML/DL models trained on larger, real-world datasets
- Mobile application support

---

## 📜 License
This project is licensed under the MIT License.
