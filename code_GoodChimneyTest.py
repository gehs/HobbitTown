"""Chimney Relay Test for Hobbit Town.

This script tests the chimney relay on GPIO19.
Connect the MT3608 output to the relay COM, and power the relay.
The script will turn the relay on for 5 seconds, then off.
"""

import time
import digitalio
import config

# Chimney relay pin
CHIMNEY_PIN = config.CHIMNEY_RELAY_PIN

def test_chimney_relay():
    """Test the chimney relay"""
    print("Testing chimney relay on GPIO19...")
    print("Relay should turn on for 5 seconds, then off.")

    # Initialize pin
    pin = digitalio.DigitalInOut(CHIMNEY_PIN)
    pin.direction = digitalio.Direction.OUTPUT

    # Turn on
    pin.value = True
    print("Relay ON")
    time.sleep(5)

    # Turn off
    pin.value = False
    print("Relay OFF")

    print("Test complete.")

if __name__ == "__main__":
    test_chimney_relay()