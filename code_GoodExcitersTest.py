"""
Tsunami Super WAV Trigger binary packet test for ESP32-S3.
Uses the 10-byte Extended Track Control command for instant Mono routing.
"""

import board  # type: ignore
import busio  # type: ignore
import time


class Tsunami:
    def __init__(self, tx_pin, rx_pin, baudrate=57600):
        self.uart = busio.UART(tx_pin, rx_pin, baudrate=baudrate)
        
    def track_play_routed(self, track_num, output):
        """
        Plays a track directly to a specific output using the 10-byte extended command.
        This matches the manual: Length 0x0A, Command 0x03.
        """
        track_lsb = track_num & 0xFF
        track_msb = (track_num >> 8) & 0xFF
        
        packet = bytearray([
            0xF0,              # Start of Message 1
            0xAA,              # Start of Message 2
            0x0A,              # Length of message (10 bytes)
            0x03,              # Command: Track Control
            0x01,              # Action: Play Poly
            track_lsb,         # Track LSB
            track_msb,         # Track MSB
            int(output),       # Output Route (6 for 4L, 7 for 4R)
            0x00,              # Flags (0 = normal, 1 = lock voice)
            0x55               # End of Message
        ])
        self.uart.write(packet)
        
    def stop_all(self):
        """Stop all tracks (CMD 0x04)"""
        packet = bytearray([0xF0, 0xAA, 0x05, 0x04, 0x55])
        self.uart.write(packet)


def setup():
    print("Tsunami Extended Command test starting...")
    
    try:
        tsunami = Tsunami(board.GPIO17, board.GPIO18, baudrate=57600)
        print("-> Tsunami UART initialized")
        time.sleep(1)
        
        # Mono output definitions
        output_4L = 6
        output_4R = 7
        
        print("\nSending Track 001 to 4L using 10-byte command...")
        tsunami.track_play_routed(1, output_4L)
        
        print("Sending Track 002 to 4R using 10-byte command...")
        tsunami.track_play_routed(2, output_4R)
        
        print("Tracks sent! Listening for 4 seconds...")
        time.sleep(4)
        
        print("\nStopping all tracks...")
        tsunami.stop_all()
        print("-> Test complete!")
        
    except Exception as e:
        print(f"\n-> ERROR: {e}")
        import traceback
        traceback.print_exc()


def loop():
    while True:
        time.sleep(1)


setup()
loop()