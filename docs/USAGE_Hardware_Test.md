# Hardware Test Scene: Usage Guide

## Quick Start

### Manual Trigger (Python)
```python
from code import trigger_hardware_test
trigger_hardware_test()
```

### Web API Trigger
Call HTTP endpoint (once web server is fully implemented):
```
GET /test
```

---

## What The Test Does

The **Smial Inspection Test** validates all hardware components across three hobbit holes (smials) in sequence:

### Timeline (2 minutes total)

**Smial 1 (Bag End): 0-40 seconds**
- Audio narration + bell tone announces test
- Door 1 opens and closes smoothly
- Lights fade in (warm white) then out
- Chimney fogger activates, hisses, then stops

**Smial 2: 40-80 seconds**
- Repeats test sequence for Smial 2

**Smial 3 (The Great Smial): 80-120 seconds**
- Repeats test sequence for Smial 3

Each test verifies:
- ✓ Speaker audio output
- ✓ Servo door movement (open/close)
- ✓ LED lighting control (fade in/out)
- ✓ Fogger relay (on/off)

---

## Audio Files Needed

Place these files in `/audio/test_scene/`:

| File | Purpose | Duration |
|------|---------|----------|
| `test_bell.wav` | Bell tone to announce test | 2 sec |
| `test_narration_bagend.wav` | "Testing Bag End" | 2 sec |
| `test_narration_smial2.wav` | "Testing Smial 2" | 2 sec |
| `test_narration_smial3.wav` | "Testing Smial 3" | 2 sec |
| `door_open.wav` | Door creak/squeak | 1 sec |
| `door_close.wav` | Door close (quiet) | 1 sec |
| `lights_on.wav` | Confirmation beep | 0.5 sec |
| `lights_off.wav` | Lower beep | 0.5 sec |
| `fogger_hiss.wav` | Fogger activation | 1 sec |
| `fogger_stop.wav` | Fogger shutoff click | 0.5 sec |

**Note:** If audio files are missing, the test will still run but without narration. Visual and mechanical tests will complete normally.

---

## Interpretation Guide

### Success Indicators
- ✓ Door opens completely (90°), then closes back to neutral (0°)
- ✓ Lights brighten to warm white, then dim to off
- ✓ Fogger activates with visible mist, deactivates cleanly
- ✓ Audio plays clearly from each speaker location

### Potential Issues

| Issue | Likely Cause | Action |
|-------|--------------|--------|
| Door doesn't move | Servo not responding | Check PCA9685 I2C connection |
| Lights don't change | Incorrect segment ID | Verify `lights.json` segment ranges |
| No audio | Audio stubs active (no hardware) | Audio print statements in console |
| Fogger doesn't spray | Relay stuck or unplugged | Inspect GPIO 18 relay wiring |

---

## Repeating the Test

The test is a one-shot sequence that runs for ~2 minutes and then stops automatically. To repeat:
1. Wait for previous test to complete
2. Call `trigger_hardware_test()` again

Alternatively, integrate into a continuous loop for stress testing.

---

## Advanced: Custom Test Sequence

To modify the test flow, edit `logic/test_scene.py`:
- Adjust timings in `_run_smial_test()` function
- Add/remove test steps
- Change lighting colors or fog duration
- Customize audio track numbers

Remember to use `time.monotonic()` for non-blocking timing!