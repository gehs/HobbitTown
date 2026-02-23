#include <WebServer.h>

// Tell this file that 'partyModeActive' is defined in the main file
extern bool partyModeActive; 

WebServer server(80); 

void handleParty() {
  partyModeActive = true; 
  server.send(200, "text/plain", "The Party has started in the Shire!");
  Serial.println("WiFi Command: Party Mode Triggered!");
}

void setupWeb() {
  server.on("/party", handleParty); 
  server.begin();
  Serial.println("Web Server started. Waiting for WiFi commands...");
}

void runWebSync() {
  server.handleClient(); 
}