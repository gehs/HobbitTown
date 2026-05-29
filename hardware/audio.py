"""UART-only Tsunami Super WAV Trigger support.

This module intentionally excludes I2C and direct trigger modes.
"""

import time
import busio
import config
from hardware import tsunami_protocol

uart = None
audio_ready = False
uart_ready = False

AUDIO_TRACK_DAYTIME = getattr(config, "AUDIO_TRACK_DAYTIME", None)
AUDIO_TRACK_SUNSET = getattr(config, "AUDIO_TRACK_SUNSET", None)
AUDIO_TRACK_NIGHTTIME = getattr(config, "AUDIO_TRACK_NIGHTTIME", None)
AUDIO_TRACK_DRAGON_EVENT = getattr(config, "AUDIO_TRACK_DRAGON_EVENT", None)
AUDIO_TRACK_PARTY_MUSIC = getattr(config, "AUDIO_TRACK_PARTY_MUSIC", None)
DEFAULT_OUTPUT_INDEX = getattr(config, "AUDIO_DEFAULT_OUTPUT_INDEX", 0)


def setup_audio():
    """Initialize Tsunami UART transport."""
    global uart, audio_ready, uart_ready

    if not getattr(config, "ENABLE_AUDIO", False):
        print("Audio: disabled in config")
        return

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
            print("Audio: UART initialized for Tsunami")
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

    if not audio_ready:
        print("Audio: initialized (UART unavailable)")


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


def _get_default_output_index():
    try:
        return tsunami_protocol.output_number_to_index(DEFAULT_OUTPUT_INDEX + 1)
    except Exception:
        print("Audio: invalid AUDIO_DEFAULT_OUTPUT_INDEX; using 0")
        return 0


def _play_track_uart(track, loop=False):
    output_index = _get_default_output_index()
    play_command = tsunami_protocol.build_control_track_for_index(
        track_number=track,
        output_index=output_index,
        control_code=tsunami_protocol.PLAY_POLY,
        lock_voice=False,
    )

    ok = _send_uart_command(play_command)

    if ok and loop:
        loop_command = tsunami_protocol.build_control_track_for_index(
            track_number=track,
            output_index=output_index,
            control_code=tsunami_protocol.LOOP_ON,
            lock_voice=False,
        )
        ok = _send_uart_command(loop_command)

    if ok:
        print(f"Audio: UART playback command sent for track {track}")
    else:
        print(f"Audio: failed to send UART command for track {track}")


def play_audio(player, track, loop=False):
    if uart_ready:
        _play_track_uart(track, loop=loop)
        return

    mode = "looping" if loop else "one-shot"
    print(f"Audio: UART unavailable for track {track} ({mode})")


def run_audio_cycle():
    # No periodic work required for UART-only mode.
    return


def _play_named_track(name, track_number):
    if track_number is None:
        print(f"Audio: {name} track not configured")
        return

    if uart_ready:
        _play_track_uart(track_number)
        return

    print(f"Audio: ♪ {name}")


def get_status():
    status = {
        "enabled": getattr(config, "ENABLE_AUDIO", False),
        "uart_enabled": getattr(config, "ENABLE_AUDIO_UART", False),
        "uart_ready": uart_ready,
        "uart_tx": str(getattr(config, "AUDIO_UART_TX", None)),
        "uart_rx": str(getattr(config, "AUDIO_UART_RX", None)),
        "default_output_index": _get_default_output_index(),
    }
    if uart_ready:
        status["device_info"] = _query_uart(b"v\r", timeout=0.2)
    else:
        status["device_info"] = None
    return status


def play_daytime():
    _play_named_track("Daytime ambience", AUDIO_TRACK_DAYTIME)


def play_sunset_sfx():
    _play_named_track("Sunset SFX", AUDIO_TRACK_SUNSET)


def play_nighttime():
    _play_named_track("Nighttime ambience", AUDIO_TRACK_NIGHTTIME)


def play_dragon_event():
    _play_named_track("Dragon event", AUDIO_TRACK_DRAGON_EVENT)


def play_party_music():
    _play_named_track("Party music", AUDIO_TRACK_PARTY_MUSIC)


def _clamp_gain_db(gain_db):
    gain = int(gain_db)
    if gain < tsunami_protocol.TSUNAMI_MIN_GAIN_DB:
        return tsunami_protocol.TSUNAMI_MIN_GAIN_DB
    if gain > tsunami_protocol.TSUNAMI_MAX_GAIN_DB:
        return tsunami_protocol.TSUNAMI_MAX_GAIN_DB
    return gain


def _gain_byte_to_db(gain_value):
    """Map legacy 0-255 gain scale to Tsunami signed dB range (-70..+10)."""
    byte_val = int(gain_value)
    if byte_val < 0 or byte_val > 255:
        raise ValueError("gain byte must be 0-255")
    scaled = -70 + (byte_val * 80.0 / 255.0)
    return _clamp_gain_db(round(scaled))


def _set_output_gain_uart(output_channel, gain_db):
    """
    Send gain control command via UART to Tsunami.
    
    Args:
        output_channel: Output 0-7
        gain_db: Signed dB value (-70 to +10)
    """
    if uart is None:
        return False
    packet = tsunami_protocol.build_output_volume_for_index(output_channel, _clamp_gain_db(gain_db))
    
    return _send_uart_command(packet)


def set_output_gain(output_channel, gain_value):
    """
    Set output volume gain for a Tsunami UART output.
    
    Args:
        output_channel: Output number (0-7)
        gain_value:
            - preferred signed dB (-70 to +10)
            - compatibility byte scale (0-255), converted to dB
    
    Returns:
        True if command sent successfully, False otherwise
    """
    if not (0 <= output_channel <= 7):
        print(f"Audio: Invalid output channel {output_channel}")
        return False

    try:
        gain_raw = int(gain_value)
    except Exception:
        print(f"Audio: Invalid gain value {gain_value}")
        return False

    if -70 <= gain_raw <= 10:
        gain_db = _clamp_gain_db(gain_raw)
    elif 0 <= gain_raw <= 255:
        gain_db = _gain_byte_to_db(gain_raw)
    else:
        print("Audio: Invalid gain value (must be -70..+10 dB or 0..255 byte scale)")
        return False

    if uart_ready:
        if _set_output_gain_uart(output_channel, gain_db):
            print(f"Audio: UART gain set to {gain_db} dB on output {output_channel}")
            return True
        else:
            print(f"Audio: Failed to set UART gain on output {output_channel}")
            return False
    
    print("Audio: UART not ready for gain control")
    return False


def stop_all():
    """Stop all active Tsunami tracks via UART."""
    if not uart_ready:
        print("Audio: UART not ready for stop_all")
        return False

    packet = tsunami_protocol.build_stop_all()
    if _send_uart_command(packet):
        print("Audio: stop_all command sent")
        return True

    print("Audio: failed to send stop_all command")
    return False
