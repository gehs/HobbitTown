"""PCA9685 door servo bench test for Hobbit Town.

This script exercises PCA9685 PWM channels 0-3 and prints I2C diagnostics.
Use it after wiring the PCA9685 board with VCC, GND, SDA, SCL, OE low, and V+ for servo power.
"""

import time
import config
import hardware.motion as motion

TEST_CHANNELS = [0, 1, 2, 3]
SWEEP_ANGLE = 90
RETURN_ANGLE = 0
PAUSE_SECONDS = 2.0


def print_wiring_reminder():
    print("PCA9685 bench test starting")
    print("--- Wiring reminder ---")
    print("  GND  -> common ground with ESP32 and servos")
    print("  VCC  -> 5V logic power for PCA9685 and I2C")
    print("  V+   -> 5V servo power bus")
    print("  SDA  -> GPIO21")
    print("  SCL  -> GPIO47")
    print("  OE   -> tie to GND on non-jumpered boards")
    print("---")


def run_servo_test():
    config.ENABLE_MOTION = True
    motion.setup_hardware()

    diagnostics = motion.get_bus_diagnostics()
    print("I2C diagnostics:", diagnostics.get("found", []))
    print("Expected addresses:", diagnostics.get("expected", []))
    print("PCA9685 health:", diagnostics.get("pca9685", {}))
    if not diagnostics.get("hardware_ready"):
        print("Hardware not ready. Verify power, OE, and I2C wiring.")
        return

    print("Beginning servo channel sweep")
    for channel in TEST_CHANNELS:
        print(f"Channel {channel}: move to {SWEEP_ANGLE}°")
        motion.set_servo_channel(channel, SWEEP_ANGLE)
        time.sleep(PAUSE_SECONDS)
        print(f"Channel {channel}: return to {RETURN_ANGLE}°")
        motion.set_servo_channel(channel, RETURN_ANGLE)
        time.sleep(1.0)

    print("Servo sweep complete. Restoring door servos to 90°.")
    for door_id in (1, 2, 3):
        motion.set_door(door_id, 90)
    print("Test finished.")


print_wiring_reminder()
run_servo_test()
