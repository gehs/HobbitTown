"""Chimney Relay Test for Hobbit Town.

This script tests the chimney relay on GPIO19.
Connect the MT3608 output to the relay COM, and power the relay.
The script will move the relay on and off slowly so you can hear the click.
"""

import time
import digitalio
import config

# Chimney relay pin
CHIMNEY_PIN = config.CHIMNEY_RELAY_PIN

# Seconds to wait for each relay state change
STATE_WAIT_SECONDS = 5


def set_relay(pin, state, label):
    """Set relay state and print a user-friendly message."""
    pin.value = state
    print(f"{label}: {'ON' if state else 'OFF'} (listen for the relay click)")


def countdown(seconds):
    """Countdown to give you time to hear the relay."""
    for remaining in range(seconds, 0, -1):
        print(f"  waiting {remaining}...")
        time.sleep(1)


def test_chimney_relay():
    """Test the chimney relay with clear on/off steps."""
    print("Starting chimney relay test on GPIO19.")
    print("If the relay is active-low, the printed ON/OFF labels may be reversed.")

    pin = digitalio.DigitalInOut(CHIMNEY_PIN)
    pin.direction = digitalio.Direction.OUTPUT

    print("Initial state: OFF first")
    set_relay(pin, False, "Initial state")
    countdown(STATE_WAIT_SECONDS)

    print("Now switching relay ON")
    set_relay(pin, True, "Relay state")
    countdown(STATE_WAIT_SECONDS)

    print("Now switching relay OFF")
    set_relay(pin, False, "Relay state")
    countdown(STATE_WAIT_SECONDS)

    print("One more ON/OFF cycle")
    set_relay(pin, True, "Relay state")
    countdown(STATE_WAIT_SECONDS)
    set_relay(pin, False, "Relay state")

    print("Test complete. If the relay stays active, check wiring and whether the module is active-low.")


if __name__ == "__main__":
    test_chimney_relay()
