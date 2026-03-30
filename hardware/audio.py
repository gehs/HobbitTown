"""
audio.py - Audio placeholder module
No hardware audio playback implemented (DFPlayer removed).
Provides stubs for all audio functions used by soundscape and scenes.
Future: Replace with actual audio playback via MAX98357 or similar I2S amplifier.
"""
import time


def setup_audio():
    """Initialize audio system (stub)."""
    print("Audio: Initialized (no hardware audio - using stubs)")


def play_audio(player, track, loop=False):
    """
    Stub for playing audio via specified player.
    Args:
        player: Player ID (1 or 2, for compatibility)
        track: Track number
        loop: Whether to loop playback
    """
    mode = "looping" if loop else "one-shot"
    print(f"Audio: Playing track {track} ({mode})")


def run_audio_cycle():
    """
    Non-blocking audio update cycle (stub).
    Placeholder for future continuous audio logic.
    """
    pass


# Convenience functions for soundscape/scene integration
def play_daytime():
    """Play daytime ambience (stub)."""
    print("Audio: ♪ Daytime ambience")


def play_sunset_sfx():
    """Play sunset sound effects (stub)."""
    print("Audio: ♪ Sunset SFX")


def play_nighttime():
    """Play nighttime ambience (stub)."""
    print("Audio: ♪ Nighttime ambience")


def play_dragon_event():
    """Play dragon event audio (stub)."""
    print("Audio: ♪ Dragon event")


def play_party_music():
    """Play party music (stub)."""
    print("Audio: ♪ Party music")
