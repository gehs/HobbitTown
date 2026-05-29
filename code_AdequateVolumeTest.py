"""
Tsunami Multi-Output Volume Cycling Test
Uses shared Tsunami protocol builders with validated frame encoding.
Cycles through Physical Outputs: 1, 2, 3, 4, 7, 8
"""

import time
import board
import busio
from hardware.tsunami_protocol import (
    PLAY_POLY,
    build_control_track_for_index,
    build_output_volume_for_index,
    build_stop_all,
    frame_to_hex,
)


DEBUG_PACKET_HEX = False


class Tsunami:
    """Minimal Tsunami control class for volume testing."""
    
    def __init__(self, tx_pin, rx_pin, baudrate=57600):
        """Initialize UART connection to Tsunami."""
        self.uart = busio.UART(tx_pin, rx_pin, baudrate=baudrate)
        self._drain()
    
    def _drain(self):
        """Drain any pending data from UART."""
        while True:
            data = self.uart.read(32)
            if not data:
                break
    
    def set_output_gain(self, output_channel, gain_db):
        """
        Set output gain for a specific Tsunami output channel using dB values.
        
        Args:
            output_channel: Output 0-7
            gain_db: Gain in dB. 0 is max volume (0dB), -70 is muted (-70dB)
        """
        # Ensure bounds for safety (-70dB to +10dB)
        if gain_db > 10:
            gain_db = 10
        if gain_db < -70:
            gain_db = -70

        packet = build_output_volume_for_index(output_channel, gain_db)
        
        try:
            self.uart.write(packet)
            if DEBUG_PACKET_HEX:
                print("TX (OUTPUT_VOLUME): %s" % frame_to_hex(packet))
            return True
        except Exception as e:
            print(f"Error sending gain command: {e}")
            return False
    
    def track_play_routed(self, track_num, output):
        """
        Plays a track on a specific output route.
        
        Args:
            track_num: Track number (1-4095)
            output: Output route (0-7)
        """
        packet = build_control_track_for_index(
            track_number=track_num,
            output_index=output,
            control_code=PLAY_POLY,
            lock_voice=False,
        )
        
        try:
            self.uart.write(packet)
            if DEBUG_PACKET_HEX:
                print("TX (CONTROL_TRACK): %s" % frame_to_hex(packet))
            return True
        except Exception as e:
            print(f"Error sending track play command: {e}")
            return False
    
    def stop_all(self):
        """Stop all tracks."""
        packet = build_stop_all()
        
        try:
            self.uart.write(packet)
            if DEBUG_PACKET_HEX:
                print("TX (STOP_ALL): %s" % frame_to_hex(packet))
            return True
        except Exception as e:
            print(f"Error sending stop command: {e}")
            return False


def setup():
    """Initialize and prepare for testing."""
    global tsunami
    
    print("=" * 60)
    print("Tsunami Target Output & Volume Cycling Test")
    print("=" * 60)
    
    try:
        tsunami = Tsunami(board.GPIO17, board.GPIO18, baudrate=57600)
        print("✓ Tsunami UART initialized (GPIO17 TX, GPIO18 RX, 57600 baud)")
    except Exception as e:
        print(f"✗ Failed to initialize Tsunami: {e}")
        return False
    
    return True


def cycle_outputs_test():
    """
    Cycles through physical outputs 1, 2, 3, 4, 7, 8.
    Fades volume up, holds, fades down, then moves to the next output channel.
    """
    # Mapping table: (Physical label, Zero-indexed code routing)
    target_outputs = [
        (1, 0),  # Output 1 (1L)
        (2, 1),  # Output 2 (1R)
        (3, 2),  # Output 3 (2L)
        (4, 3),  # Output 4 (2R)
        (7, 6),  # Output 7 (4L)
        (8, 7)   # Output 8 (4R)
    ]
    
    track_id = 1  # Adjust as needed per your MicroSD file index
    fade_delay = 0.214
    print("\nStarting multi-channel output sweep...")
    
    for physical_num, code_channel in target_outputs:
        print("-" * 60)
        print(f"TESTING PHYSICAL OUTPUT: {physical_num} (Channel Index {code_channel})")
        print("-" * 60)
        
        # 1. Initialize output to silent (-70 dB) before triggering track
        tsunami.set_output_gain(code_channel, -70)
        time.sleep(0.05)
        
        print(f"Triggering Track {track_id} on Output {physical_num}...")
        if not tsunami.track_play_routed(track_id, code_channel):
            print("✗ Failed to start playback")
            continue
            
        time.sleep(0.2)  # Give track brief moment to initiate buffers
        
        # 2. Fade volume UP over 15 seconds (-70dB to 0dB)
        print("Fading Volume Up (15 Second Window)...")
        for db in range(-70, 1, 1):  # Step up cleanly by 1 dB
            tsunami.set_output_gain(code_channel, db)
            # Print feedback every 10dB so the console isn't flooded
            if db % 10 == 0 or db == -70 or db == 0:
                print(f"   Current Gain: {db} dB")
            time.sleep(fade_delay)
            
        # 3. Hold at Max volume (0dB) to verify audio stability
        print("Holding Max Volume (0dB) for 3 seconds...")
        tsunami.set_output_gain(code_channel, 0)
        time.sleep(3.0)
        
        # 4. Fade volume DOWN over 15 seconds (0dB to -70dB)
        print("Fading Volume Down (15 Second Window)...")
        for db in range(0, -71, -1):  # Step down cleanly by 1 dB
            tsunami.set_output_gain(code_channel, db)
            if db % 10 == 0 or db == 0 or db == -70:
                print(f"   Current Gain: {db} dB")
            time.sleep(fade_delay)
            
        # Stop track to prepare clean buffers for the next channel
        tsunami.stop_all()
        time.sleep(1.0)


def cleanup():
    """Ensure all channels are muted and tracks stopped."""
    print("\n" + "-" * 60)
    print("CLEANUP")
    print("-" * 60)
    
    # Silence all target channels safely
    channels = [0, 1, 2, 3, 6, 7]
    for ch in channels:
        tsunami.set_output_gain(ch, -70)
        
    tsunami.stop_all()
    print("✓ All targets muted and tracks stopped.")


def run_test():
    """Main execution control workflow."""
    if not setup():
        return
    
    try:
        cycle_outputs_test()
    except KeyboardInterrupt:
        print("\n✗ Test paused/interrupted manually.")
    finally:
        cleanup()
        print("=" * 60)
        print("Test cycle concluded.")
        print("=" * 60)


if __name__ == "__main__":
    run_test()