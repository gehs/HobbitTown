"""Chimney Relay Test for Hobbit Town.

This script tests the chimney relays on GPIO21, GPIO40, GPIO41 for smials 1-3.
Connect the MT3608 outputs to the relay COMs, and power the relays.
The script will move each relay on and off slowly so you can hear the clicks.
"""

import time
import digitalio
import config

# Chimney relay pins
CHIMNEY_PIN1 = config.CHIMNEY_RELAY_PIN1
CHIMNEY_PIN2 = config.CHIMNEY_RELAY_PIN2
CHIMNEY_PIN3 = config.CHIMNEY_RELAY_PIN3

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
    """Test the chimney relays with clear on/off steps."""
    print("Starting chimney relay test on GPIO21, GPIO35, GPIO36.")
    print("If the relay is active-low, the printed ON/OFF labels may be reversed.")

    pins = [
        (CHIMNEY_PIN1, "Chimney 1 (GPIO21)"),
        (CHIMNEY_PIN2, "Chimney 2 (GPIO40)"),
        (CHIMNEY_PIN3, "Chimney 3 (GPIO41)"),
    ]

    for pin_obj, label in pins:
        print(f"\nTesting {label}")
        pin = digitalio.DigitalInOut(pin_obj)
        pin.direction = digitalio.Direction.OUTPUT

        print("Initial state: OFF")
        set_relay(pin, False, "Initial state")
        countdown(STATE_WAIT_SECONDS)

        print("Switching ON")
        set_relay(pin, True, "Relay state")
        countdown(STATE_WAIT_SECONDS)

        print("Switching OFF")
        set_relay(pin, False, "Relay state")
        countdown(STATE_WAIT_SECONDS)

    print("\nAll chimney tests complete. If relays stay active, check wiring and active-low setting.")


if __name__ == "__main__":
    test_chimney_relay()
