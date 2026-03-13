#pragma once

#include <Arduino.h>
#include <Wire.h>
#include <Adafruit_PWMServoDriver.h>
#include <DFRobotDFPlayerMini.h>
#include <WebServer.h>

// I2C pins for PCA9685 (default ESP32 pins)
#ifndef HT_SDA_PIN
#define HT_SDA_PIN 21
#endif
#ifndef HT_SCL_PIN
#define HT_SCL_PIN 22
#endif

// Servo/PWM driver addresses
#ifndef HT_PCA9685_ADDR1
#define HT_PCA9685_ADDR1 0x40
#endif
#ifndef HT_PCA9685_ADDR2
#define HT_PCA9685_ADDR2 0x41
#endif

// Global hardware objects (defined in HobbitTownHardware.cpp)
extern int8_t htSDA;
extern int8_t htSCL;
extern Adafruit_PWMServoDriver pwm1;
extern Adafruit_PWMServoDriver pwm2;

extern DFRobotDFPlayerMini dfPlayerBase;
extern DFRobotDFPlayerMini dfPlayerSpots;

// User-configurable volumes
extern uint8_t base_vol;
extern uint8_t spot_vol;

// Initialization
void setupHobbitTownHardware();

// Control helpers for the web UI & tests
void hobbitSetDoor(int id, uint8_t angle);
void hobbitSetMister(int id, uint8_t value);
void hobbitSetSpeaker(int channel, uint8_t value);
void hobbitSetBlower(int id, uint8_t value);
void hobbitPlayAudio(int player, int track, bool loop);
void hobbitResetAll();

// Helper for the /hobbit web endpoint
String processHobbitRequest(WebServer &server);
String buildHobbitPage(const String &msg);
