"""
Audio hardware support for the WAV Trigger.
Supports Qwiic/I2C command mode, UART command mode, and optional direct trigger outputs.
"""

import time
import busio
import digitalio
import config

uart = None
i2c = None
audio_ready = False
uart_ready = False
i2c_ready = False
trigger_1 = None
trigger_2 = None
trigger_ready = False
_trigger_pulse_state = None

# I2C command bytes follow the WAV Trigger Pro Qwiic command set.
CMD_GET_VERSION = 1
CMD_GET_NUM_TRACKS = 2
CMD_TRACK_PLAY_POLY = 3
CMD_GET_TRACK_STATUS = 4
CMD_GET_NUM_ACTIVE_VOICES = 5
CMD_TRACK_SET_LOOP = 6
CMD_TRACK_SET_LOCK = 7
CMD_STOP_ALL = 8
CMD_TRACK_STOP = 9
CMD_TRACK_FADE = 10
CMD_MIDI_MSG = 11
CMD_LOAD_PRESET = 12
CMD_SET_OUTPUT_GAIN = 13
RESPONSE_DELAY_SEC = 0.002


def setup_audio():
    """Initialize audio hardware support."""
    global uart, i2c, audio_ready, uart_ready, i2c_ready, trigger_1, trigger_2, trigger_ready

    if not getattr(config, "ENABLE_AUDIO", False):
        print("Audio: disabled in config")
        return

    if getattr(config, "ENABLE_AUDIO_I2C", False):
        try:
            from hardware import motion as motion_hw
            i2c_source = None
            if getattr(config, "ENABLE_MOTION", False) and getattr(motion_hw, "i2c", None) is not None:
                i2c_source = motion_hw.i2c
                print("Audio: reusing motion I2C bus for WAV Trigger Pro")
            else:
                i2c_source = busio.I2C(config.I2C_SCL, config.I2C_SDA)

            i2c = i2c_source
            i2c_ready = _i2c_device_present()
            audio_ready = i2c_ready
            if i2c_ready:
                print(f"Audio: I2C initialized for WAV Trigger Pro at 0x{config.AUDIO_I2C_ADDR:02X}")
            else:
                raise RuntimeError("WAV Trigger Pro not found on I2C bus")
        except Exception as exc:
            i2c = None
            i2c_ready = False
            audio_ready = False
            if getattr(config, "ALLOW_MISSING_HARDWARE", False):
                print(f"Audio: I2C dry-load mode ({exc})")
            else:
                raise
    else:
        print("Audio: I2C mode disabled")

    if getattr(config, "ENABLE_AUDIO_UART", False):
        try:
            uart = busio.UART(
                tx=config.AUDIO_UART_TX,
                rx=config.AUDIO_UART_RX,
                baudrate=config.AUDIO_UART_BAUDRATE,
                timeout=config.AUDIO_UART_TIMEOUT,
            )
            uart_ready = True
            audio_ready = audio_ready or uart_ready
            print("Audio: UART initialized for WAV Trigger")
            _drain_uart()
        except Exception as exc:
            uart = None
            uart_ready = False
            if getattr(config, "ALLOW_MISSING_HARDWARE", False):
                print(f"Audio: UART dry-load mode ({exc})")
            else:
                raise
    else:
        print("Audio: UART mode disabled")

    if getattr(config, "ENABLE_AUDIO_TRIGGERS", False):
        try:
            trigger_1 = digitalio.DigitalInOut(config.AUDIO_TRIGGER_1_PIN)
            trigger_1.direction = digitalio.Direction.OUTPUT
            trigger_1.value = not config.AUDIO_TRIGGER_ACTIVE_LOW

            trigger_2 = digitalio.DigitalInOut(config.AUDIO_TRIGGER_2_PIN)
            trigger_2.direction = digitalio.Direction.OUTPUT
            trigger_2.value = not config.AUDIO_TRIGGER_ACTIVE_LOW

            trigger_ready = True
            print("Audio: direct trigger pins initialized for WAV Trigger")
        except Exception as exc:
            trigger_1 = None
            trigger_2 = None
            trigger_ready = False
            if getattr(config, "ALLOW_MISSING_HARDWARE", False):
                print(f"Audio: trigger dry-load mode ({exc})")
            else:
                raise
    else:
        print("Audio: direct trigger pins disabled")

    if not audio_ready and not trigger_ready:
        print("Audio: initialized (no WAV Trigger hardware enabled)")


def _i2c_device_present():
    if i2c is None:
        return False
    try:
        if i2c.try_lock():
            try:
                return config.AUDIO_I2C_ADDR in i2c.scan()
            finally:
                i2c.unlock()
        return False
    except Exception as exc:
        print(f"Audio: I2C scan failed ({exc})")
        return False


def _drain_uart():
    if uart is None:
        return
    while True:
        data = uart.read(32)
        if not data:
            break


def _send_uart_command(command_bytes):
    if uart is None:
        return False
    try:
        uart.write(command_bytes)
        return True
    except Exception as exc:
        print(f"Audio: UART write failed ({exc})")
        return False


def _send_i2c_command(command_bytes):
    if i2c is None:
        return False
    try:
        if i2c.try_lock():
            try:
                i2c.writeto(config.AUDIO_I2C_ADDR, command_bytes)
            finally:
                i2c.unlock()
        else:
            print("Audio: I2C bus busy")
            return False
        return True
    except Exception as exc:
        print(f"Audio: I2C write failed ({exc})")
        return False


def _query_i2c_bytes(command_bytes, length):
    if i2c is None:
        return None
    try:
        if i2c.try_lock():
            try:
                i2c.writeto(config.AUDIO_I2C_ADDR, command_bytes)
                time.sleep(RESPONSE_DELAY_SEC)
                response = bytearray(length)
                i2c.readfrom_into(config.AUDIO_I2C_ADDR, response)
            finally:
                i2c.unlock()
        else:
            print("Audio: I2C bus busy")
            return None
        return bytes(response)
    except Exception as exc:
        print(f"Audio: I2C query failed ({exc})")
        return None


def _query_uart(command_bytes, timeout=0.2):
    if uart is None:
        return None
    try:
        uart.write(command_bytes)
    except Exception as exc:
        print(f"Audio: UART query write failed ({exc})")
        return None

    deadline = time.monotonic() + timeout
    response = b""
    while time.monotonic() < deadline:
        data = uart.read(64)
        if data:
            response += data
            if b"\r" in response or b"\n" in response:
                break
    if not response:
        return None
    try:
        return response.decode("ascii", errors="replace").strip()
    except Exception:
        return None


def _format_play_command(track, loop=False):
    track_number = int(track)
    if loop:
        return f"P{track_number:03d}\r".encode("ascii")
    return f"p{track_number:03d}\r".encode("ascii")


def _play_track_uart(track, loop=False):
    command = _format_play_command(track, loop=loop)
    if _send_uart_command(command):
        print(f"Audio: UART playback command sent for track {track}")
    else:
        print(f"Audio: failed to send UART command for track {track}")


def _play_track_i2c(track, loop=False):
    track_number = int(track)
    flags = 0x01 if loop else 0x00
    gain = 0
    balance = 64
    attack = 0
    cents = 0

    txbuf = bytearray(11)
    txbuf[0] = CMD_TRACK_PLAY_POLY
    txbuf[1] = track_number & 0xFF
    txbuf[2] = (track_number >> 8) & 0xFF
    txbuf[3] = gain & 0xFF
    txbuf[4] = (gain >> 8) & 0xFF
    txbuf[5] = balance & 0xFF
    txbuf[6] = attack & 0xFF
    txbuf[7] = (attack >> 8) & 0xFF
    txbuf[8] = cents & 0xFF
    txbuf[9] = (cents >> 8) & 0xFF
    txbuf[10] = flags

    if _send_i2c_command(txbuf):
        print(f"Audio: I2C playback command sent for track {track}")
    else:
        print(f"Audio: failed to send I2C playback command for track {track}")


def _try_trigger_play(track):
    if not trigger_ready:
        return False

    if int(track) == getattr(config, "AUDIO_TRIGGER_1_TRACK", 1):
        _pulse_trigger(trigger_1)
        return True
    if int(track) == getattr(config, "AUDIO_TRIGGER_2_TRACK", 2):
        _pulse_trigger(trigger_2)
        return True
    return False


def _pulse_trigger(pin):
    global _trigger_pulse_state
    if pin is None:
        return

    active_value = not config.AUDIO_TRIGGER_ACTIVE_LOW
    idle_value = config.AUDIO_TRIGGER_ACTIVE_LOW
    pin.value = active_value
    _trigger_pulse_state = {
        "pin": pin,
        "idle_value": idle_value,
        "release_at": time.monotonic() + (config.AUDIO_TRIGGER_PULSE_MS / 1000.0),
    }
    print("Audio: trigger pin pulsed for WAV Trigger")


def _update_trigger_pulse():
    global _trigger_pulse_state
    if _trigger_pulse_state is None:
        return

    if time.monotonic() >= _trigger_pulse_state["release_at"]:
        _trigger_pulse_state["pin"].value = _trigger_pulse_state["idle_value"]
        _trigger_pulse_state = None


def play_audio(player, track, loop=False):
    if i2c_ready:
        _play_track_i2c(track, loop=loop)
        return

    if uart_ready:
        _play_track_uart(track, loop=loop)
        return

    if _try_trigger_play(track):
        return

    mode = "looping" if loop else "one-shot"
    print(f"Audio: Playing track {track} ({mode})")


def run_audio_cycle():
    _update_trigger_pulse()


def _play_named_track(name, track_number):
    if track_number is None:
        print(f"Audio: {name} track not configured")
        return

    if i2c_ready:
        _play_track_i2c(track_number)
        return

    if uart_ready:
        _play_track_uart(track_number)
        return

    if _try_trigger_play(track_number):
        return

    print(f"Audio: ♪ {name}")


def get_status():
    status = {
        "enabled": getattr(config, "ENABLE_AUDIO", False),
        "i2c_enabled": getattr(config, "ENABLE_AUDIO_I2C", False),
        "i2c_ready": i2c_ready,
        "i2c_addr": hex(config.AUDIO_I2C_ADDR),
        "i2c_sda": str(config.I2C_SDA),
        "i2c_scl": str(config.I2C_SCL),
        "uart_enabled": getattr(config, "ENABLE_AUDIO_UART", False),
        "uart_ready": uart_ready,
        "trigger_enabled": getattr(config, "ENABLE_AUDIO_TRIGGERS", False),
        "trigger_ready": trigger_ready,
        "uart_tx": str(config.AUDIO_UART_TX),
        "uart_rx": str(config.AUDIO_UART_RX),
        "trigger_1_pin": str(config.AUDIO_TRIGGER_1_PIN),
        "trigger_2_pin": str(config.AUDIO_TRIGGER_2_PIN),
        "trigger_1_track": config.AUDIO_TRIGGER_1_TRACK,
        "trigger_2_track": config.AUDIO_TRIGGER_2_TRACK,
    }
    if i2c_ready:
        version_bytes = _query_i2c_bytes(bytearray([CMD_GET_VERSION]), 12)
        if version_bytes is not None:
            status["device_info"] = version_bytes.decode("ascii", errors="replace").rstrip("\x00\r\n")
        else:
            status["device_info"] = None
    elif uart_ready:
        status["device_info"] = _query_uart(b"v\r", timeout=0.2)
    else:
        status["device_info"] = None
    return status


def play_daytime():
    _play_named_track("Daytime ambience", config.AUDIO_TRACK_DAYTIME)


def play_sunset_sfx():
    _play_named_track("Sunset SFX", config.AUDIO_TRACK_SUNSET)


def play_nighttime():
    _play_named_track("Nighttime ambience", config.AUDIO_TRACK_NIGHTTIME)


def play_dragon_event():
    _play_named_track("Dragon event", config.AUDIO_TRACK_DRAGON_EVENT)


def play_party_music():
    _play_named_track("Party music", config.AUDIO_TRACK_PARTY_MUSIC)


def _set_output_gain_uart(output_channel, gain_value):
    """
    Send gain control command via UART to Tsunami.
    
    Args:
        output_channel: Output 0-7
        gain_value: Gain level 0-255
    """
    if uart is None:
        return False
    
    gain_lsb = gain_value & 0xFF
    gain_msb = (gain_value >> 8) & 0xFF
    
    packet = bytearray([
        0xF0,                    # Start of Message 1
        0xAA,                    # Start of Message 2
        0x05,                    # Length of message
        0x0D,                    # Command: Set Output Gain (13)
        output_channel,          # Output channel (0-7)
        gain_lsb,                # Gain value LSB
        gain_msb,                # Gain value MSB
        0x55                     # End of Message
    ])
    
    return _send_uart_command(packet)


def _set_output_gain_i2c(output_channel, gain_value):
    """
    Send gain control command via I2C to WAV Trigger Pro.
    
    Args:
        output_channel: Output channel
        gain_value: Gain level 0-255
    """
    if i2c is None:
        return False
    
    txbuf = bytearray(3)
    txbuf[0] = CMD_SET_OUTPUT_GAIN
    txbuf[1] = output_channel & 0xFF
    txbuf[2] = gain_value & 0xFF
    
    return _send_i2c_command(txbuf)


def set_output_gain(output_channel, gain_value):
    """
    Set output volume gain for a specific Tsunami/WAV Trigger output.
    
    Args:
        output_channel: Output number (0-7)
        gain_value: Gain level (0-255, where 0=silent, 255=max)
    
    Returns:
        True if command sent successfully, False otherwise
    """
    if not (0 <= output_channel <= 7):
        print(f"Audio: Invalid output channel {output_channel}")
        return False
    
    if not (0 <= gain_value <= 255):
        print(f"Audio: Invalid gain value {gain_value} (must be 0-255)")
        return False
    
    if i2c_ready:
        if _set_output_gain_i2c(output_channel, gain_value):
            print(f"Audio: I2C gain set to {gain_value} on output {output_channel}")
            return True
        else:
            print(f"Audio: Failed to set I2C gain on output {output_channel}")
            return False
    
    if uart_ready:
        if _set_output_gain_uart(output_channel, gain_value):
            print(f"Audio: UART gain set to {gain_value} on output {output_channel}")
            return True
        else:
            print(f"Audio: Failed to set UART gain on output {output_channel}")
            return False
    
    print("Audio: No audio device ready for gain control")
    return False
