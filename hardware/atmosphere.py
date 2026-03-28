import digitalio  # type: ignore
import time
import config

fogger_relay = None
last_fog_time = 0
is_fogging = False

def setup_atmosphere():
    global fogger_relay
    fogger_relay = digitalio.DigitalInOut(config.FOGGER_RELAY_PIN)
    fogger_relay.direction = digitalio.Direction.OUTPUT
    fogger_relay.value = True  # Relay off
    print("Atmosphere: initialized")

def run_atmosphere_cycle():
    global last_fog_time, is_fogging
    current_time = time.monotonic()
    
    if not is_fogging and (current_time - last_fog_time >= config.FOG_INTERVAL):
        print("Atmosphere: Triggering morning mist...")
        fogger_relay.value = False  # Turn on
        last_fog_time = current_time
        is_fogging = True
    elif is_fogging and (current_time - last_fog_time >= config.FOG_DURATION):
        print("Atmosphere: Mist cycle complete.")
        fogger_relay.value = True  # Turn off
        is_fogging = False