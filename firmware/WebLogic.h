#include <WiFi.h>
#include <WebServer.h>
#include <ESPmDNS.h>

#include "HobbitTownHardware.h"

extern void applyLightingPreset(int presetID);

// Optional local override file for secrets. Keep this untracked.
#if __has_include("NetworkSecrets.h")
#include "NetworkSecrets.h"
#endif

#ifndef WIFI_SSID
#define WIFI_SSID "YOUR_WIFI_SSID"
#endif

#ifndef WIFI_PASSWORD
#define WIFI_PASSWORD "YOUR_WIFI_PASSWORD"
#endif

#ifndef DEVICE_HOSTNAME
#define DEVICE_HOSTNAME "hobbitt2"
#endif

extern bool partyModeActive;

WebServer server(80);
bool webServerStarted = false;

void connectWiFi() {
  WiFi.mode(WIFI_STA);

  if (WiFi.status() == WL_CONNECTED) {
    return;
  }

  Serial.print("Connecting to WiFi SSID: ");
  Serial.println(WIFI_SSID);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

  unsigned long connectStart = millis();
  while (WiFi.status() != WL_CONNECTED && (millis() - connectStart) < 20000) {
    delay(500);
    Serial.print(".");
  }
  Serial.println();

  if (WiFi.status() == WL_CONNECTED) {
    Serial.print("WiFi connected. IP: ");
    Serial.println(WiFi.localIP());
  } else {
    Serial.println("WiFi connect timed out. Web features are offline.");
  }
}

void startMdns() {
  if (WiFi.status() != WL_CONNECTED) {
    return;
  }

  if (!MDNS.begin(DEVICE_HOSTNAME)) {
    Serial.println("mDNS failed to start.");
    return;
  }

  MDNS.addService("http", "tcp", 80);
  Serial.print("mDNS ready at http://");
  Serial.print(DEVICE_HOSTNAME);
  Serial.println(".local");
}

void handleParty() {
  partyModeActive = true;
  server.send(200, "text/plain", "The Party has started in the Shire!");
  Serial.println("WiFi command: Party mode triggered");
}

void handleLightingPreset() {
  if (!server.hasArg("preset")) {
    server.send(400, "text/plain", "Missing 'preset' query parameter (e.g. /lighting?preset=3)");
    return;
  }

  int preset = server.arg("preset").toInt();
  applyLightingPreset(preset);
  server.send(200, "text/plain", "Lighting preset set to " + String(preset));
  Serial.printf("WiFi command: lighting preset %d\n", preset);
}

void handleRoot() {
  server.send(200, "text/plain", "HobbitTown controller is online.");
}

void setupWeb() {
  connectWiFi();
  startMdns();

  server.on("/", handleRoot);
  server.on("/party", handleParty);
  server.on("/lighting", handleLightingPreset);

  // Hobbit Town hardware test UI
  server.on("/hobbit", []() {
    String msg = processHobbitRequest(server);
    server.send(200, "text/html", buildHobbitPage(msg));
  });

  server.begin();
  webServerStarted = true;
  Serial.println("Web server started. Waiting for LAN commands...");
}

void runWebSync() {
  if (!webServerStarted) {
    return;
  }

  if (WiFi.status() != WL_CONNECTED) {
    connectWiFi();
    if (WiFi.status() == WL_CONNECTED) {
      startMdns();
    }
  }

  server.handleClient();
}
