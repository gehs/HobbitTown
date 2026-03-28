#include <Arduino.h>
#include <WiFi.h>          
#include <time.h>         
#include "AudioLogic.h"   
#include "Atmosphere.h"   
#include "Lighting.h"     
#include "WebLogic.h"    
#include "TimeSync.h"

// 1. DEFINITIONS (Move these to the top so the whole file sees them)
enum ShireState { MORNING, DAY, EVENING, NIGHT };
ShireState currentState = DAY;
bool partyModeActive = false;
int lastHour = -1; // To track when the hour actually changes

void setup() {
  Serial.begin(115200);
  
  // Initialize all your "Header" modules
  setupAudio();      
  setupHobbitTownHardware();
  setupAtmosphere(); 
  setupLighting();   
  setupWeb();
  
  Serial.println("The Shire is waking up...");
}

void loop() {
  // --- A. NETWORKING & EXTERNAL COMMANDS ---
  runWebSync();       // Check for /party web commands
  runLightingCycle(); // Animate lighting when needed

  // --- B. TIME MANAGEMENT ---
  int currentHour = getHour();
  if (currentHour != lastHour) { // Only run this check once per hour change
    updateStateByTime(currentHour);
    lastHour = currentHour;
  }

  // --- C. OVERRIDES (Like Party Mode) ---
  if (partyModeActive) {
    applyLightingPreset(5); 
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
      applyLightingPreset(1); playDaytime(); break;
    case DAY:
      applyLightingPreset(2); break; // Birds continue from morning
    case EVENING:
      applyLightingPreset(3); playSunsetSfx(); break;
    case NIGHT:
      applyLightingPreset(4); playNighttime(); break;
  }
}

