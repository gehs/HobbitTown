# Hardware Test Scene: Smial Inspection

**Purpose:** Verify all three smials (Smial 1, Smial 2, Smial 3) are functional by testing speaker, door servo, lighting, and chimney fogger for each unit in sequence.

**Duration:** ~2 minutes total (~40 seconds per smial)

**Audio Narration:**
- "Testing Smial 1..." (speaker 1)
- "Door test..." (servo movement sound)
- "Lights on." / "Lights off." (LED confirmation)
- "Chimney test." (fogger activation sound)
- Repeat for Smial 2, Smial 3

---

## Scene Flow

### Smial 1: 0-40 seconds
1. **0-2s:** Play narration "Testing Smial 1" with bell tone (speaker audio)
2. **2-5s:** Door servo 1 opens (0° → 90°), plays door creak sound
3. **5-8s:** Door servo 1 closes (90° → 0°), plays door close sound
4. **8-12s:** Lights (Smial 1 segment) fade 0% → 100% (warm white), play "Lights on"
5. **12-15s:** Lights fade 100% → 0%, play "Lights off"
6. **15-18s:** Fogger activates (chimney rising), play fogger hiss sound
7. **18-20s:** Fogger holds, play confirmation tone
8. **20-25s:** Fogger stops (chimney falling), play stop sound
9. **25-40s:** Silence/pause before next smial

### Smial 2: 40-80 seconds
- Repeat flow for Smial 2 (door servo 2, Smial 2 lights)

### Smial 3: 80-120 seconds
- Repeat flow for Smial 3 (door servo 3, Smial 3 lights)

---

## Hardware Mapping

| Component | Resource | Action |
|-----------|----------|--------|
| Speaker (Smial 1) | MAX98357 #1 | Play bell tone, narration, feedback |
| Speaker (Smial 2) | MAX98357 #2 | Play bell tone, narration, feedback |
| Speaker (Smial 3) | MAX98357 #3 | Play bell tone, narration, feedback |
| Door 1 (Smial 1) | PCA9685 ch 0 | Open/close sequence |
| Door 2 (Smial 2) | PCA9685 ch 1 | Open/close sequence |
| Door 3 (Smial 3) | PCA9685 ch 2 | Open/close sequence |
| Lights (Smial 1) | SK6812 px 89-91 | Fade warm white 0-100% |
| Lights (Smial 2) | SK6812 px 92-94 | Fade warm white 0-100% |
| Lights (Smial 3) | SK6812 px 95-99 | Fade warm white 0-100% |
| Fogger | GPIO 18 Relay | Pulse on/off cycles |

---

## Audio Files Required

Store in `/audio/test_scene/`:
- `test_bell.wav` (2 sec, bell tone to announce test)
- `test_vocal_start_smial1.wav` (2 sec, "Testing Smial 1")
- `test_sound_smial1.wav` (2 sec, musical tone)
- `test_vocal_start_smial2.wav` (2 sec, "Testing Smial 2")
- `test_sound_smial2.wav` (2 sec, musical tone)
- `test_vocal_start_smial3.wav` (2 sec, "Testing Smial 3")
= `test_sound_smial3.wav` (2 sec, musical tone)
- `door_open.wav` (1 sec, door creak/squeak)
- `door_close.wav` (1 sec, quiet close)
- `lights_on.wav` (0.5 sec, confirmation beep)
- `lights_off.wav` (0.5 sec, lower beep)
- `fogger_hiss.wav` (1 sec, fogger activation sound)
- `fogger_stop.wav` (0.5 sec, shut-off click)
- `test_vocal_end_smial1.wav` (2 sec, "Testing Smial 1")
- `test_vocal_end_smial2.wav` (2 sec, "Testing Smial 2")
- `test_vocal_end_smial3.wav` (2 sec, "Testing Smial 3")
- `test_complete.wav` (1 sec, all-clear tone)


---

## Implementation Notes

- Use `time.monotonic()` to track elapsed time per smial
- Sequence events within 40-second windows
- Fade lights using sine wave over 4 seconds
- Play audio via existing routes
- Wait 10 seconds between smials for visual inspection
- Loop continuously or trigger manually via web API
