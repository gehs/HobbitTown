import digitalio  # type: ignore
import time
import config

fogger_relay = None
last_fog_time = 0
is_fogging = False
atmosphere_ready = False

chimney_relay_1 = None
chimney_relay_2 = None
chimney_relay_3 = None
chimneys_ready = False


def setup_atmosphere():
    global fogger_relay, is_fogging, atmosphere_ready

    if not getattr(config, "ENABLE_ATMOSPHERE", True):
        fogger_relay = None
        is_fogging = False
        atmosphere_ready = False
        print("Atmosphere: disabled (enable in config.py when the fogger relay is connected)")
        return

    try:
        fogger_relay = digitalio.DigitalInOut(config.FOGGER_RELAY_PIN)
        fogger_relay.direction = digitalio.Direction.OUTPUT
        fogger_relay.value = True  # Relay off
        is_fogging = False
        atmosphere_ready = True
        print("Atmosphere: initialized")
    except Exception as exc:
        fogger_relay = None
        is_fogging = False
        atmosphere_ready = False
        print(f"Atmosphere: dry-load mode ({exc})")


def run_atmosphere_cycle():
    global last_fog_time, is_fogging

    if fogger_relay is None:
        return

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


def setup_chimneys():
    """Initialize the three chimney smoke relays (GPIO40/41/42) as safe-off outputs."""
    global chimney_relay_1, chimney_relay_2, chimney_relay_3, chimneys_ready

    if not getattr(config, "ENABLE_CHIMNEYS", False):
        chimney_relay_1 = None
        chimney_relay_2 = None
        chimney_relay_3 = None
        chimneys_ready = False
        print("Chimneys: disabled (set ENABLE_CHIMNEYS = True in config.py when relays are connected)")
        return

    pins = [
        (config.CHIMNEY_RELAY_PIN1, 'chimney_relay_1'),
        (config.CHIMNEY_RELAY_PIN2, 'chimney_relay_2'),
        (config.CHIMNEY_RELAY_PIN3, 'chimney_relay_3'),
    ]
    relays = []
    for pin, label in pins:
        try:
            relay = digitalio.DigitalInOut(pin)
            relay.direction = digitalio.Direction.OUTPUT
            relay.value = True  # Relay off (active-low relay board)
            relays.append(relay)
        except Exception as exc:
            relays.append(None)
            if getattr(config, "ALLOW_MISSING_HARDWARE", False):
                print(f"Chimneys: {label} dry-load mode ({exc})")
            else:
                raise

    chimney_relay_1, chimney_relay_2, chimney_relay_3 = relays
    chimneys_ready = any(r is not None for r in relays)
    print("Chimneys: initialized")


def set_chimney(chimney_id, on):
    """Turn chimney smoke relay on (True) or off (False). chimney_id is 1, 2, or 3."""
    relay_map = {1: chimney_relay_1, 2: chimney_relay_2, 3: chimney_relay_3}
    relay = relay_map.get(chimney_id)
    if relay is None:
        return
    relay.value = not on  # Active-low relay: False = ON, True = OFF


def stop_chimneys():
    """Turn off all three chimney smoke relays."""
    for chimney_id in (1, 2, 3):
        set_chimney(chimney_id, False)