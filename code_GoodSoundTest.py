"""
Tsunami Super WAV Trigger binary packet test for ESP32-S3.

This test validates the Tsunami UART1 connection to Audio Out 1L.
It only exercises the first output path for the WAV Trigger.

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

To repeat: copy `tsunami.ini` to the SD root, save `code.py`, reset the ESP32, then confirm the Tsunami green track LED and audio output.
"""

import board  # type: ignore
import busio  # type: ignore
import time


class Tsunami:
    def __init__(self, tx_pin, rx_pin, baudrate=57600):
        # Initialize the UART bus. Tsunami expects exactly 57600 baud by default.
        self.uart = busio.UART(tx_pin, rx_pin, baudrate=baudrate)
        
    def _send_track_command(self, action, track_num):
        """Builds and sends the 8-byte Track Control packet."""
        # The track number is a 16-bit integer, so we split it into two 8-bit bytes (Little Endian)
        track_lsb = track_num & 0xFF
        track_msb = (track_num >> 8) & 0xFF
        
        packet = bytearray([
            0xF0,
            0xAA,
            0x08,
            0x03,
            action,
            track_lsb,
            track_msb,
            0x55
        ])
        self.uart.write(packet)

    def track_play_poly(self, track_num):
        """Plays a track, blending it with any already playing."""
        self._send_track_command(0x01, track_num)
        
    def track_play_solo(self, track_num):
        """Stops all current tracks and plays the requested track."""
        self._send_track_command(0x00, track_num)
        
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
    """Test the Tsunami connection with correct pins."""
    print("Tsunami test starting...")
    
    try:
        # Use GPIO17 (TX) and GPIO18 (RX) for UART1
        tsunami = Tsunami(board.GPIO17, board.GPIO18, baudrate=57600)
        print("? Tsunami UART initialized on GPIO17/18 at 57600 baud")
        
        # Wait for Tsunami to be ready
        time.sleep(1)
        
        # Play track 001 (poly mode)
        print("\nPlaying track 001...")
        tsunami.track_play_poly(1)
        print("Track 001 sent. Listening for 4 seconds...")
        time.sleep(4)
        
        # Play track 002 (poly mode - will blend with track 001)
        print("\nPlaying track 002...")
        tsunami.track_play_poly(2)
        print("Track 002 sent. Listening for 4 seconds...")
        time.sleep(4)
        
        # Stop all
        print("\nStopping all tracks...")
        tsunami.stop_all()
        
        print("\n? Test complete! Check if you heard the audio.")
        
    except Exception as e:
        print(f"\n? ERROR: {e}")
        import traceback
        traceback.print_exc()


def loop():
    while True:
        time.sleep(1)


setup()
loop()
