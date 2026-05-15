"""
Tsunami Volume Control Test (1L Output)
Tests master volume ramping on output channel 1L with gradual and stepwise phases.
"""

import time
import config

# Import all hardware modules
from hardware import lighting_sky, lighting_ground, lighting_stream
from hardware import motion, audio, atmosphere
import web_logic


# ============================================================================
# HARDWARE VALIDATION
# ============================================================================

def validate_hardware():
    """Log all active GPIO and I2C assignments for wiring verification."""
    if not getattr(config, "ENABLE_HARDWARE_VALIDATION", False):
        return

    print("\n" + "=" * 70)
    print("HARDWARE VALIDATION REPORT")
    print("=" * 70)

    print("\n[LIGHTING PINS]")
    print(f"  Sky Arc        (GPIO4):  {config.NUM_PIXELS_SKY} pixels @ {config.BRIGHTNESS:.2f} brightness")
    print(f"  Ground Effects (GPIO6):  {config.NUM_PIXELS_GROUND} pixels @ {config.BRIGHTNESS:.2f} brightness")
    print(f"  Stream Beads   (GPIO5):  {config.NUM_PIXELS_STREAM} pixels @ {config.BRIGHTNESS:.2f} brightness")

    print("\n[I2C BUS]")
    print(f"  SDA: GPIO8")
    print(f"  SCL: GPIO9")
    if config.ENABLE_MOTION:
        print(f"  PCA9685 #1 (Motion):     0x{config.PCA9685_ADDR1:02X}")
        print(f"  PCA9685 #2 (Vapor/PWM):  0x{config.PCA9685_ADDR2:02X}")

    print("\n[AUDIO]")
    if config.ENABLE_AUDIO_UART:
        print(f"  UART TX (GPIO17):  Tsunami RXI")
        print(f"  UART RX (GPIO18):  Tsunami TXO @ {config.AUDIO_UART_BAUDRATE} baud")
    if config.ENABLE_AUDIO_I2C:
        print(f"  I2C Address:       0x{config.AUDIO_I2C_ADDR:02X} (WAV Trigger Pro)")

    print("\n[RELAYS]")
    print(f"  Fogger      (GPIO39):  {config.FOGGER_RELAY_PIN}")
    print(f"  Chimney 1   (GPIO42):  {config.CHIMNEY_RELAY_PIN1}")
    print(f"  Chimney 2   (GPIO41):  {config.CHIMNEY_RELAY_PIN2}")
    print(f"  Chimney 3   (GPIO40):  {config.CHIMNEY_RELAY_PIN3}")

    print("\n[MODULE STATUS]")
    print(f"  ENABLE_LIGHTING:    {config.ENABLE_LIGHTING}")
    print(f"  ENABLE_MOTION:      {config.ENABLE_MOTION}")
    print(f"  ENABLE_AUDIO:       {config.ENABLE_AUDIO}")
    print(f"  ENABLE_ATMOSPHERE:  {config.ENABLE_ATMOSPHERE}")
    print(f"  ENABLE_WEB:         {config.ENABLE_WEB}")

    print("\n" + "=" * 70)
    print("VALIDATION COMPLETE — Verify physical wiring matches above layout")
    print("=" * 70 + "\n")


# ============================================================================
# SETUP
# ============================================================================

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
    Linearly increase volume from -70dB to +10dB over ~30 seconds.
    """
    print("-" * 60)
    print("PHASE 1: GRADUAL VOLUME RAMP (30 seconds)")
    print("-" * 60)
    print()
    
    track_id = 22
    output_channel = 0  # 1L left channel
    
    # Pre-set output to silent (-70dB) before starting playback
    tsunami.set_output_gain(output_channel, -70)
    
    print(f"Starting track {track_id} on output {output_channel} (1L)...")
    if not tsunami.track_play_routed(track_id, output_channel):
        print("✗ Failed to start playback")
        return False
    
    time.sleep(0.5)  # Allow track to start
    
    print("Ramping volume from -70dB to +10dB...")
    print()
    
    # Ramp volume in 5dB steps over ~30 seconds
    # Total steps: 17 (-70 to +10 by 5)
    # Time per step: 30 sec / 16 jumps ≈ 1.875 sec
    step_size = 5
    delay_per_step = 1.875  # seconds
    
    for gain in range(-70, 11, step_size):
        if tsunami.set_output_gain(output_channel, gain):
            # Calculate a rough percentage mapped from the -70 to +10 range
            percent = ((gain + 70) / 80.0) * 100
            print(f"Volume: {gain:3d} dB ({percent:5.1f}%)")
            time.sleep(delay_per_step)
        else:
            print(f"✗ Failed to set gain to {gain} dB")
            break
            
    print()
    print("✓ Phase 1 complete")
    print()


def test_stepwise_volume_levels():
    """
    Phase 2: Stepwise volume levels
    Hold at 5 discrete levels. Each level held for 2 seconds.
    """
    print("-" * 60)
    print("PHASE 2: STEPWISE VOLUME LEVELS (5 steps × 2 sec = 10 seconds)")
    print("-" * 60)
    print()
    
    output_channel = 0  # 1L left channel
    
    # Define 5 step levels using the dB scale
    steps = [
        (-70, "0%   (Silent)"),
        (-35, "25%  (Quiet)"),
        (-15, "50%  (Medium)"),
        (0,   "75%  (Reference)"),
        (10,  "100% (Maximum)")
    ]
    
    hold_time = 2.0  # seconds per step
    
    for gain_value, label in steps:
        if tsunami.set_output_gain(output_channel, gain_value):
            print(f"Step: {label} (gain={gain_value:3d} dB)")
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
    
    # Set volume back to silent before stopping
    output_channel = 0
    print("Stopping audio and resetting gain to -70dB...")
    tsunami.set_output_gain(output_channel, -70)
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