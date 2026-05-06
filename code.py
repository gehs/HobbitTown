"""PCA9685 door servo bench test for Hobbit Town.

This script exercises PCA9685 PWM channels 0-3 and prints I2C diagnostics.
Use it after wiring the PCA9685 board with VCC, GND, SDA, SCL, OE low, and V+ for servo power.
"""

import time
import config


# Sky arc strip sections
DAWN_PIXELS = 19      # WS2812B (GRB)
NOON_PIXELS = 91      # SK6812 RGBW (32-bit)
DUSK_PIXELS = 19      # WS2812B (GRB)
TOTAL_SKY_PIXELS = DAWN_PIXELS + NOON_PIXELS + DUSK_PIXELS

# Ground strip test pixels
GROUND_PIXEL_COUNT = 70
BRIGHTNESS = 0.25

# Explicit pin mapping for this diagnostic
SKY_PIN = config.NEOPIXEL_SKY_PIN        # GPIO4
GROUND_PIN = config.NEOPIXEL_GROUND_PIN  # GPIO2


class ColorOrderTester:
    """Tests different color orders to find the correct mapping for SK6812 LEDs"""

    def __init__(self, pin, total_pixels, brightness=0.25):
        self.pin = digitalio.DigitalInOut(pin)
        self.pin.direction = digitalio.Direction.OUTPUT
        self.total_pixels = total_pixels
        self.brightness = brightness
        self.pixels = [(0, 0, 0, 0)] * total_pixels

    def set_pixel_order(self, index, color, order):
        """Set pixel with specified color order for the noon RGBW section"""
        if not isinstance(color, tuple) or len(color) < 3:
            self.pixels[index] = (0, 0, 0, 0)
            return

        r, g, b = color
        if order == "RGB":
            self.pixels[index] = (r, g, b, 0)
        elif order == "GRB":
            self.pixels[index] = (g, r, b, 0)
        elif order == "BRG":
            self.pixels[index] = (b, r, g, 0)
        elif order == "GBR":
            self.pixels[index] = (g, b, r, 0)
        elif order == "BGR":
            self.pixels[index] = (b, g, r, 0)
        elif order == "RBG":
            self.pixels[index] = (r, b, g, 0)

    def set_pixel_grb(self, index, color):
        """Standard GRB for WS2812B"""
        if not isinstance(color, tuple) or len(color) < 3:
            self.pixels[index] = (0, 0, 0, 0)
            return

        r, g, b = color
        self.pixels[index] = (g, r, b, 0)

    def set_pixel_rgbw(self, index, color):
        """Set pixel in noon section as RGBW"""
        if not isinstance(color, tuple) or len(color) < 3:
            self.pixels[index] = (0, 0, 0, 0)
            return

        r, g, b = color
        self.pixels[index] = (r, g, b, 0)

    def _build_bytearray(self):
        buffer = bytearray()
        for index, (r, g, b, w) in enumerate(self.pixels):
            if index < DAWN_PIXELS or index >= DAWN_PIXELS + NOON_PIXELS:
                # Dawn/Dusk are WS2812B GRB (24-bit)
                buffer.extend((g, r, b))
            else:
                # Noon/sun section is SK6812 RGBW (32-bit)
                buffer.extend((r, g, b, w))
        return buffer

    def show(self):
        neopixel_write(self.pin, self._build_bytearray())

    def test_section_color_orders(self, start_pixel, end_pixel, color, delay=2.0):
        """Test different color orders on a pixel range"""
        orders = ["RGB", "GRB", "BRG", "GBR", "BGR", "RBG"]

        print(f"\nTesting pixels {start_pixel}-{end_pixel-1} with {color}")
        print("Expected color should be: RED" if color == (255, 0, 0) else
              "GREEN" if color == (0, 255, 0) else
              "BLUE" if color == (0, 0, 255) else str(color))

        for order in orders:
            # Clear section
            for i in range(start_pixel, end_pixel):
                self.pixels[i] = (0, 0, 0, 0)

            # Set with current order
            for i in range(start_pixel, end_pixel):
                self.set_pixel_order(i, color, order)

            self.show()
            print(f"  {order}: ", end="")
            time.sleep(delay)

        # Clear section at end
        for i in range(start_pixel, end_pixel):
            self.pixels[i] = (0, 0, 0, 0)
        self.show()


# Initialize strips
sky_strip = ColorOrderTester(SKY_PIN, TOTAL_SKY_PIXELS, BRIGHTNESS)  # GPIO4
ground_pixels = neopixel.NeoPixel(
    GROUND_PIN,  # GPIO2
    GROUND_PIXEL_COUNT,
    brightness=BRIGHTNESS,
    auto_write=False,
)


def test_color_orders():
    """Run diagnostic test for different color orders"""
    print("LED Color Order Diagnostic Test")
    print("=" * 40)
    print(f"Sky strip (GPIO{config.NEOPIXEL_PIN}): {TOTAL_SKY_PIXELS} pixels total")
    print(f"Ground strip (GPIO{config.NEOPIXEL_GROUND_PIN}): {GROUND_PIXEL_COUNT} pixels")
    print(f"  Dawn (WS2812B GRB): pixels 0-{DAWN_PIXELS-1}")
    print(f"  Noon (SK6812 ???): pixels {DAWN_PIXELS}-{DAWN_PIXELS+NOON_PIXELS-1}")
    print(f"  Dusk (WS2812B GRB): pixels {DAWN_PIXELS+NOON_PIXELS}-{TOTAL_SKY_PIXELS-1}")
    print()
    print("Testing different color orders for SK6812 section...")
    print("Watch the noon section and note which order shows the correct color!")

    # Test red
    sky_strip.test_section_color_orders(DAWN_PIXELS, DAWN_PIXELS + NOON_PIXELS, (255, 0, 0), 3.0)

    # Test green
    sky_strip.test_section_color_orders(DAWN_PIXELS, DAWN_PIXELS + NOON_PIXELS, (0, 255, 0), 3.0)

    # Test blue
    sky_strip.test_section_color_orders(DAWN_PIXELS, DAWN_PIXELS + NOON_PIXELS, (0, 0, 255), 3.0)

    print("\nDiagnostic complete!")
    print("Which color order showed the correct colors for the SK6812 section?")
    print("Update the code with the correct order (RGB, GRB, BRG, etc.)")


def demo_corrected_colors(correct_order):
    """Demo the strip with corrected color order"""
    print(f"\nDemo with corrected SK6812 order: {correct_order}")

    # Set dawn section (GRB)
    for i in range(DAWN_PIXELS):
        sky_strip.set_pixel_grb(i, (255, 0, 0))  # Red

    # Set noon section with correct order
    for i in range(DAWN_PIXELS, DAWN_PIXELS + NOON_PIXELS):
        sky_strip.set_pixel_order(i, (255, 0, 0), correct_order)  # Red

    # Set dusk section (GRB)
    for i in range(DAWN_PIXELS + NOON_PIXELS, TOTAL_SKY_PIXELS):
        sky_strip.set_pixel_grb(i, (255, 0, 0))  # Red

    sky_strip.show()
    time.sleep(2)

    # Test other colors
    colors = [(0, 255, 0), (0, 0, 255), (255, 255, 255)]  # Green, Blue, White
    for color in colors:
        # Dawn (GRB)
        for i in range(DAWN_PIXELS):
            sky_strip.set_pixel_grb(i, color)

        # Noon (correct order)
        for i in range(DAWN_PIXELS, DAWN_PIXELS + NOON_PIXELS):
            sky_strip.set_pixel_order(i, color, correct_order)

        # Dusk (GRB)
        for i in range(DAWN_PIXELS + NOON_PIXELS, TOTAL_SKY_PIXELS):
            sky_strip.set_pixel_grb(i, color)

        sky_strip.show()
        time.sleep(1.5)


# Main test
print("Starting LED color order diagnostic...")
print(f"Configured sky pin: GPIO{SKY_PIN} (should be 4)")
print(f"Configured ground pin: GPIO{GROUND_PIN} (should be 2)")

# First run the diagnostic
test_color_orders()

# Then demo with assumed correct order (change this based on your results!)
# Common SK6812 orders: RGB, GRB, BRG
demo_corrected_colors("RGB")  # Change this to the correct order you observed

print("\nTest complete. Update the code with the correct color order!")