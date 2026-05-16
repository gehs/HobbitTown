import json
import time

import config
from hardware import atmosphere
from hardware import audio
from hardware import lighting_ground
from hardware import lighting_sky
from hardware import lighting_stream
from hardware import motion


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

    for channel in (12, 13):
        motion.set_speaker(channel, 0)

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
    """Check Tsunami output-to-track-range rules from config.py."""
    if output_number < 1 or output_number > config.AUDIO_OUTPUT_COUNT:
        return False, "invalid output number"

    if not getattr(config, "ENFORCE_AUDIO_OUTPUT_TRACK_RANGES", False):
        return True, "range enforcement disabled"

    track = int(track_number)
    low, high = config.AUDIO_TRACK_RANGES_BY_OUTPUT[output_number - 1]
    if low <= track <= high:
        return True, "ok"
    return False, "track outside output range"


def play_track_checked(output_number, track_number, loop=False):
    ok, reason = validate_track_for_output(output_number, track_number)
    if not ok:
        print(
            "[TEST:audio] SKIP output",
            output_number,
            "track",
            track_number,
            "reason:",
            reason,
        )
        return False

    # Current audio module sends play command by track; output-number verification
    # is enforced here to keep test assignments aligned with Tsunami planning.
    audio.play_audio(output_number, int(track_number), loop=loop)
    return True


def pulse_exciter_channels(elapsed_s):
    """Simple non-blocking pulse pattern for PCA9685 exciter channels 12 and 13."""
    if elapsed_s < 1.0:
        motion.set_speaker(12, 255)
        motion.set_speaker(13, 0)
    elif elapsed_s < 2.0:
        motion.set_speaker(12, 0)
        motion.set_speaker(13, 255)
    else:
        motion.set_speaker(12, 0)
        motion.set_speaker(13, 0)


def monotonic_now():
    return time.monotonic()
