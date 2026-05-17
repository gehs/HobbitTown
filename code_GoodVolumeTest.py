"""
Tsunami Test (1L Output)
Fails to adjust Volume, but does play sound.
"""

import time
import board
import busio


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
    
    def set_output_gain(self, output_channel, gain_value):
        """
        Set output gain for a specific Tsunami output channel.
        
        Args:
            output_channel: Output 0-7 (e.g., 6 for 1L left channel)
            gain_value: Gain level 0-255 (0 = silent, 255 = max)
        """
        # Tsunami gain command format (UART binary):
        # [0xF0, 0xAA, length, 0x0D, output, gain_LSB, gain_MSB, 0x55]
        # where 0x0D is CMD_SET_OUTPUT_GAIN (13)
        
        gain_lsb = gain_value & 0xFF
        gain_msb = (gain_value >> 8) & 0xFF
        
        packet = bytearray([
            0xF0,                    # Start of Message 1
            0xAA,                    # Start of Message 2
            0x05,                    # Length of message (cmd + output + gain_LSB + gain_MSB + end)
            0x0D,                    # Command: Set Output Gain (13)
            output_channel,          # Output channel (0-7)
            gain_lsb,                # Gain value LSB
            gain_msb,                # Gain value MSB
            0x55                     # End of Message
        ])
        
        try:
            self.uart.write(packet)
            return True
        except Exception as e:
            print(f"Error sending gain command: {e}")
            return False
    
    def track_play_routed(self, track_num, output):
        """
        Plays a track on a specific output.
        
        Args:
            track_num: Track number (0-4095)
            output: Output route (0-7)
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
            int(output),       # Output Route
            0x00,              # Flags (0 = normal, 1 = lock voice)
            0x55               # End of Message
        ])
        
        try:
            self.uart.write(packet)
            return True
        except Exception as e:
            print(f"Error sending track play command: {e}")
            return False
    
    def stop_all(self):
        """Stop all tracks."""
        packet = bytearray([0xF0, 0xAA, 0x05, 0x04, 0x55])
        
        try:
            self.uart.write(packet)
            return True
        except Exception as e:
            print(f"Error sending stop command: {e}")
            return False


def setup():
    """Initialize and prepare for testing."""
    global tsunami
    
    print("=" * 60)
    print("Tsunami Volume Control Test (1L Output)")
    print("=" * 60)
    print()
    
    # Initialize Tsunami UART
    try:
        tsunami = Tsunami(board.GPIO17, board.GPIO18, baudrate=57600)
        print("✓ Tsunami UART initialized (GPIO17 TX, GPIO18 RX, 57600 baud)")
        print()
    except Exception as e:
        print(f"✗ Failed to initialize Tsunami: {e}")
        return False
    
    return True


def test_gradual_volume_ramp():
    """
    Phase 1: Gradual volume ramp
    Linearly increase volume from 0 to 255 over ~30 seconds.
    """
    print("-" * 60)
    print("PHASE 1: GRADUAL VOLUME RAMP (30 seconds)")
    print("-" * 60)
    print()
    
    # Start audio playback on 1L output (output 6)
    # Using track 500 (first track in output 5 range per config)
    track_id = 500
    output_channel = 6  # 1L left channel
    
    print(f"Starting track {track_id} on output {output_channel} (1L)...")
    if not tsunami.track_play_routed(track_id, output_channel):
        print("✗ Failed to start playback")
        return False
    
    time.sleep(0.5)  # Allow track to start
    
    print("Ramping volume from 0 to 255...")
    print()
    
    # Ramp volume in steps over ~30 seconds
    # Total steps: 51 (0 to 255 by 5) = 51 iterations
    # Time per step: 30 sec / 51 ≈ 588 ms
    step_size = 5
    delay_per_step = 0.588  # seconds
    
    for gain in range(0, 256, step_size):
        if tsunami.set_output_gain(output_channel, gain):
            percent = (gain / 255.0) * 100
            print(f"Volume: {gain:3d}/255 ({percent:5.1f}%)")
            time.sleep(delay_per_step)
        else:
            print(f"✗ Failed to set gain to {gain}")
            break
    
    # Ensure we reach maximum
    if tsunami.set_output_gain(output_channel, 255):
        print(f"Volume: 255/255 (100.0%)")
    
    print()
    print("✓ Phase 1 complete")
    print()


def test_stepwise_volume_levels():
    """
    Phase 2: Stepwise volume levels
    Hold at 5 discrete levels: 0%, 25%, 50%, 75%, 100%.
    Each level held for 2 seconds.
    """
    print("-" * 60)
    print("PHASE 2: STEPWISE VOLUME LEVELS (5 steps × 2 sec = 10 seconds)")
    print("-" * 60)
    print()
    
    output_channel = 0  # 1L left channel
    
    # Define 5 step levels
    steps = [
        (0,   "0%   (Silent)"),
        (64,  "25%  (Quiet)"),
        (128, "50%  (Medium)"),
        (192, "75%  (Loud)"),
        (255, "100% (Maximum)")
    ]
    
    hold_time = 2.0  # seconds per step
    
    for gain_value, label in steps:
        if tsunami.set_output_gain(output_channel, gain_value):
            print(f"Step: {label} (gain={gain_value:3d})")
            time.sleep(hold_time)
        else:
            print(f"✗ Failed to set step {label}")
            break
    
    print()
    print("✓ Phase 2 complete")
    print()


def cleanup():
    """Stop playback and reset to safe state."""
    print("-" * 60)
    print("CLEANUP")
    print("-" * 60)
    print()
    
    # Set volume to 0 before stopping
    output_channel = 6
    print("Stopping audio and resetting gain...")
    tsunami.set_output_gain(output_channel, 0)
    time.sleep(0.2)
    
    # Stop all playback
    tsunami.stop_all()
    print("✓ All tracks stopped")
    print()


def run_test():
    """Run complete volume control test."""
    if not setup():
        print("Setup failed. Exiting.")
        return
    
    try:
        test_gradual_volume_ramp()
        time.sleep(2)  # Pause between phases
        test_stepwise_volume_levels()
    except KeyboardInterrupt:
        print("\n✗ Test interrupted by user")
    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
    finally:
        cleanup()
        print("=" * 60)
        print("Test complete")
        print("=" * 60)


# Entry point
if __name__ == "__main__":
    run_test()
