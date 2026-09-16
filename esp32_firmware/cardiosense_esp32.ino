/*
  esp32_firmware/cardiosense_esp32.ino
  ------------------------------------
  NOTE: No ESP32/Arduino source file was included in your original
  upload, so this is a NEW reference sketch (not a modification of
  something you had). It shows the minimum needed to satisfy the
  device-authentication design in backend/utils/device_auth.py:
  every request carries X-Device-Id and X-Device-Secret headers,
  obtained once from POST /api/devices (see routes/devices.py) and
  then hardcoded into this firmware at flash time.

  Sensors: AD8232 (ECG) on an analog pin, MAX30100 (PPG/HR/SpO2) over I2C.
  This sketch intentionally sends RAW ecg/ppg + the MAX30100 library's
  own hr/spo2 estimate -- HRV and blood pressure are NOT computed here.
  They're computed backend-side (services/signal_processing.py) from the
  raw ecg/ppg stream, per your instruction to prefer backend processing.
*/
#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>
#include "MAX30100_PulseOximeter.h"

const char* WIFI_SSID = "YOUR_WIFI_SSID";
const char* WIFI_PASSWORD = "YOUR_WIFI_PASSWORD";
const char* BACKEND_URL = "http://YOUR_BACKEND_HOST:5000/api/readings";

// Obtained ONE TIME from POST /api/devices (see routes/devices.py).
// Treat DEVICE_SECRET like a password -- do not commit this file with
// a real secret filled in to a public repo.
const char* DEVICE_ID = "esp32-01";
const char* DEVICE_SECRET = "PASTE_THE_SECRET_SHOWN_ONCE_AT_REGISTRATION";

const int ECG_PIN = 34;
PulseOximeter pox;

void setup() {
  Serial.begin(115200);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  while (WiFi.status() != WL_CONNECTED) { delay(500); Serial.print("."); }
  Serial.println("\nWi-Fi connected.");

  if (!pox.begin()) {
    Serial.println("MAX30100 init failed");
  }
}

void loop() {
  pox.update();

  int ecgRaw = analogRead(ECG_PIN);          // 0-4095 on ESP32 ADC
  float ppgRaw = pox.getIR();                 // raw infrared reading, used as PPG signal
  float hr = pox.getHeartRate();
  float spo2 = pox.getSpO2();

  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    http.begin(BACKEND_URL);
    http.addHeader("Content-Type", "application/json");
    http.addHeader("X-Device-Id", DEVICE_ID);
    http.addHeader("X-Device-Secret", DEVICE_SECRET);

    StaticJsonDocument<256> doc;
    doc["ecg"] = ecgRaw;
    doc["ppg"] = ppgRaw;
    doc["hr"] = hr;
    doc["spo2"] = spo2;

    String payload;
    serializeJson(doc, payload);

    int statusCode = http.POST(payload);
    Serial.printf("POST /api/readings -> %d\n", statusCode);
    http.end();
  }

  delay(20); // ~50 samples/sec -- adjust to match your R-peak detection needs
}
