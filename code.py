import time
import config
import hardware.lighting as lighting
import hardware.motion as motion
import hardware.audio as audio
import hardware.atmosphere as atmosphere
import hardware.soundscape as soundscape
import time_sync
import web_logic
from logic.test_scene import smial_test

# States
MORNING = 0
DAY = 1
EVENING = 2
NIGHT = 3

current_state = DAY
party_mode_active = False
last_hour = -1


def _safe_setup_step(name, setup_func):
    """Initialize one subsystem without aborting the whole boot in dry-load mode."""
    try:
        setup_func()
    except Exception as exc:
        if getattr(config, "ALLOW_MISSING_HARDWARE", False):
            print(f"{name}: dry-load mode ({exc})")
        else:
            raise


def setup():
    """Initialize all hardware and systems."""
    print("The Shire is waking up...")
    print("Dry-load boot enabled: external components can stay unplugged during upload/testing.")

    _safe_setup_step("lighting", lighting.setup_lighting)
    _safe_setup_step("motion", motion.setup_hardware)
    _safe_setup_step("audio", audio.setup_audio)
    _safe_setup_step("atmosphere", atmosphere.setup_atmosphere)
    _safe_setup_step("web", web_logic.setup_web)

    print("Startup summary:")
    print(" - lighting:", "ready" if getattr(lighting, "is_available", False) else "dry-load")
    print(" - motion:", "ready" if getattr(motion, "hardware_ready", False) else "dry-load")
    print(" - atmosphere:", "ready" if getattr(atmosphere, "atmosphere_ready", False) else "dry-load")
    print(" - web:", "ready" if getattr(web_logic, "server_socket", None) else "standby")
    print("Shire controller ready. Upload confirmed.")


def loop():
    """Main execution cycle."""
    global last_hour, party_mode_active

    # Always handle web requests so the UI stays responsive
    web_logic.run_web_sync()

    # Check if hardware test is running
    if smial_test.is_running:
        smial_test.update()
        return

    lighting.run_lighting_cycle()

    current_hour = time_sync.get_hour()
    if current_hour != last_hour:
        update_state_by_time(current_hour)
        last_hour = current_hour

    if party_mode_active:
        lighting.apply_lighting_preset(5)
        audio.play_party_music()
        party_mode_active = False

    audio.run_audio_cycle()
    atmosphere.run_atmosphere_cycle()


def update_state_by_time(hour):
    global current_state
    if 6 <= hour < 9:
        current_state = MORNING
    elif 9 <= hour < 17:
        current_state = DAY
    elif 17 <= hour < 20:
        current_state = EVENING
    else:
        current_state = NIGHT

    apply_shire_atmosphere(current_state)


def apply_shire_atmosphere(state):
    if state == MORNING:
        lighting.apply_lighting_preset(1)
        audio.play_daytime()
    elif state == DAY:
        lighting.apply_lighting_preset(2)
    elif state == EVENING:
        lighting.apply_lighting_preset(3)
        audio.play_sunset_sfx()
    elif state == NIGHT:
        lighting.apply_lighting_preset(4)
        audio.play_nighttime()


def trigger_hardware_test():
    """Start the hardware certification test sequence."""
    smial_test.start()


# --- Main Execution ---
setup()

while True:
    try:
        loop()
        time.sleep(config.LOOP_DELAY)
    except Exception as e:
        print(f"Error in main loop: {e}")
        time.sleep(1)