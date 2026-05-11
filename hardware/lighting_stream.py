"""
Stream Bead Lighting Controller for HobbitTown ESP32-S3.

Controls the stream bead string (GPIO5): 85px of independent effect lighting
for accent and special effects.
"""

import neopixel  # type: ignore
import config
import random

pixels = None
current_preset = 0
animation_step = 0
is_available = False


def setup_lighting_stream():
    """Initialize stream bead lighting strip."""
    global pixels, is_available

    if not getattr(config, "ENABLE_LIGHTING", True):
        pixels = None
        is_available = False
        print("Stream Bead Lighting: disabled (enable in config.py when the strip is connected)")
        return

    try:
        pixels = neopixel.NeoPixel(
            config.NEOPIXEL_STREAM_BEAD_PIN,
            config.NUM_PIXELS_STREAM_BEAD,
            brightness=config.BRIGHTNESS,
            auto_write=False,
        )
        pixels.fill((0, 0, 0))
        pixels.show()
        is_available = True
        print("Stream Bead Lighting: initialized")
    except Exception as exc:
        pixels = None
        is_available = False
        print(f"Stream Bead Lighting: dry-load mode ({exc})")


def apply_lighting_preset_stream(preset_id):
    """Apply a preset color/animation to the stream bead string."""
    global current_preset, animation_step
    current_preset = preset_id
    animation_step = 0

    if pixels is None:
        return

    if preset_id == 1:  # Morning - warm glow
        pixels.fill((255, 215, 0))  # Gold
    elif preset_id == 2:  # Day - bright white
        pixels.fill((255, 255, 255))  # White
    elif preset_id == 3:  # Sunset - orange gradient
        for i in range(config.NUM_PIXELS_STREAM_BEAD):
            v = 0.784 - (0.784 - 0.251) * (i / (config.NUM_PIXELS_STREAM_BEAD - 1))
            pixels[i] = hsv_to_rgb(0.078, 0.784, v)
    elif preset_id == 4:  # Night - dim blue
        pixels.fill((138, 43, 226))  # BlueViolet
    elif preset_id in (5, 6, 9):  # Animated presets
        pass  # Handled in run_lighting_cycle_stream
    else:
        pixels.fill((0, 0, 0))

    pixels.show()


def run_lighting_cycle_stream():
    """Non-blocking lighting animation update."""
    global animation_step

    if pixels is None:
        return

    if current_preset == 5:  # Party rainbow
        for i in range(config.NUM_PIXELS_STREAM_BEAD):
            hue = ((animation_step + i * 7) % 256) / 255.0
            pixels[i] = hsv_to_rgb(hue, 1.0, 1.0)
        animation_step += 1
        pixels.show()
    elif current_preset == 6:  # Fast party
        for i in range(config.NUM_PIXELS_STREAM_BEAD):
            hue = ((animation_step + i * 12) % 256) / 255.0
            pixels[i] = hsv_to_rgb(hue, 1.0, 1.0)
        animation_step += 2
        pixels.show()
    elif current_preset == 9:  # Storm flicker
        if random.randint(0, 255) < 60:
            pixels.fill((255, 255, 255))  # White lightning
        else:
            pixels.fill((0, 0, 255))  # Blue
        pixels.show()


def set_all_lights_off_stream():
    """Turn off all stream bead pixels."""
    if pixels is None:
        return
    pixels.fill((0, 0, 0))
    pixels.show()


def hsv_to_rgb(h, s, v):
    """Convert HSV to RGB tuple (0-255)."""
    if s == 0.0:
        r = g = b = int(v * 255)
        return (r, g, b)

    i = int(h * 6.0)
    f = (h * 6.0) - i
    p = v * (1.0 - s)
    q = v * (1.0 - s * f)
    t = v * (1.0 - s * (1.0 - f))

    i = i % 6

    if i == 0:
        r, g, b = v, t, p
    elif i == 1:
        r, g, b = q, v, p
    elif i == 2:
        r, g, b = p, v, t
    elif i == 3:
        r, g, b = p, q, v
    elif i == 4:
        r, g, b = t, p, v
    else:
        r, g, b = v, p, q

    return (int(r * 255), int(g * 255), int(b * 255))
