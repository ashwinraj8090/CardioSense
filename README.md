# 🫀 CardioSense
## Towards Intelligent and Personalized Cardiovascular Health Monitoring

CardioSense is an **ML and IoT-driven cardiovascular health monitoring system** developed to demonstrate the integration of physiological sensing, machine learning–based risk analysis, and real-time web visualization. 

The system collects cardiac signals using wearable sensors, processes and analyzes the data through a machine learning model, and presents personalized health insights via an interactive dashboard and AI assistant. 

CardioSense is designed as a research and academic prototype aimed at early health awareness, system experimentation, and intelligent decision support rather than clinical diagnosis.

---

## 📌 Key Features

- Real-time acquisition of ECG, Heart Rate, and SpO₂ signals  
- Wireless data transmission using ESP32 microcontroller  
- Machine Learning–based cardiovascular risk prediction  
- Interactive web dashboard with live vitals and waveform visualization  
- AI-assisted chatbot for explanations and health recommendations  
- Modular and extensible system architecture  

---

## 🏗️ System Overview

### Hardware Layer (Data Acquisition)
- **MAX30100** – PPG signal, Heart Rate, and SpO₂ measurement  
- **AD8232** – ECG signal acquisition  
- **ESP32** – Sensor interfacing and Wi-Fi communication  

### Software Layer (Analysis & Interaction)
- **Flask Backend** – API handling, data processing, ML inference  
- **Machine Learning Model** – Logistic Regression–based risk prediction  
- **Web Dashboard** – Real-time visualization and monitoring  
- **Chatbot Module** – AI-based explanations and recommendations  

---

## 🤖 Machine Learning Model

- **Algorithm**: Logistic Regression  
- **Input Features**:
  - Heart Rate (HR)  
  - SpO₂  
  - Heart Rate Variability (HRV)  
  - Systolic Blood Pressure  
  - Diastolic Blood Pressure  
  - Age  
- **Output**: Probabilistic cardiovascular risk score categorized as Low, Medium, or High  

The model is trained using a synthetic dataset that reflects realistic physiological ranges and inter-feature relationships, allowing controlled experimentation and evaluation.

---

## 📊 Dashboard Capabilities

- Live ECG and PPG waveform visualization  
- Continuous display of HR, SpO₂, HRV, and Blood Pressure  
- Color-coded cardiovascular risk indicator
- User History of Heart Rate and SpO₂ 
- AI-assisted health insights based on short-term trends
- Integrated AI chatbot for explanations, guidance, and user interaction  
- Session-based user monitoring  

---

## 📁 Project Structure
```
CardioSense/
│
├── app.py # Flask backend server
├── cardiosense_dashboard.html # Frontend dashboard
├── cardio_risk_dataset.csv # Training dataset
├── cardio_risk_model.pkl # Trained ML model
├── train_cardio_risk_model.py # Model training script
├── requirements.txt # Python dependencies
├── static/
│ └── css/ # Stylesheets
├── package.json # Frontend dependencies
├── tailwind.config.js # Tailwind CSS configuration
└── README.md # Project documentation
```
---

## 🚀 How to Run the Project

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/ashwinraj8090/CardioSense.git
cd CardioSense
```

### 2️⃣ Install Python Dependencies
```
pip install -r requirements.txt
```

### 3️⃣ Start the Flask Backend
```
python app.py
```

### 4️⃣ Launch the Dashboard
```
Open cardiosense_dashboard.html in a browser (Live Server recommended)

Ensure the Flask server is running before starting monitoring
```

---

## 🔑 API Key Configuration

This project uses an external AI service for chatbot-based health explanations and recommendations.
API keys are not included in this repository for security reasons.

### 📍 Where to add your API key

Add your API key in the frontend JavaScript section inside:
```
cardiosense_dashboard.html
```

Look for a placeholder similar to:
```
const AI_API_KEY = "YOUR_API_KEY_HERE";
```

Replace "YOUR_API_KEY_HERE" with your own valid API key.

---

## 📡 IoT Integration

The ESP32 continuously sends sensor readings to the Flask backend using HTTP-based REST APIs.
The system supports:

Simulated data mode for testing and development

Live IoT mode for real-time sensor integration

---

## 🔮 Future Enhancements

- Clinical validation with real-world patient data

- Advanced ML/DL models for improved prediction accuracy

- Mobile application support

- Cloud-based deployment and scalability

- Secure authentication and encrypted data storage

---

## 👨‍💻 Author

Ashwin Raj

Computer Science Engineering
