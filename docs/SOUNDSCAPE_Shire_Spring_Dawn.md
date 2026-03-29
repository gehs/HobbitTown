# The Waking of the Shire: Spring Dawn Soundscape

**Time Period:** 4:00 AM – 6:30 AM  
**Season:** Mid-April (Spring)  
**Theme:** Peaceful awakening of the Shire on a gentle spring morning

---

## Overview

This soundscape captures the tranquil transition from pre-dawn darkness to early morning light in the Shire. Spring birdsong gradually builds, morning water sources become audible, and the gentle rustle of awakening flora creates an immersive natural landscape. The progression mirrors the astronomical dawn, with sounds layering to increase intensity and activity as morning approaches.

---

## Audio Components & Configuration

### Component 1: Ambient Bird Chorus (Primary Layer)
- **Type:** Looping MP3 background track
- **Duration:** ~10-12 minutes (seamless loop)
- **Audio Output:** MAX98357 Amplifier #1 → Speaker #1 (Bag End/Main area)
- **Timing:** Runs continuously from 4:00 AM, gradually increases in volume
- **Description:** Mixed spring birdsong featuring robins, thrushes, blackbirds, and sparrows. Starts very quietly at 4:00 AM and crescendos by 6:30 AM as more "birds" awaken.

### Component 2: Water Features (Secondary Layer)
- **Type:** Looping MP3/WAV ambient track
- **Duration:** ~8-10 minutes (seamless loop)
- **Audio Output:** MAX98357 Amplifier #2 → Speaker #2 (River segment area)
- **Timing:** Fades in around 4:30 AM
- **Description:** Gentle stream flow, distant running water, occasional babbling brook sounds. Suggests the River running through the Shire.

### Component 3: Breeze & Foliage Rustle (Ambient Layer)
- **Type:** Looping WAV or short MP3
- **Duration:** ~6-8 minutes (seamless loop)
- **Audio Output:** MAX98357 Amplifier #3 → Speaker #3 (Party Tree area)
- **Timing:** Subtle throughout, peaks around 5:30 AM
- **Description:** Soft wind through leaves, gentle rustling of spring flowers and budding branches. Occasional gentle gusts.

### Component 4: Dew & Nature Micro-sounds (Texture Layer)
- **Type:** Short WAV samples
- **Duration:** 1-3 seconds each, triggered randomly
- **Audio Output:** MAX98357 Amplifier #4 → Speaker #4 (Bridge area)
- **Timing:** Random trigger intervals starting around 4:45 AM
- **Description:** Occasional dew drops falling, small insects stirring, delicate natural sounds that add depth without overwhelming.

### Component 5: Distant Bell Toll & Rooster (Event Markers)
- **Type:** Single WAV samples
- **Duration:** 3-8 seconds
- **Audio Output:** MAX98357 Amplifier #5 → Audio Exciter #1 (atmospheric presence)
- **Timing:** Rooster at 5:15 AM (single crow), church/Shire bell at 6:00 AM (2-3 tolls)
- **Description:** Distant rooster crow suggesting nearby farms. Subtle Shire bell toll marking the quarter-hour, adding a fantastical element to the natural soundscape.

---

## Speaker & Amplifier Mapping

| Component | Speaker # | Amplifier | Location/Purpose |
|-----------|-----------|-----------|------------------|
| Bird Chorus | #1 | MAX98357 #1 | Center (Bag End) - primary narrative |
| Water Features | #2 | MAX98357 #2 | River segment - spatial positioning |
| Wind/Foliage | #3 | MAX98357 #3 | Party Tree area - ambient surround |
| Micro-sounds | #4 | MAX98357 #4 | Bridge area - subtle texture |
| Bell/Rooster | Exciter #1 | MAX98357 #5 | Directional/atmospheric depth |

---

## Audio File Search Terms & Sources

Use these terms to find or create audio samples from royalty-free sources like **Freesound.org**, **Zenodo**, or **BBC Sound Library**:

### Primary Searches:
1. **"spring bird chorus dawn"** - Get a mixed track with multiple species
2. **"gentle stream flowing"** or **"babbling brook"** - Natural water ambience
3. **"wind through leaves"** or **"breeze rustling grass"** - Foliage ambience
4. **"dew dripping"** + **"morning insects"** - Micro-sound effects
5. **"rooster crow distant"** - Single clear rooster sound
6. **"church bell toll"** or **"shire fantasy bell"** - Atmospheric marker

### Recommended Audio Processing:
- Apply low-pass filter (~6kHz) to bird chorus for naturalistic depth
- Compress ensemble slightly to maintain consistency
- Use reverb (small room, ~0.5s decay) for spatial cohesion
- Fade in/out audio layers (5-10 second curves) to avoid abrupt transitions

---

## Audio File Mapping & Implementation

Store all audio files on the **Micro SD Card** (8GB available). Organize in a dedicated folder:

```
/audio/
  /shire_spring_dawn/
    - birds_chorus_spring.mp3          (10–12 min, primary)
    - stream_flowing_gentle.wav        (8–10 min, looping)
    - wind_foliage_rustle.wav          (6–8 min, looping)
    - dew_drop_single.wav              (1 sec, triggerable)
    - insect_chirp_soft.wav            (0.5 sec, triggerable)
    - rooster_distant_single.wav       (3 sec, single trigger)
    - shire_bell_toll_single.wav       (5 sec, single trigger)
    - leaves_flutter_quick.wav         (2 sec, occasional)
```

**File Format Guidelines:**
- **Long ambience (>3 min):** MP3 @ 128 kbps to save space
- **Short samples (<3 sec):** WAV @ 16-bit 44.1kHz for responsiveness
- **Total storage:** ~50–80 MB for full soundscape set

---

## Time-Based Event Schedule

| Time | Event | Action |
|------|-------|--------|
| 4:00 AM | Dawn begins | Fade in bird chorus very quietly (5% volume) |
| 4:30 AM | Day progresses | Fade in stream sounds (15% volume), birds increase to 20% |
| 5:00 AM | More activity | Wind/foliage enters (10% volume), birds 35%, stream 25% |
| 5:15 AM | Rooster crow | Trigger rooster sample once |
| 5:30 AM | Peak dawn | Birds 60%, stream 40%, wind 25%, occasional micro-sounds active |
| 5:45 AM | Approaching sunrise | Birds holding steady at 60%, all layers present |
| 6:00 AM | Sunrise mark | Trigger Shire bell toll (2-3 rings, 50% volume) |
| 6:15 AM | Full morning | All layers at full intended volume, bird chorus peaks |
| 6:30 AM | Morning established | Transition to full daylight state (or loop for ambience) |

---

## CircuitPython Implementation

### 1. Audio Manager Module (`hardware/soundscape.py`)

```python
import time
import busio
import digitalio
import config

# Track state for non-blocking audio management
class SoundscapeManager:
    def __init__(self):
        self.start_time = None
        self.is_playing = False
        self.current_layer_volumes = {
            'birds': 0.0,
            'stream': 0.0,
            'wind': 0.0,
            'micro': 0.0,
            'event': 0.0,
        }
        self.last_rooster_time = 0
        self.last_bell_time = 0
        self.last_micro_sound_time = 0
    
    def setup_soundscape(self):
        """Initialize audio hardware and DFPlayer modules for soundscape."""
        print("Soundscape: Initializing Spring Dawn soundscape...")
        self.start_time = time.monotonic()
        self.is_playing = True
    
    def run_soundscape_cycle(self, current_hour=None):
        """
        Non-blocking soundscape update cycle.
        Call repeatedly in main loop.
        """
        if not self.is_playing or current_hour != 4:  # Only run at 4 AM hour
            return
        
        elapsed = time.monotonic() - self.start_time
        
        # Calculate volume fade-ins based on elapsed time (in seconds)
        # Assuming 4:00 AM = 0s, 6:30 AM = 9000s (2.5 hours)
        
        if elapsed < 300:  # 4:00–4:05 AM - Bird intro
            self.current_layer_volumes['birds'] = 0.05
        elif elapsed < 900:  # 4:05–4:15 AM
            self.current_layer_volumes['birds'] = 0.10
        elif elapsed < 1800:  # 4:15–4:30 AM
            self.current_layer_volumes['birds'] = 0.20
            self.current_layer_volumes['stream'] = 0.15
        elif elapsed < 3000:  # 4:30–5:00 AM
            self.current_layer_volumes['birds'] = 0.35
            self.current_layer_volumes['stream'] = 0.25
            self.current_layer_volumes['wind'] = 0.10
        elif elapsed < 3300:  # 5:00–5:05 AM (Rooster triggers around 5:15, prepare)
            self.current_layer_volumes['birds'] = 0.45
            self.current_layer_volumes['stream'] = 0.30
            self.current_layer_volumes['wind'] = 0.15
        elif elapsed < 5100:  # 5:05–5:30 AM (Rooster at 5:15)
            self.current_layer_volumes['birds'] = 0.55
            self.current_layer_volumes['stream'] = 0.35
            self.current_layer_volumes['wind'] = 0.20
            # Trigger rooster once around 5:15 AM (900 seconds from 4:00)
            if 900 < elapsed < 920 and (time.monotonic() - self.last_rooster_time > 1):
                self.trigger_event_sound('rooster')
                self.last_rooster_time = time.monotonic()
        elif elapsed < 5700:  # 5:30–5:45 AM
            self.current_layer_volumes['birds'] = 0.60
            self.current_layer_volumes['stream'] = 0.40
            self.current_layer_volumes['wind'] = 0.25
            # Occasional micro-sounds (dew, insects)
            if (time.monotonic() - self.last_micro_sound_time > 15):
                self.trigger_micro_sound()
                self.last_micro_sound_time = time.monotonic()
        elif elapsed < 6300:  # 5:45–6:05 AM (Bell at 6:00 AM = 3600 seconds)
            self.current_layer_volumes['birds'] = 0.60
            self.current_layer_volumes['stream'] = 0.40
            self.current_layer_volumes['wind'] = 0.25
            # Trigger bell at 6:00 AM (3600 seconds)
            if 3600 < elapsed < 3620 and (time.monotonic() - self.last_bell_time > 1):
                self.trigger_event_sound('bell')
                self.last_bell_time = time.monotonic()
        elif elapsed < 9000:  # 6:05–6:30 AM (End of soundscape)
            self.current_layer_volumes['birds'] = 0.60
            self.current_layer_volumes['stream'] = 0.40
            self.current_layer_volumes['wind'] = 0.25
    
    def trigger_event_sound(self, event_type):
        """Trigger one-off event sounds (rooster, bell)."""
        if event_type == 'rooster':
            print("Soundscape: Rooster crows in the distance...")
            # play_audio(player=2, track=TRACK_ROOSTER, loop=False)
        elif event_type == 'bell':
            print("Soundscape: Shire bell tolls...")
            # play_audio(player=2, track=TRACK_SHIRE_BELL, loop=False)
    
    def trigger_micro_sound(self):
        """Randomly trigger subtle micro-sounds."""
        import random
        micro_type = random.choice(['dew', 'insect', 'flutter'])
        print(f"Soundscape: {micro_type} sound...")
        # Implementation depends on audio hardware capability

# Global instance
soundscape = SoundscapeManager()
```

### 2. Integration into `code.py`

```python
import hardware.soundscape as soundscape
import time_sync

def setup():
    """Initialize all hardware systems."""
    # ... existing setup ...
    soundscape.soundscape.setup_soundscape()

def loop():
    """Main execution cycle - non-blocking."""
    # ... existing loop code ...
    
    current_hour = time_sync.get_hour()
    soundscape.soundscape.run_soundscape_cycle(current_hour)
    
    # ... rest of loop ...
```

---

## Lighting Integration

Coordinate with LED animations for immersive experience:

| Time | LED Action | Lighting Segment |
|------|-----------|-----------------|
| 4:00 AM | Dim starfield (10%) | Star Field fade in |
| 4:30 AM | Moon (cool white) starts fade | The Moon (10% → 30%) |
| 5:15 AM | Rooster crow + subtle Earth colors | Star Field (10% → 5%), Sun prep |
| 6:00 AM | Sun rises (warm white ramp) | The Sun (0% → 70%), Moon fade to 10% |
| 6:30 AM | Full daylight state | All core LEDs at daytime preset |

---

## Storage & SD Card Organization

**Recommended directory structure on Micro SD Card:**

```
/music/
  /00_shire_spring_dawn/
    metadata.json                    (optional: track list)
    birds_chorus_spring.mp3
    stream_flowing_gentle.wav
    wind_foliage_rustle.wav
    dew_drop_single.wav
    insect_chirp_soft.wav
    rooster_distant_single.wav
    shire_bell_toll_single.wav
    leaves_flutter_quick.wav
```

**Metadata example (`metadata.json`):**

```json
{
  "soundscape": "Shire Spring Dawn",
  "start_hour": 4,
  "end_hour": 6,
  "duration_minutes": 150,
  "tracks": [
    {
      "id": 1,
      "name": "birds_chorus_spring.mp3",
      "type": "ambient_loop",
      "duration_sec": 720,
      "volume_range": [0.05, 0.60]
    },
    {
      "id": 2,
      "name": "stream_flowing_gentle.wav",
      "type": "ambient_loop",
      "duration_sec": 480,
      "volume_range": [0.15, 0.40]
    }
  ]
}
```

---

## Notes & Restoration

- **Graceful Fallback:** If audio files are missing, the soundscape manager logs warnings but does not crash
- **Looping Logic:** All ambient tracks should have seamless loop points (tested silence at boundaries)
- **Volume Ceiling:** Ensure composite volume never exceeds 100% across all channels to prevent distortion
- **Memory:** With 5 MAX98357 amplifiers and 8× 2W speakers, the system supports spatial multi-track playback without bottlenecking
- **Future Expansion:** This soundscape template can be adapted for other times of day (Day ambient, Evening twilight, Night cricket chorus, etc.)

---

## References

- **Freesound.org Collections:** "Birdsong," "Spring Ambience," "Natural Water Sounds"
- **BBC Sound Library:** https://www.bbc.co.uk/sounds/collections (excellent for nature recordings)
- **Zenodo Open Science:** "Environmental Recordings" collections (often CC0/CC-BY licensed)
- **Ardour DAW:** Free tool for audio file processing (crossfades, compression, normalization)