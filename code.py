"""LED Strand Connectivity Isolation Test for ESP32-S3 CircuitPython.

Sequentially tests Sky, Ground, and Stream strands individually for 5 seconds 
each to isolate wiring and physical data line connections.
"""

import time
import board
import neopixel
import config

# ============================================================================
# CONFIGURATION SETUP
# ============================================================================

# Read definitions directly from config.py
SKY_PIN = board.GPIO4 #config.NEOPIXEL_SKY_PIN
GROUND_PIN = board.GPIO5 #config.NEOPIXEL_GROUND_PIN
STREAM_PIN = board.GPIO6 #config.NEOPIXEL_STREAM_PIN

# Calculated or direct pixel counts
TOTAL_SKY_PIXELS = 5 #19 + 91 + 19  # 129 pixels total for the mixed sky arc
GROUND_PIXEL_COUNT = 5 #config.NUM_PIXELS_GROUND
STREAM_PIXEL_COUNT = 5 #config.NUM_PIXELS_STREAM
BRIGHTNESS =  .5 #config.BRIGHTNESS

print("=" * 50)
print("STARTING ISOLATED STRAND CONNECTIVITY TEST")
print("=" * 50)
print(f"Strand 1 (SKY)    -> Pin: {SKY_PIN} | Pixels: {TOTAL_SKY_PIXELS}")
print(f"Strand 2 (GROUND) -> Pin: {GROUND_PIN} | Pixels: {GROUND_PIXEL_COUNT}")
print(f"Strand 3 (STREAM) -> Pin: {STREAM_PIN} | Pixels: {STREAM_PIXEL_COUNT}")
print("=" * 50)

# Check for pin collisions before starting
if SKY_PIN == STREAM_PIN or SKY_PIN == GROUND_PIN or GROUND_PIN == STREAM_PIN:
    print("\n[WARNING] PIN ASSIGNMENT OVERLAP DETECTED IN config.py!")
    print("Ensure your pins are uniquely assigned to prevent hardware hijacking.\n")

# ============================================================================
# INITIALIZE STRIPS AS INDEPENDENT NEOPIXEL OBJECTS
# ============================================================================
# For a pure connectivity check, treating the Sky strip as standard GRB 
# will still light up every pixel (even the RGBW ones will respond to the data).

print("Initializing hardware channels...")

sky_strip = neopixel.NeoPixel(
    SKY_PIN, TOTAL_SKY_PIXELS, brightness=BRIGHTNESS, auto_write=False, pixel_order=neopixel.GRB
)

ground_strip = neopixel.NeoPixel(
    GROUND_PIN, GROUND_PIXEL_COUNT, brightness=BRIGHTNESS, auto_write=False, pixel_order=neopixel.GRB
)

stream_strip = neopixel.NeoPixel(
    STREAM_PIN, STREAM_PIXEL_COUNT, brightness=BRIGHTNESS, auto_write=False, pixel_order=neopixel.GRB
)

# Ensure everything starts dark
sky_strip.fill((0, 0, 0))
ground_strip.fill((0, 0, 0))
stream_strip.fill((0, 0, 0))
sky_strip.show()
ground_strip.show()
stream_strip.show()

# ============================================================================
# RUN SEQUENTIAL 30-SECOND TEST (2 CYCLES x 15 SECONDS)
# ============================================================================

TEST_COLOR = (255, 255, 255) # Solid bright white for maximum visibility
HOLD_TIME = 5.0              # Seconds per strand

try:
    for cycle in range(1, 3):
        print(f"\n--- Starting Test Cycle {cycle} of 2 ---")
        
        # 1. TEST SKY STRAND ONLY
        print("  [ON]  Testing SKY Strand... (Ground & Stream should be DARK)")
        sky_strip.fill(TEST_COLOR)
        ground_strip.fill((0, 0, 0))
        stream_strip.fill((0, 0, 0))
        sky_strip.show()
        ground_strip.show()
        stream_strip.show()
        time.sleep(HOLD_TIME)
        
        # 2. TEST GROUND STRAND ONLY
        print("  [ON]  Testing GROUND Strand... (Sky & Stream should be DARK)")
        sky_strip.fill((0, 0, 0))
        ground_strip.fill(TEST_COLOR)
        stream_strip.fill((0, 0, 0))
        sky_strip.show()
        ground_strip.show()
        stream_strip.show()
        time.sleep(HOLD_TIME)
        
        # 3. TEST STREAM STRAND ONLY
        print("  [ON]  Testing STREAM Strand... (Sky & Ground should be DARK)")
        sky_strip.fill((0, 0, 0))
        ground_strip.fill((0, 0, 0))
        stream_strip.fill(TEST_COLOR)
        sky_strip.show()
        ground_strip.show()
        stream_strip.show()
        time.sleep(HOLD_TIME)

    # Final Cleanup
    print("\n30-second execution loop complete. Turning all strands off.")
    sky_strip.fill((0, 0, 0))
    ground_strip.fill((0, 0, 0))
    stream_strip.fill((0, 0, 0))
    sky_strip.show()
    ground_strip.show()
    stream_strip.show()

except KeyboardInterrupt:
    print("\nTest aborted early by user. Clearing all channels.")
    sky_strip.fill((0, 0, 0))
    ground_strip.fill((0, 0, 0))
    stream_strip.fill((0, 0, 0))
    sky_strip.show()
    ground_strip.show()
    stream_strip.show()

print("Test script finished.")