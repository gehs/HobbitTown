"""
HobbitTown ESP32-S3 Main Entry Point

Runs a full hardware run-through on startup (all 3 smials, ~2 minutes),
then continues with the non-blocking ambient main loop.

Hardware is enabled/disabled via config.py flags.
See config.py for all pin assignments and hardware settings.
"""

import time
import config

from hardware import lighting_sky, lighting_ground, lighting_stream
from hardware import lighting_manager
from hardware import motion, audio, atmosphere
from logic.full_run_scene import full_run
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
    print(f"  Ground Effects (GPIO5):  {config.NUM_PIXELS_GROUND} pixels @ {config.BRIGHTNESS:.2f} brightness")
    print(f"  Stream Beads   (GPIO6):  {config.NUM_PIXELS_STREAM} pixels @ {config.BRIGHTNESS:.2f} brightness")

    print("\n[I2C BUS]")
    print(f"  SDA: GPIO8 | SCL: GPIO9")
    if config.ENABLE_MOTION:
        print(f"  PCA9685 #1 (Motion): 0x{config.PCA9685_ADDR1:02X}")

    print("\n[AUDIO]")
    if config.ENABLE_AUDIO_UART:
        print(f"  UART TX (GPIO17) -> Tsunami RXI | UART RX (GPIO18) -> Tsunami TXO")
        print(f"  Baudrate: {config.AUDIO_UART_BAUDRATE} | Outputs 1-6 active")

    print("\n[RELAYS]")
    print(f"  Fogger      (GPIO39)  ENABLE_ATMOSPHERE = {config.ENABLE_ATMOSPHERE}")
    print(f"  Chimney 1   (GPIO42)  ENABLE_CHIMNEYS   = {getattr(config, 'ENABLE_CHIMNEYS', False)}")
    print(f"  Chimney 2   (GPIO41)")
    print(f"  Chimney 3   (GPIO40)")

    print("\n[MODULE STATUS]")
    print(f"  ENABLE_LIGHTING:    {config.ENABLE_LIGHTING}")
    print(f"  ENABLE_MOTION:      {config.ENABLE_MOTION}")
    print(f"  ENABLE_AUDIO:       {config.ENABLE_AUDIO}")
    print(f"  ENABLE_ATMOSPHERE:  {config.ENABLE_ATMOSPHERE}")
    print(f"  ENABLE_CHIMNEYS:    {getattr(config, 'ENABLE_CHIMNEYS', False)}")
    print(f"  ENABLE_WEB:         {config.ENABLE_WEB}")

    print("\n" + "=" * 70 + "\n")


# ============================================================================
# SETUP
# ============================================================================

def setup():
    """Initialize all hardware modules."""
    print("\n[INIT] Starting HobbitTown ESP32-S3...")

    validate_hardware()

    if config.ENABLE_WEB:
        web_logic.setup_web()

    if config.ENABLE_LIGHTING:
        lighting_sky.setup_lighting_sky()
        lighting_ground.setup_lighting_ground()
        lighting_stream.setup_lighting_stream()
        lighting_manager.ensure_segments_loaded()
    else:
        print("[INIT] Lighting: disabled")

    if config.ENABLE_MOTION:
        motion.setup_hardware()
    else:
        print("[INIT] Motion: disabled")

    if config.ENABLE_AUDIO:
        audio.setup_audio()
    else:
        print("[INIT] Audio: disabled")

    if config.ENABLE_ATMOSPHERE:
        atmosphere.setup_atmosphere()
    else:
        print("[INIT] Atmosphere (fogger): disabled")

    if getattr(config, "ENABLE_CHIMNEYS", False):
        has_setup = callable(getattr(atmosphere, "setup_chimneys", None))
        has_set = callable(getattr(atmosphere, "set_chimney", None))
        has_stop = callable(getattr(atmosphere, "stop_chimneys", None))
        print(f"[INIT] Chimney API: setup={has_setup} set={has_set} stop={has_stop}")
        if not (has_setup and has_set and has_stop):
            print("[WARN] Chimney feature enabled, but atmosphere module is missing chimney APIs. Deploy the latest hardware/atmosphere.py.")

    print("[INIT] Hardware initialized. Starting full run-through...\n")
    full_run.start()


# ============================================================================
# MAIN LOOP
# ============================================================================

def main_loop():
    """Non-blocking main loop — updates all active hardware modules each tick."""
    time.sleep(config.LOOP_DELAY)

    # Run the full hardware run-through until it completes (~120 seconds)
    if full_run.is_running:
        full_run.update()

    if config.ENABLE_WEB:
        web_logic.run_web_sync()

    if config.ENABLE_LIGHTING:
        lighting_sky.run_lighting_cycle_sky()
        lighting_ground.run_lighting_cycle_ground()
        lighting_stream.run_lighting_cycle_stream()

    if config.ENABLE_ATMOSPHERE:
        atmosphere.run_atmosphere_cycle()


# ============================================================================
# ENTRY POINT
# ============================================================================

setup()

while True:
    try:
        main_loop()
    except KeyboardInterrupt:
        print("\n[EXIT] Keyboard interrupt — cleaning up...")
        full_run.stop()
        lighting_sky.set_all_lights_off_sky()
        lighting_ground.set_all_lights_off_ground()
        lighting_stream.set_all_lights_off_stream()
        break
    except Exception as exc:
        print(f"\n[ERROR] Main loop exception: {exc}")
        print("[ERROR] Restarting in 5 seconds...")
        time.sleep(5)