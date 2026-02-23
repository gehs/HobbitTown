/*
 * SHIRE DIORAMA: Audio Logic Controller
 * Target: ESP32
 * Library: DFRobotDFPlayerMini
 */

#include "Arduino.h"
#include "DFRobotDFPlayerMini.h"

// ESP32 Hardware Serial pins for DFPlayer
// Connect DFPlayer TX to ESP32 RX2 (GPIO 16)
// Connect DFPlayer RX to ESP32 TX2 (GPIO 17) - Use a 1k Ohm resistor!
HardwareSerial mySoftwareSerial(2);
DFRobotDFPlayerMini myDFPlayer;

void setupAudio() {
  mySoftwareSerial.begin(9600, SERIAL_8N1, 16, 17);
  Serial.begin(115200);

  Serial.println(F("Initializing DFPlayer..."));

  if (!myDFPlayer.begin(mySoftwareSerial)) { 
    Serial.println(F("Unable to begin: Check connection/SD card."));
    while(true);
  }
  
  Serial.println(F("DFPlayer Mini online."));
  
  // Set initial volume (0-30)
  myDFPlayer.volume(15); 
  
  // Start the Day Ambiance on Boot
  myDFPlayer.loop(1); 
}

void runAudioCycle() {
  // Logic for switching tracks based on WLED or Time of Day goes here
}