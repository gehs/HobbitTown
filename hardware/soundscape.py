"""
Soundscape Manager for HobbitTown Diorama.
Non-blocking audio control for complex multi-layer soundscapes.
"""
import time
import random
import config

class SoundscapeManager:
    """Manages time-based soundscape transitions and audio layer control."""
    
    def __init__(self):
        self.start_time = None
        self.is_playing = False
        self.current_soundscape = None
        self.current_layer_volumes = {}
        self.last_event_time = {}
    
    def setup_soundscape(self, soundscape_name="default"):
        """Initialize soundscape playback."""
        self.current_soundscape = soundscape_name
        self.start_time = time.monotonic()
        self.is_playing = True
        print(f"Soundscape: Initialized '{soundscape_name}'")
    
    def stop_soundscape(self):
        """Stop current soundscape."""
        self.is_playing = False
        self.start_time = None
        print("Soundscape: Stopped")
    
    def run_soundscape_cycle(self, current_hour=None):
        """
        Non-blocking soundscape update cycle.
        Should be called repeatedly in main loop.
        """
        if not self.is_playing or self.start_time is None:
            return
        
        elapsed = time.monotonic() - self.start_time
        
        # Dispatch to appropriate soundscape handler
        if self.current_soundscape == "shire_spring_dawn":
            self._run_shire_spring_dawn(elapsed)
        elif self.current_soundscape == "shire_summer_thunderstorm":
            self._run_shire_summer_thunderstorm(elapsed)
    
    def _run_shire_spring_dawn(self, elapsed):
        """
        Shire Spring Dawn soundscape (4:00 AM - 6:30 AM).
        Progressive layering of natural sounds with timed events.
        """
        # Timeline progression (in seconds from 4:00 AM)
        # 0s = 4:00 AM, 9000s = 6:30 AM
        
        if elapsed < 300:  # 4:00–4:05 AM
            self.current_layer_volumes = {'birds': 0.05, 'stream': 0.0, 'wind': 0.0}
        elif elapsed < 1800:  # 4:05–4:30 AM
            progress = (elapsed - 300) / 1500.0
            self.current_layer_volumes = {
                'birds': 0.05 + (0.15 * progress),
                'stream': 0.0,
                'wind': 0.0
            }
        elif elapsed < 3000:  # 4:30–5:00 AM
            progress = (elapsed - 1800) / 1200.0
            self.current_layer_volumes = {
                'birds': 0.20 + (0.15 * progress),
                'stream': 0.0 + (0.25 * progress),
                'wind': 0.0 + (0.10 * progress)
            }
        elif elapsed < 3300:  # 5:00–5:05 AM
            self.current_layer_volumes = {
                'birds': 0.35,
                'stream': 0.25,
                'wind': 0.10
            }
            # Trigger rooster around 5:15 AM mark
            if 900 < elapsed < 920:
                self._trigger_event('rooster', 5.0)
        elif elapsed < 5100:  # 5:05–5:30 AM
            progress = (elapsed - 3300) / 1800.0
            self.current_layer_volumes = {
                'birds': 0.35 + (0.20 * progress),
                'stream': 0.25 + (0.10 * progress),
                'wind': 0.10 + (0.10 * progress)
            }
            # Occasional micro-sounds
            if random.random() < 0.01:  # ~1% chance per cycle
                self._trigger_event('micro', 1.0)
        elif elapsed < 5700:  # 5:30–5:45 AM
            self.current_layer_volumes = {
                'birds': 0.55,
                'stream': 0.35,
                'wind': 0.20
            }
        elif elapsed < 6300:  # 5:45–6:05 AM
            self.current_layer_volumes = {
                'birds': 0.60,
                'stream': 0.40,
                'wind': 0.25
            }
            # Trigger bell at 6:00 AM (3600 seconds)
            if 3600 < elapsed < 3620:
                self._trigger_event('bell', 5.0)
        elif elapsed < 9000:  # 6:05–6:30 AM
            self.current_layer_volumes = {
                'birds': 0.60,
                'stream': 0.40,
                'wind': 0.25
            }
        else:
            # Soundscape complete
            self.is_playing = False
            print("Soundscape: Spring Dawn complete")

    def _run_shire_summer_thunderstorm(self, elapsed):
        """
        Late Summer Thunderstorm soundscape (18 minutes = 1080 seconds).
        """
        total_duration = 1080
        if elapsed >= total_duration:
            self.is_playing = False
            print("Soundscape: Summer thunderstorm complete")
            # Back to default / follow-up soundscape (e.g., spring dawn or normal day).
            self.setup_soundscape('shire_spring_dawn')
            return

        # pre-mapped stage boundaries
        if elapsed < 120:  # 0-2m: pre-storm calm
            self.current_layer_volumes = {
                'storm_base': 0.10,
                'thunder': 0.0,
                'gusts': 0.0,
                'post_birds': 0.0
            }
        elif elapsed < 420:  # 2-7m: rain builds
            progress = (elapsed - 120) / 300.0
            self.current_layer_volumes = {
                'storm_base': 0.10 + 0.30 * progress,
                'thunder': 0.05 + 0.10 * progress,
                'gusts': 0.05 + 0.15 * progress,
                'post_birds': 0.0
            }
        elif elapsed < 780:  # 7-13m: peak storm
            progress = (elapsed - 420) / 360.0
            self.current_layer_volumes = {
                'storm_base': 0.40 + 0.20 * (1 - abs(0.5 - progress) * 2),
                'thunder': 0.20 + 0.30 * (1 - abs(0.5 - progress) * 2),
                'gusts': 0.20 + 0.20 * (1 - abs(0.5 - progress) * 2),
                'post_birds': 0.0
            }
        elif elapsed < 960:  # 13-16m: rain relaxes
            progress = (elapsed - 780) / 180.0
            self.current_layer_volumes = {
                'storm_base': 0.60 - 0.20 * progress,
                'thunder': 0.50 - 0.30 * progress,
                'gusts': 0.40 - 0.20 * progress,
                'post_birds': 0.0
            }
        else:  # 16-18m: post storm recovery
            progress = (elapsed - 960) / 120.0
            self.current_layer_volumes = {
                'storm_base': 0.40 * (1 - progress),
                'thunder': 0.20 * (1 - progress),
                'gusts': 0.25 * (1 - progress),
                'post_birds': 0.20 * progress
            }

        # Thunder event triggers
        if elapsed % 45 < 0.1:
            self._trigger_event('thunder', 6.0)
        # Wind gusts events
        if 250 < elapsed < 780 and elapsed % 30 < 0.1:
            self._trigger_event('gust', 3.0)

    def _trigger_event(self, event_type, duration):
        """Trigger a one-time event sound."""
        last_trigger = self.last_event_time.get(event_type, 0)
        current = time.monotonic()
        
        # Only trigger if enough time has passed since last trigger
        if current - last_trigger > duration:
            if event_type == 'rooster':
                print("Soundscape: 🐓 Rooster crows")
                # Implement rooster playback here
            elif event_type == 'bell':
                print("Soundscape: 🔔 Shire bell tolls")
                # Implement bell playback here
            elif event_type == 'micro':
                micro_sound = random.choice(['dew', 'insect', 'flutter'])
                print(f"Soundscape: 💧 {micro_sound} sound")
                # Implement micro-sound playback here
            elif event_type == 'thunder':
                print("Soundscape: 🌩️ Thunder crack")
                # Implement thunder playback here
            elif event_type == 'gust':
                print("Soundscape: 🌬️ Wind gust")
                # Implement gust playback here
            
            self.last_event_time[event_type] = current
    
    def get_volumes(self):
        """Return current layer volumes as dict."""
        return self.current_layer_volumes

# Global instance
soundscape_manager = SoundscapeManager()