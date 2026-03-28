/*
 * SHIRE DIORAMA: Audio Logic Controller
 * Target: ESP32
 * Library: DFRobotDFPlayerMini
 */

#include "HobbitTownHardware.h"

// Track IDs expected by the main controller logic.
const int TRACK_DAYTIME = 1;
const int TRACK_SUNSET = 2;
const int TRACK_NIGHTTIME = 3;
const int TRACK_DRAGON_EVENT = 4;
const int TRACK_PARTY = 5;
const int TRACK_RAIN_STORM = 9;

void setupAudio() {
  Serial.println(F("Audio logic: ready."));
}

void runAudioCycle() {
  // Logic for switching tracks based on lighting presets or Time of Day goes here
}

void playDaytime() {
  dfPlayerBase.loop(TRACK_DAYTIME);
}

void playSunsetSfx() {
  dfPlayerBase.play(TRACK_SUNSET);
}

void playNighttime() {
  dfPlayerBase.loop(TRACK_NIGHTTIME);
}

void playDragonEvent() {
  dfPlayerBase.play(TRACK_DRAGON_EVENT);
}

void playPartyMusic() {
  dfPlayerBase.loop(TRACK_PARTY);
}