"""
Tsunami Super WAV Trigger binary packet test for ESP32-S3 Exciters on 4L and 4R.

This test validates the Tsunami UART1 connection and output routing to Audio Out 4L and 4R.
It exercises the exciters connected through the LQ-AMP10W with soldered wires.

The Tsunami uses a binary packet protocol:
  0xF0 0xAA (Start of Message)
  Length (1 byte)
  Command code
  Command data
  0x55 (End of Message)

Wire (UART1 on GPIO17/18):
- Tsunami RXI -> ESP32 GPIO17 (U1TXD)
- Tsunami TXO -> ESP32 GPIO18 (U1RXD)
- Common ground

Exciters wired to Tsunami 4L and 4R via LQ-AMP10W (soldered to avoid jack limitations).

To repeat: copy `tsunami.ini` to the SD root, save `code.py`, reset the ESP32, then confirm the Tsunami green track LED and exciter vibration.
"""

import board  # type: ignore
import busio  # type: ignore
import time


class Tsunami:
    def __init__(self, tx_pin, rx_pin, baudrate=57600):
        # Initialize the UART bus. Tsunami expects exactly 57600 baud by default.
        self.uart = busio.UART(tx_pin, rx_pin, baudrate=baudrate)
        self._drain()

    def _drain(self):
        """Drain any pending data from UART."""
        while True:
            data = self.uart.read(32)
            if not data:
                break

    def _send_track_command(self, action, track_num, output_routing=None):
        """Builds and sends the Track Control packet with optional output routing."""
        track_lsb = track_num & 0xFF
        track_msb = (track_num >> 8) & 0xFF

        if output_routing is not None:
            packet = bytearray([
                0xF0,
                0xAA,
                0x09,
                0x03,
                action,
                track_lsb,
                track_msb,
                output_routing,
                0x55,
            ])
        else:
            packet = bytearray([
                0xF0,
                0xAA,
                0x08,
                0x03,
                action,
                track_lsb,
                track_msb,
                0x55,
            ])

        self.uart.write(packet)

    def track_play_poly(self, track_num, output_routing=None):
        """Plays a track, blending it with any already playing."""
        self._send_track_command(0x01, track_num, output_routing)

    def track_play_solo(self, track_num, output_routing=None):
        """Stops all current tracks and plays the requested track."""
        self._send_track_command(0x00, track_num, output_routing)

    def track_pause(self, track_num):
        self._send_track_command(0x02, track_num)

    def track_resume(self, track_num):
        self._send_track_command(0x03, track_num)

    def track_stop(self, track_num):
        self._send_track_command(0x04, track_num)

    def stop_all(self):
        """Stop all is a specific 5-byte command (CMD 0x04)"""
        packet = bytearray([0xF0, 0xAA, 0x05, 0x04, 0x55])
        self.uart.write(packet)


def setup():
    """Test the Tsunami connection with exciters on 4L and 4R."""
    print("Tsunami Exciters test starting...")

    try:
        tsunami = Tsunami(board.GPIO17, board.GPIO18, baudrate=57600)
        print("? Tsunami UART initialized on GPIO17/18 at 57600 baud")

        time.sleep(2)

        # Output routing for 4L and 4R: bits 6 and 7 set
        # Bit mapping: 0=1L, 1=1R, 2=2L, 3=2R, 4=3L, 5=3R, 6=4L, 7=4R
        routing_4L_4R = 0xC0

        print("\nPlaying track 001 on 4L and 4R (binary routing)...")
        tsunami.track_play_poly(1, output_routing=routing_4L_4R)
        print("Track 001 sent to 4L/4R. Listening for vibration for 4 seconds...")
        time.sleep(4)

        print("\nStopping all tracks...")
        tsunami.stop_all()
        print("? Test complete! Check if you felt the exciter vibration on 4L and 4R.")

    except Exception as e:
        print(f"\n? ERROR: {e}")
        import traceback
        traceback.print_exc()


def loop():
    while True:
        time.sleep(1)


setup()
loop()