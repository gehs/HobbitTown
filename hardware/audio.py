"""
audio.py - Testable audio control path for HobbitTown.

Current project state:
- Full waveform playback is not implemented yet.
- This module provides a hardware-test mode by driving PCA9685 speaker-control
  channels via hardware.motion.set_speaker().
"""
import time
import hardware.motion as motion

# Active playback state for test mode
_audio_ready = False
_current_channel = None
_current_level_channel = None
_current_level_value = 0
_looping = False
_stop_at = 0.0


def _track_to_digital_channel(track):
    """Map arbitrary track IDs to speaker control channels 8-11."""
    safe_track = int(track) if int(track) > 0 else 1
    return 8 + ((safe_track - 1) % 4)


def _player_to_level_channel(player):
    """Player 1 -> channel 12, player 2 -> channel 13."""
    return 12 if int(player) == 1 else 13


def _track_to_duration_seconds(track):
    """Short deterministic durations for bench validation."""
    safe_track = int(track) if int(track) > 0 else 1
    return 1.5 + (safe_track % 4) * 0.5


def _stop_all_channels():
    """Force all speaker-control channels to OFF/0."""
    for ch in (8, 9, 10, 11, 12, 13):
        motion.set_speaker(ch, 0)


def setup_audio():
    """Initialize audio test control mode."""
    global _audio_ready

    _stop_all_channels()
    _audio_ready = bool(getattr(motion, "hardware_ready", False))

    if _audio_ready:
        print("Audio: PCA9685 test mode ready (channels 8-13)")
    else:
        print("Audio: dry-load mode (motion/PCA9685 not ready)")


def play_audio(player, track, loop=False):
    """Drive speaker control channels in a non-blocking test pattern."""
    global _current_channel, _current_level_channel, _current_level_value, _looping, _stop_at

    # Always log intent so UI/testing remains informative in dry-load mode.
    mode = "looping" if loop else "one-shot"
    print(f"Audio: Playing track {track} ({mode})")

    if not _audio_ready:
        return

    # Stop any previous playback pattern before starting a new one.
    _stop_all_channels()

    digital_channel = _track_to_digital_channel(track)
    level_channel = _player_to_level_channel(player)

    # Digital gate ON, level set to medium-high for visible scope/meter response.
    level_value = 180
    motion.set_speaker(digital_channel, 255)
    motion.set_speaker(level_channel, level_value)

    _current_channel = digital_channel
    _current_level_channel = level_channel
    _current_level_value = level_value
    _looping = bool(loop)
    _stop_at = time.monotonic() + _track_to_duration_seconds(track)


def run_audio_cycle():
    """Non-blocking update cycle for audio test mode."""
    global _stop_at

    if not _audio_ready or _current_channel is None:
        return

    now = time.monotonic()
    if _looping:
        # Keep channels active while loop is requested.
        motion.set_speaker(_current_channel, 255)
        motion.set_speaker(_current_level_channel, _current_level_value)
        return

    if now >= _stop_at:
        _stop_all_channels()
        _clear_state()


def _clear_state():
    """Clear active playback state."""
    global _current_channel, _current_level_channel, _current_level_value, _looping, _stop_at
    _current_channel = None
    _current_level_channel = None
    _current_level_value = 0
    _looping = False
    _stop_at = 0.0


# Convenience functions for soundscape/scene integration
def play_daytime():
    """Play daytime ambience."""
    play_audio(1, 1, loop=True)


def play_sunset_sfx():
    """Play sunset sound effects."""
    play_audio(1, 2, loop=False)


def play_nighttime():
    """Play nighttime ambience."""
    play_audio(2, 3, loop=True)


def play_dragon_event():
    """Play dragon event audio."""
    play_audio(1, 9, loop=False)


def play_party_music():
    """Play party music."""
    play_audio(2, 5, loop=True)
