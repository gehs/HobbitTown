import json
import time

import config
from hardware import atmosphere
from hardware import audio
from hardware import lighting_ground
from hardware import lighting_sky
from hardware import lighting_stream
from hardware import motion
from tests.modular_dry_run import Convert_for_Tsunami as cft


MIN_TSUNAMI_TRACK = 1
MAX_TSUNAMI_TRACK = 4096


def tsunami_control_track_poly(track_number, output_number=1, lock_voice=False):
    """Compatibility wrapper around centralized Tsunami converter."""
    return cft.build_control_track(
        track_number=track_number,
        output_number=output_number,
        control_code=cft.PLAY_POLY,
        lock_voice=lock_voice,
    )


def tsunami_stop_all():
    """Compatibility wrapper around centralized Tsunami converter."""
    return cft.build_stop_all()


def setup_shared_hardware():
    """Initialize all subsystems used by modular dry-run tests."""
    lighting_ground.setup_lighting_ground()
    lighting_stream.setup_lighting_stream()
    lighting_sky.setup_lighting_sky()
    motion.setup_hardware()
    audio.setup_audio()
    atmosphere.setup_atmosphere()


def safe_shutdown():
    """Return hardware to safe defaults after each modular test."""
    motion.set_door(1, 90)
    motion.set_door(2, 90)
    motion.set_door(3, 90)

    if atmosphere.fogger_relay is not None:
        atmosphere.fogger_relay.value = True

    # Stop Tsunami playback as part of safe shutdown for audio-routed exciters.
    try:
        if audio.uart is not None:
            audio.uart.write(tsunami_stop_all())
    except Exception as exc:
        print("[TEST:audio] failed to send STOP_ALL during shutdown: %s" % exc)

    lighting_ground.set_all_lights_off_ground()
    lighting_stream.set_all_lights_off_stream()
    lighting_sky.set_all_lights_off_sky()


def load_segment_map():
    segment_map = {}
    try:
        with open("lights.json", "r") as f:
            data = json.load(f)
        for strip_name in ("strip_ground_effects", "strip_water_effects", "strip_sky_arc", "strip_standard_ws2812b"):
            for segment in data.get(strip_name, {}).get("segments", []):
                segment_map[segment["id"]] = tuple(segment["range"])
    except Exception as exc:
        print("[TEST:common] failed to load lights.json", exc)
    return segment_map


def set_ground_segments(segment_map, segment_ids, rgb):
    if lighting_ground.pixels is None:
        return

    r = int(rgb[0] * config.BRIGHTNESS)
    g = int(rgb[1] * config.BRIGHTNESS)
    b = int(rgb[2] * config.BRIGHTNESS)

    for seg_id in segment_ids:
        seg = segment_map.get(seg_id)
        if seg is None:
            continue
        start, end = seg
        for i in range(start, end + 1):
            lighting_ground.pixels[i] = (r, g, b)
    lighting_ground.pixels.show()


def validate_track_for_output(output_number, track_number):
    """Validate output number and track ID for modular dry-run tests.

    Any track 1..4096 can route to any mono output 1..8.
    """
    if output_number < 1 or output_number > config.AUDIO_OUTPUT_COUNT:
        return False, "invalid output number"

    track = int(track_number)
    if MIN_TSUNAMI_TRACK <= track <= MAX_TSUNAMI_TRACK:
        return True, "ok"
    return False, "track outside allowed modular-test range 1..4096"


def play_track_checked(output_number, track_number, loop=False):
    """Send Tsunami CONTROL_TRACK command with binary frame encoding.
    
    Args:
        output_number: 1-8 (user-facing; converted to 0-7 index internally)
        track_number: 1-4096
        loop: ignored in this implementation (uses PLAY_POLY)
    
    Returns:
        bool: True if command sent, False if validation failed
    """
    ok, reason = validate_track_for_output(output_number, track_number)
    if not ok:
        print("[TEST:audio] SKIP output %d track %d reason: %s" % (output_number, track_number, reason))
        return False
    
    try:
        # Build binary Tsunami frame with proper little-endian encoding.
        cmd = tsunami_control_track_poly(track_number, output_number=output_number, lock_voice=False)
        info = cft.describe_control_track(track_number, output_number)
        
        # Send via UART if available.
        if audio.uart is not None:
            audio.uart.write(cmd)
            print(
                "[TEST:audio] sent CONTROL_TRACK output %d (index %d) track %d "
                "(LE %02X %02X) frame: %s"
                % (
                    info["output_number"],
                    info["output_index"],
                    info["track_number"],
                    info["track_lsb"],
                    info["track_msb"],
                    cmd.hex(),
                )
            )
            return True
        else:
            print("[TEST:audio] UART not initialized; cannot send command")
            return False
    except Exception as exc:
        print("[TEST:audio] failed to send command for output %d track %d: %s" % (output_number, track_number, exc))
        return False


def monotonic_now():
    return time.monotonic()
