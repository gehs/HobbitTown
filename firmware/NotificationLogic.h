#include <WiFiUdp.h>

WiFiUDP udp;
const unsigned int wledPort = 21324; // Standard WLED notification port
byte packetBuffer[64]; 

void setupWLEDListener() {
  udp.begin(wledPort);
  Serial.println("Listening for WLED Presets on the network...");
}

void runWLEDListener() {
  int packetSize = udp.parsePacket();
  if (packetSize) {
    udp.read(packetBuffer, packetSize);

    // WLED Notification packets: Byte 1 is usually the Preset ID
    // Note: This logic depends on WLED 'Sync' settings being on.
    int receivedPreset = packetBuffer[1]; 
    
    Serial.print("WLED moved to Preset: ");
    Serial.println(receivedPreset);

    // Trigger Audio based on the Lighting Preset
    handleStateChange(receivedPreset);
  }
}