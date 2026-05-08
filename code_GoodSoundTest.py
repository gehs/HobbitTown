"""
Tsunami Super WAV Trigger binary packet test for ESP32-S3.
Uses the 10-byte Extended Track Control command for instant Mono routing.
Wire (UART1 on GPIO17/18):
- Tsunami RXI -> ESP32 GPIO17 (U1TXD)
- Tsunami TXO -> ESP32 GPIO18 (U1RXD)
- Common ground
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
        
        # Output definitions for the Tsunami 4-channel speaker setup
        output_1L = 0
        output_1R = 1
        output_2L = 2
        output_2R = 3
        output_3L = 4
        output_3R = 5
        output_4L = 6
        output_4R = 7
        
        print("\nSending Track 001 to 1L using 10-byte command...")
        tsunami.track_play_routed(1, output_1L)
        time.sleep(3)
        
        print("Sending Track 001 to 2L using 10-byte command...")
        tsunami.track_play_routed(1, output_2L)
        time.sleep(3)
        
        print("Sending Track 002 to 1R using 10-byte command...")
        tsunami.track_play_routed(2, output_1R)
        time.sleep(3)
        
        print("Sending Track 002 to 2R using 10-byte command...")
        tsunami.track_play_routed(2, output_2R)
        time.sleep(3)
        
        print("\nStopping all tracks...")
        tsunami.stop_all()
        print("-> Test complete! Played 001 to 1L/2L and 002 to 1R/2R.")
        
    except Exception as e:
        print(f"\n-> ERROR: {e}")
        import traceback
        traceback.print_exc()


def loop():
    while True:
        time.sleep(1)


setup()
loop()