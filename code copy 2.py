"""
HobbitTown ESP32-S3 Main Entry Point

Orchestrates all hardware modules (lighting, motion, audio, atmosphere) and
the web server. Runs a non-blocking main loop with optional hardware validation.

Hardware modules are fully independent and can be enabled/disabled via config.py.
See config.py for all pin assignments and hardware settings.
"""

import time
import config

# Import all hardware modules
from hardware import lighting_sky, lighting_ground, lighting_stream
from hardware import motion, audio, atmosphere
import web_logic


# ============================================================================
# HARDWARE VALIDATION
# ============================================================================

def validate_hardware():
    """Log all active GPIO and I2C assignments for wiring verification."""
    if not getattr(config, "ENABLE_HARDWARE_VALIDATION", False):
        return

    print("\n" + "=" * 70)
    print("HARDWARE VALIDATION REPORT")
    print("=" * 70)

    print("\n[LIGHTING PINS]")
    print(f"  Sky Arc        (GPIO4):  {config.NUM_PIXELS_SKY} pixels @ {config.BRIGHTNESS:.2f} brightness")
    print(f"  Ground Effects (GPIO2):  {config.NUM_PIXELS_GROUND} pixels @ {config.BRIGHTNESS:.2f} brightness")
    print(f"  Stream Beads   (GPIO5):  {config.NUM_PIXELS_STREAM} pixels @ {config.BRIGHTNESS:.2f} brightness")

    print("\n[I2C BUS]")
    print(f"  SDA: GPIO8")
    print(f"  SCL: GPIO9")
    if config.ENABLE_MOTION:
        print(f"  PCA9685 #1 (Motion):     0x{config.PCA9685_ADDR1:02X}")
        print(f"  PCA9685 #2 (Vapor/PWM):  0x{config.PCA9685_ADDR2:02X}")

    print("\n[AUDIO]")
    if config.ENABLE_AUDIO_UART:
        print(f"  UART TX (GPIO17):  Tsunami RXI")
        print(f"  UART RX (GPIO18):  Tsunami TXO @ {config.AUDIO_UART_BAUDRATE} baud")
    if config.ENABLE_AUDIO_I2C:
        print(f"  I2C Address:       0x{config.AUDIO_I2C_ADDR:02X} (WAV Trigger Pro)")

    print("\n[RELAYS]")
    print(f"  Fogger      (GPIO21?): {config.FOGGER_RELAY_PIN}")
    print(f"  Chimney 1   (GPIO21):  {config.CHIMNEY_RELAY_PIN1}")
    print(f"  Chimney 2   (GPIO40):  {config.CHIMNEY_RELAY_PIN2}")
    print(f"  Chimney 3   (GPIO41):  {config.CHIMNEY_RELAY_PIN3}")

    print("\n[MODULE STATUS]")
    print(f"  ENABLE_LIGHTING:    {config.ENABLE_LIGHTING}")
    print(f"  ENABLE_MOTION:      {config.ENABLE_MOTION}")
    print(f"  ENABLE_AUDIO:       {config.ENABLE_AUDIO}")
    print(f"  ENABLE_ATMOSPHERE:  {config.ENABLE_ATMOSPHERE}")
    print(f"  ENABLE_WEB:         {config.ENABLE_WEB}")

    print("\n" + "=" * 70)
    print("VALIDATION COMPLETE — Verify physical wiring matches above layout")
    print("=" * 70 + "\n")


# ============================================================================
# SETUP
# ============================================================================

def setup():
    """Initialize all hardware modules."""
    print("\n[INIT] Starting HobbitTown ESP32-S3...")
    print(f"[INIT] Main loop delay: {config.LOOP_DELAY}s")

    validate_hardware()

    # Initialize web server (if enabled)
    if config.ENABLE_WEB:
        web_logic.setup_web()

    # Initialize lighting modules (fully independent)
    if config.ENABLE_LIGHTING:
        lighting_sky.setup_lighting_sky()
        lighting_ground.setup_lighting_ground()
        lighting_stream.setup_lighting_stream()
    else:
        print("[INIT] Lighting: disabled")

    # Initialize motion (PCA9685 servos/blowers)
    if config.ENABLE_MOTION:
        motion.setup_hardware()
    else:
        print("[INIT] Motion: disabled")

    # Initialize audio (Tsunami WAV Trigger)
    if config.ENABLE_AUDIO:
        audio.setup_audio()
    else:
        print("[INIT] Audio: disabled")

    # Initialize atmosphere (fogger relay)
    if config.ENABLE_ATMOSPHERE:
        atmosphere.setup_atmosphere()
    else:
        print("[INIT] Atmosphere: disabled")

    print("[INIT] All hardware initialized. Entering main loop...\n")


# ============================================================================
# MAIN LOOP
# ============================================================================

def main_loop():
    """
    Non-blocking main loop. Yields time and updates all active hardware modules.
    Call this function repeatedly in your code.py or let it run as the main loop.
    """
    # Optional: yield to other tasks
    time.sleep(config.LOOP_DELAY)

    # Update web server (accepts one pending request per loop iteration)
    if config.ENABLE_WEB:
        web_logic.run_web_sync()

    # Update lighting animations
    if config.ENABLE_LIGHTING:
        lighting_sky.run_lighting_cycle_sky()
        lighting_ground.run_lighting_cycle_ground()
        lighting_stream.run_lighting_cycle_stream()

    # Update atmosphere (fogger cycles)
    if config.ENABLE_ATMOSPHERE:
        atmosphere.run_atmosphere_cycle()

    # Motion and audio modules do not require per-loop updates
    # (they manage their own state or are purely command-based)


# ============================================================================
# ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    setup()

    # Main loop – run forever
    while True:
        try:
            main_loop()
        except KeyboardInterrupt:
            print("\n[EXIT] Keyboard interrupt. Cleaning up...")
            lighting_sky.set_all_lights_off_sky()
            lighting_ground.set_all_lights_off_ground()
            lighting_stream.set_all_lights_off_stream()
            break
        except Exception as exc:
            print(f"\n[ERROR] Main loop exception: {exc}")
            print("[ERROR] Restarting in 5 seconds...")
            time.sleep(5)
