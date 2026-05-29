"""LED Diagnostic Test for ESP32-S3 CircuitPython.

Diagnoses color orders and validates all three independent lighting strands
(Sky, Ground, Stream) using assignments directly from config.py.
"""

import time
import board
import digitalio
import neopixel
from neopixel_write import neopixel_write
import config

# ============================================================================
# CONFIGURATION EXTRACTION
# ============================================================================

# 1. Sky Arc Setup (Mixed WS2812B and SK6812 RGBW)
DAWN_PIXELS = 19      # WS2812B (GRB)
NOON_PIXELS = 91      # SK6812 RGBW (32-bit)
DUSK_PIXELS = 19      # WS2812B (GRB)
TOTAL_SKY_PIXELS = DAWN_PIXELS + NOON_PIXELS + DUSK_PIXELS # 129 Total

# 2. Ground and Stream Setup
GROUND_PIXEL_COUNT = config.NUM_PIXELS_GROUND  # 153 from config
STREAM_PIXEL_COUNT = config.NUM_PIXELS_STREAM  # 85 from config
BRIGHTNESS = config.BRIGHTNESS

print("=" * 50)
print("LOADING HOBBITTOWN LED DIAGNOSTIC TOOL")
print("=" * 50)
print(f"Sky Strip    -> Pin: {config.NEOPIXEL_SKY_PIN} | Expected Pixels: {TOTAL_SKY_PIXELS}")
print(f"Ground Strip -> Pin: {config.NEOPIXEL_GROUND_PIN} | Pixels: {GROUND_PIXEL_COUNT}")
print(f"Stream Strip -> Pin: {config.NEOPIXEL_STREAM_PIN} | Pixels: {STREAM_PIXEL_COUNT}")
print("=" * 50)

# Check for pin collisions before proceeding
if config.NEOPIXEL_SKY_PIN == config.NEOPIXEL_STREAM_PIN:
    print("\n[WARNING] PIN COLLISION DETECTED!")
    print("Both SKY and STREAM are mapped to the same GPIO pin in config.py.")
    print("Please fix config.py before running. Defaulting to safe separation for test.\n")

# ============================================================================
# SPECIAL CONTROLLER FOR MIXED SKY STRIP
# ============================================================================

class SkyStripTester:
    """Handles raw byte generation for mixed 24-bit (GRB) and 32-bit (RGBW) Sky strip"""
    def __init__(self, pin, total_pixels):
        self.pin = digitalio.DigitalInOut(pin)
        self.pin.direction = digitalio.Direction.OUTPUT
        self.total_pixels = total_pixels
        self.pixels = [(0, 0, 0, 0)] * total_pixels

    def set_pixel_order(self, index, color, order):
        """Maps an RGB tuple to a specific color order for testing"""
        if not isinstance(color, tuple) or len(color) < 3:
            self.pixels[index] = (0, 0, 0, 0)
            return

        r, g, b = color
        if order == "RGB":   self.pixels[index] = (r, g, b, 0)
        elif order == "GRB": self.pixels[index] = (g, r, b, 0)
        elif order == "BRG": self.pixels[index] = (b, r, g, 0)
        elif order == "GBR": self.pixels[index] = (g, b, r, 0)
        elif order == "BGR": self.pixels[index] = (b, g, r, 0)
        elif order == "RBG": self.pixels[index] = (r, b, g, 0)

    def set_pixel_grb(self, index, color):
        """Standard GRB layout for WS2812B portions"""
        r, g, b = color[:3]
        self.pixels[index] = (g, r, b, 0)

    def clear(self):
        self.pixels = [(0, 0, 0, 0)] * self.total_pixels

    def show(self):
        buffer = bytearray()
        for index, (c1, c2, c3, w) in enumerate(self.pixels):
            if index < DAWN_PIXELS or index >= (DAWN_PIXELS + NOON_PIXELS):
                # Dawn/Dusk Sections: Strict 24-bit GRB standard
                buffer.extend((c1, c2, c3))
            else:
                # Noon Section: SK6812 32-bit (Test Order + White byte)
                buffer.extend((c1, c2, c3, w))
        neopixel_write(self.pin, buffer)


# ============================================================================
# INITIALIZE STRIPS
# ============================================================================

# 1. Initialize Sky Loop
sky_strip = SkyStripTester(config.NEOPIXEL_SKY_PIN, TOTAL_SKY_PIXELS)

# 2. Initialize Ground Loop (Standard NeoPixel Object)
ground_strip = neopixel.NeoPixel(
    config.NEOPIXEL_GROUND_PIN,
    GROUND_PIXEL_COUNT,
    brightness=BRIGHTNESS,
    auto_write=False,
    pixel_order=neopixel.GRB
)

# 3. Initialize Stream Loop (Standard NeoPixel Object)
stream_strip = neopixel.NeoPixel(
    config.NEOPIXEL_STREAM_PIN,
    STREAM_PIXEL_COUNT,
    brightness=BRIGHTNESS,
    auto_write=False,
    pixel_order=neopixel.GRB
)

# ============================================================================
# DIAGNOSTIC TESTS
# ============================================================================

def test_ground_and_stream():
    """Cycles solid colors through Ground and Stream layers to verify wiring"""
    print("\n---> Testing Ground and Stream Strands (Standard GRB Verification)")
    colors = [
        ("RED", (255, 0, 0)),
        ("GREEN", (0, 255, 0)),
        ("BLUE", (0, 0, 255)),
    ]
    
    for name, rgb in colors:
        print(f"  Illuminating Ground & Stream with: {name}")
        ground_strip.fill(rgb)
        stream_strip.fill(rgb)
        ground_strip.show()
        stream_strip.show()
        time.sleep(1.5)
        
    print("  Clearing Ground & Stream.")
    ground_strip.fill((0, 0, 0))
    stream_strip.fill((0, 0, 0))
    ground_strip.show()
    stream_strip.show()


def test_sky_color_orders():
    """Cycles color permutations across the mixed Sky strand"""
    print("\n---> Testing Sky Strip Mappings (Noon SK6812 RGBW Identification)")
    print(f"  Dawn (WS2812B GRB): Pixels 0-{DAWN_PIXELS-1}")
    print(f"  Noon (SK6812 MUX): Pixels {DAWN_PIXELS}-{DAWN_PIXELS+NOON_PIXELS-1}")
    print(f"  Dusk (WS2812B GRB): Pixels {DAWN_PIXELS+NOON_PIXELS}-{TOTAL_SKY_PIXELS-1}")
    
    test_colors = [
        ("RED", (255, 0, 0)),
        ("GREEN", (0, 255, 0)),
        ("BLUE", (0, 0, 255))
    ]
    orders = ["RGB", "GRB", "BRG", "GBR", "BGR", "RBG"]

    for color_name, rgb in test_colors:
        print(f"\nEvaluating visual output for Pure {color_name}:")
        
        for order in orders:
            sky_strip.clear()
            
            # Match the outer wings to their target color profile
            for i in range(DAWN_PIXELS):
                sky_strip.set_pixel_grb(i, rgb)
            for i in range(DAWN_PIXELS + NOON_PIXELS, TOTAL_SKY_PIXELS):
                sky_strip.set_pixel_grb(i, rgb)
                
            # Cycle through mapping modes for the middle segment
            for i in range(DAWN_PIXELS, DAWN_PIXELS + NOON_PIXELS):
                sky_strip.set_pixel_order(i, rgb, order)
                
            sky_strip.show()
            print(f"  Testing Format Mode -> [ {order} ] ... watching Noon segment.")
            time.sleep(2.5)

    sky_strip.clear()
    sky_strip.show()


# ============================================================================
# RUN DIAGNOSTICS
# ============================================================================

try:
    print("\nStep 1: Running basic Ground and Stream loop verification...")
    test_ground_and_stream()
    
    print("\nStep 2: Starting dynamic Sky color order diagnostic...")
    test_sky_color_orders()
    
    print("\nDiagnostics complete! Please update your permanent code with the format mapping")
    print("where the Noon segment visually matched the outer Dawn/Dusk wings.")

except KeyboardInterrupt:
    print("\nTesting interrupted by user. Clearing arrays.")
    ground_strip.fill((0, 0, 0))
    stream_strip.fill((0, 0, 0))
    ground_strip.show()
    stream_strip.show()
    sky_strip.clear()
    sky_strip.show()