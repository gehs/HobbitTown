# The Waking of the Shire: Late Summer Thunderstorm Soundscape (18 minutes)

**Duration:** 18 minutes  
**Theme:** Late summer storm in the Shire, starting from quiet pre-storm tension, swelling into a thunderstorm, then gently returning to normal ambience.

## Structure

1. **00:00–02:00** — pre-storm calm, wind picks up, distant thunder rumble
2. **02:00–07:00** — rain starts soft, eventually heavy
3. **07:00–13:00** — full thunderstorm, strong rainfall, wind gusts, deep thunder and occasional campfire sounds (distant)
4. **13:00–16:00** — rain softens, thunder fades
5. **16:00–18:00** — storm clears, return to normal Shire ambience

## Audio Layers

- **Storm Atmosphere (Base)**: long loop MP3 (18 min) for rain + wind at mid-to-high volume
- **Thunder Events**: short WAV external thunder cracks, triggered at random intervals
- **Rain Intensity FX**: 4–5 short WAVs (light, medium, heavy) crossfade for dynamic realism
- **Wind Gusts**: short WAVs triggered around 5-7 min in the middle
- **Post-Storm Birds**: early afternoon bird chatter enters at ~14:00 mark

## Speaker/Amplifier Assignment

| Layer | Audio Output | Amplifier | Notes |
|-------|-------|-----------|-------|
| Base Storm | Tsunami track 001 | GF1002 | Main immersion (rain + wind loop) |
| Thunder, Gusts | Tsunami track 002-005 | GF1002 | Event triggers (cracks, gusts) |
| Post-Storm Birds | Tsunami track 006 | GF1002 | Clean natural transition |
| Storm Texture | Optional: Tsunami aux → LQ-AMP10W | Exciters only | Deep rumble felt through floor panels |

**Architecture note:** All speaker outputs route through a single GF1002 amplifier. The Tsunami mixes all tracks into a unified stereo output that plays through speakers and optionally through the LQ-AMP10W exciters for atmospheric vibration.

## Implementation Details

- Start by muting any running soundscape and fading to near-zero in 2 seconds.
- Preload all sounds into variables/players
- Use `time.monotonic()` for non-blocking timeline control
- Ensure missing track does not crash; print warnings only

## Sample Sound Files

- `thunderstorm_base_18m.mp3` (room rain + wind)
- `thunder_crack_1.wav`, `thunder_crack_2.wav`, ...
- `heavy_rain_3s.wav`, `light_rain_3s.wav`
- `wind_gust_2s.wav`
- `birds_poststorm_6m.mp3`

## Search Terms

- "summer thunderstorm ambience" (MP3)
- "heavy rain loop" (WAV)
- "thunder crack close" / "thunder rumble save" 
- "afternoon birds after rain"

---

## Soundscape Transition Behavior

1. **Start**: fade old loop out over 2 sec
2. **Entry**: 0-2m soft rain, low wind (30% volume)
3. **Build**: 2-7m rain gets louder + thunder at random 20-30s intervals
4. **Peak**: 7-13m heavy rain, strong wind, thunder 10-15s intervals
5. **Release**: 13-16m rain < 60%, thunder < 30%
6. **Normal**: 16-18m add birds, storm diffusely fading out

---

## CircuitPython code pattern

- instantiate `SoundscapeManager`
- call `setup_soundscape('shire_summer_thunderstorm')`
- call `run_soundscape_cycle()` in main loop
- each call updates internal `current_layer_volumes` and triggers thunder events
- once complete, calls `setup_soundscape('shire_spring_dawn')` or existing hour/day soundscape
