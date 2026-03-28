// Lighting.h
// Direct LED strip control (no WLED dependency)

#include <FastLED.h>

#ifndef LED_PIN
#define LED_PIN 2
#endif

#ifndef NUM_LEDS
#define NUM_LEDS 120
#endif

#ifndef LED_BRIGHTNESS
#define LED_BRIGHTNESS 128
#endif

CRGB leds[NUM_LEDS];
int currentLightingPreset = 0;
uint8_t lightingAnimationStep = 0;

void setupLighting() {
  FastLED.addLeds<WS2812B, LED_PIN, GRB>(leds, NUM_LEDS);
  FastLED.setBrightness(LED_BRIGHTNESS);
  FastLED.clear();
  FastLED.show();

  Serial.println("Lighting Controller: initialized (direct LED control).");
}

void applyLightingPreset(int presetID) {
  currentLightingPreset = presetID;
  lightingAnimationStep = 0;

  switch (presetID) {
    case 1: // Morning - warm glow
      fill_solid(leds, NUM_LEDS, CRGB::Gold);
      break;
    case 2: // Day - bright white
      fill_solid(leds, NUM_LEDS, CRGB::White);
      break;
    case 3: // Sunset - orange gradient
      for (int i = 0; i < NUM_LEDS; i++) {
        leds[i] = CHSV(20, 200, map(i, 0, NUM_LEDS - 1, 200, 64));
      }
      break;
    case 4: // Night - dim blue
      fill_solid(leds, NUM_LEDS, CRGB::BlueViolet);
      break;
    case 5: // Party - animated rainbow
    case 6: // Party 2 - faster rainbow
      // Animation handled in runLightingCycle()
      break;
    case 9: // Storm - flicker lightning
      // Animation handled in runLightingCycle()
      break;
    default:
      fill_solid(leds, NUM_LEDS, CRGB::Black);
      break;
  }

  FastLED.show();
}

void runLightingCycle() {
  switch (currentLightingPreset) {
    case 5: // Party rainbow
      fill_rainbow(leds, NUM_LEDS, lightingAnimationStep, 7);
      lightingAnimationStep++;
      FastLED.show();
      break;
    case 6: // Fast party
      fill_rainbow(leds, NUM_LEDS, lightingAnimationStep, 12);
      lightingAnimationStep += 2;
      FastLED.show();
      break;
    case 9: // Storm flicker
      if (random8() < 60) {
        fill_solid(leds, NUM_LEDS, CRGB::White);
      } else {
        fill_solid(leds, NUM_LEDS, CRGB::Blue);
      }
      FastLED.show();
      break;
    default:
      // Static presets already applied via applyLightingPreset()
      break;
  }
}

void setAllLightsOff() {
  fill_solid(leds, NUM_LEDS, CRGB::Black);
  FastLED.show();
}
