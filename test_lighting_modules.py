"""
Test: Lighting Modules (Sky, Ground, Stream)

Demonstrates how to use the three independent lighting modules
to test individual LED strips or run coordinated scenes.
"""

import config
from hardware import lighting_sky, lighting_ground, lighting_stream
import time


def test_all_modules_sequential():
    """Test each lighting module sequentially."""
    print("\n=== LIGHTING MODULE TEST (Sequential) ===\n")

    # Initialize all modules
    lighting_sky.setup_lighting_sky()
    lighting_ground.setup_lighting_ground()
    lighting_stream.setup_lighting_stream()

    # Test sky strip
    print("[1/3] Testing Sky Arc Strip...")
    lighting_sky.apply_lighting_preset_sky(1)  # Morning warm glow
    time.sleep(2)
    lighting_sky.apply_lighting_preset_sky(5)  # Party rainbow
    for _ in range(10):
        lighting_sky.run_lighting_cycle_sky()
        time.sleep(0.1)
    lighting_sky.set_all_lights_off_sky()

    # Test ground strip
    print("[2/3] Testing Ground Effects Strip...")
    lighting_ground.apply_lighting_preset_ground(2)  # Day bright white
    time.sleep(2)
    lighting_ground.apply_lighting_preset_ground(9)  # Storm flicker
    for _ in range(20):
        lighting_ground.run_lighting_cycle_ground()
        time.sleep(0.05)
    lighting_ground.set_all_lights_off_ground()

    # Test stream beads
    print("[3/3] Testing Stream Bead String...")
    lighting_stream.apply_lighting_preset_stream(3)  # Sunset gradient
    time.sleep(2)
    lighting_stream.apply_lighting_preset_stream(6)  # Fast party
    for _ in range(15):
        lighting_stream.run_lighting_cycle_stream()
        time.sleep(0.1)
    lighting_stream.set_all_lights_off_stream()

    print("\n=== TEST COMPLETE ===\n")


def test_all_modules_synchronized():
    """Test all three modules running the same preset simultaneously."""
    print("\n=== LIGHTING MODULE TEST (Synchronized) ===\n")

    # Initialize all modules
    lighting_sky.setup_lighting_sky()
    lighting_ground.setup_lighting_ground()
    lighting_stream.setup_lighting_stream()

    # Apply same preset to all
    print("Applying Preset 5 (Party Rainbow) to all strips...")
    lighting_sky.apply_lighting_preset_sky(5)
    lighting_ground.apply_lighting_preset_ground(5)
    lighting_stream.apply_lighting_preset_stream(5)

    # Run synchronized animation for 5 seconds
    start = time.monotonic()
    while time.monotonic() - start < 5.0:
        lighting_sky.run_lighting_cycle_sky()
        lighting_ground.run_lighting_cycle_ground()
        lighting_stream.run_lighting_cycle_stream()
        time.sleep(0.05)

    # Fade to night
    print("Fading to Night preset...")
    lighting_sky.apply_lighting_preset_sky(4)
    lighting_ground.apply_lighting_preset_ground(4)
    lighting_stream.apply_lighting_preset_stream(4)
    time.sleep(2)

    # Off
    lighting_sky.set_all_lights_off_sky()
    lighting_ground.set_all_lights_off_ground()
    lighting_stream.set_all_lights_off_stream()

    print("\n=== TEST COMPLETE ===\n")


if __name__ == "__main__":
    # Uncomment the test you want to run:
    test_all_modules_sequential()
    # test_all_modules_synchronized()
