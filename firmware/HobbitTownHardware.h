#pragma once

#include <Arduino.h>
#include <Wire.h>
#include <Adafruit_PWMServoDriver.h>
#include <DFRobotDFPlayerMini.h>
#include <WebServer.h>

// I2C pins for PCA9685
#ifndef HT_SDA_PIN
#define HT_SDA_PIN 21
#endif
#ifndef HT_SCL_PIN
#define HT_SCL_PIN 22
#endif

// PCA9685 addresses
#ifndef HT_PCA9685_ADDR1
#define HT_PCA9685_ADDR1 0x40
#endif
#ifndef HT_PCA9685_ADDR2
#define HT_PCA9685_ADDR2 0x41
#endif

// --- AUDIO GATE & SERIAL DEFINITIONS --- 
#define GATE_VOICES_PIN 18  // 74AHCT125 Pin 4
#define GATE_DEEP_PIN   19  // 74AHCT125 Pin 10
#define AUDIO_TX_PIN    17  
#define AUDIO_RX_PIN    16 

// Global hardware objects
extern int8_t htSDA;
extern int8_t htSCL;
extern Adafruit_PWMServoDriver pwm1;
extern Adafruit_PWMServoDriver pwm2;

extern DFRobotDFPlayerMini dfPlayerBase;
extern DFRobotDFPlayerMini dfPlayerSpots;

extern uint8_t base_vol;
extern uint8_t spot_vol;

// Function Prototypes
void setupHobbitTownHardware();
void hobbitSetDoor(int id, uint8_t angle);
void hobbitSetMister(int id, uint8_t value);
void hobbitSetSpeaker(int channel, uint8_t value);
void hobbitSetBlower(int id, uint8_t value);
void hobbitPlayAudio(int player, int track, bool loop);
void hobbitResetAll();

// Web Helpers
String processHobbitRequest(WebServer &server);
String buildHobbitPage(const String &msg);