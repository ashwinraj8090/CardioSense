
#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>
#include "MAX30100_PulseOximeter.h"

const char* WIFI_SSID = "YOUR_WIFI_SSID";
const char* WIFI_PASSWORD = "YOUR_WIFI_PASSWORD";
const char* BACKEND_URL = "http://YOUR_BACKEND_HOST:5000/api/readings";
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

  int ecgRaw = analogRead(ECG_PIN);          
  float ppgRaw = pox.getIR();                 
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

  delay(20); 
}
