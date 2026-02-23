// Lighting.h
#include <HTTPClient.h>

// Replace with the actual IP address WLED gets once you connect it to your WiFi
const char* wledIP = "192.168.1.50"; 

void setupLighting() {
  // WLED handles its own setup via its web interface.
  // We just need to make sure our Logic ESP32 can see it.
  Serial.println("Lighting Controller: Initialized.");
}

void applyWLEDPreset(int presetID) {
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    String url = "http://" + String(wledIP) + "/json/state";
    
    http.begin(url);
    http.addHeader("Content-Type", "application/json");

    // This is the JSON payload. "ps" stands for "Preset"
    String jsonPayload = "{\"ps\":" + String(presetID) + "}";
    
    int httpResponseCode = http.POST(jsonPayload);
    
    if (httpResponseCode > 0) {
      Serial.print("WLED Preset Applied: ");
      Serial.println(presetID);
    } else {
      Serial.print("Error sending Lighting Command: ");
      Serial.println(httpResponseCode);
    }
    http.end();
  }
}