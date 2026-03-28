import time
import config
import hardware.lighting as lighting
import hardware.motion as motion
import hardware.audio as audio
import hardware.atmosphere as atmosphere
import time_sync
import web_logic

# States
MORNING = 0
DAY = 1
EVENING = 2
NIGHT = 3

current_state = DAY
party_mode_active = False
last_hour = -1

def setup():
    """Initialize all hardware and systems."""
    print("The Shire is waking up...")
    
    lighting.setup_lighting()
    motion.setup_hardware()
    audio.setup_audio()
    atmosphere.setup_atmosphere()
    web_logic.setup_web()
    
    print("Shire controller ready.")

def loop():
    """Main execution cycle."""
    web_logic.run_web_sync()
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

# --- Main Execution ---
setup()

while True:
    try:
        loop()
        time.sleep(config.LOOP_DELAY)
    except Exception as e:
        print(f"Error in main loop: {e}")
        time.sleep(1)