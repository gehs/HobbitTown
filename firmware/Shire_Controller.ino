// Shire_Controller.ino

#include "AudioLogic.h"   // This "imports" your audio functions
#include "Atmosphere.h"   // This "imports" your fogger functions

void setup() {
  Serial.begin(115200);
  
  setupAudio();       // Function inside AudioLogic.h
  setupAtmosphere();  // Function inside Atmosphere.h
  
  Serial.println("The Shire is waking up...");
}

void loop() {
  runAudioCycle();      // Keeps the birds chirping
  runAtmosphereCycle(); // Checks if it's time for mist
}