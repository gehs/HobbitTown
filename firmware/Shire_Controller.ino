#include <Arduino.h>
#include <WiFi.h>          
#include <time.h>         
#include "AudioLogic.h"   
#include "Atmosphere.h"   
#include "Lighting.h"     
#include "WebLogic.h"    
#include "NotificationLogic.h" // The WLED Listener

// 1. DEFINITIONS (Move these to the top so the whole file sees them)
enum ShireState { MORNING, DAY, EVENING, NIGHT };
ShireState currentState = DAY;
bool partyModeActive = false;
int lastHour = -1; // To track when the hour actually changes

void setup() {
  Serial.begin(115200);
  
  // Initialize all your "Header" modules
  setupAudio();       
  setupAtmosphere();  
  setupLighting();    
  setupWeb();
  setupWLEDListener();
  
  Serial.println("The Shire is waking up...");
}

void loop() {
  // --- A. NETWORKING & EXTERNAL COMMANDS ---
  runWebSync();       // Check for /party web commands
  runWLEDListener();  // Check for WLED UDP notifications

  // --- B. TIME MANAGEMENT ---
  int currentHour = getHour();
  if (currentHour != lastHour) { // Only run this check once per hour change
    updateStateByTime(currentHour);
    lastHour = currentHour;
  }

  // --- C. OVERRIDES (Like Party Mode) ---
  if (partyModeActive) {
    applyWLEDPreset(5); 
    playPartyMusic();
    partyModeActive = false; // Reset flag
  }

  // --- D. BACKGROUND TASKS (Non-blocking) ---
  runAudioCycle();      
  runAtmosphereCycle(); 
}

// 2. HELPER FUNCTIONS

void updateStateByTime(int hour) {
  if (hour >= 6 && hour < 9) currentState = MORNING;
  else if (hour >= 9 && hour < 17) currentState = DAY;
  else if (hour >= 17 && hour < 20) currentState = EVENING;
  else currentState = NIGHT;

  // Trigger the transition
  applyShireAtmosphere(currentState);
}

void applyShireAtmosphere(ShireState state) {
  switch (state) {
    case MORNING:
      applyWLEDPreset(1); playDaytime(); break;
    case DAY:
      applyWLEDPreset(2); break; // Birds continue from morning
    case EVENING:
      applyWLEDPreset(3); playSunsetSfx(); break;
    case NIGHT:
      applyWLEDPreset(4); playNighttime(); break;
  }
}

// This handles incoming "Mood" changes from WLED App
void handleStateChange(int presetID) {
  switch (presetID) {
    case 1: playDaytime(); break;
    case 9: // Stormy
      myDFPlayer.loop(TRACK_RAIN_STORM);
      digitalWrite(RELAY_PIN, LOW); 
      break;
    case 5: playDragonEvent(); break;
    case 6: playPartyMusic(); break;
  }
}