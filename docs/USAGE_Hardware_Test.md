# Hardware Test Scene: Usage Guide

## Quick Start

### Manual Trigger (Python)
```python
from logic.dry_run_scene import run_comprehensive_dry_run
run_comprehensive_dry_run(smial_tracks=(310, 312, 314), exciter_tracks=(1, 2))
```

Or run the launcher script directly:
```python
import test_comprehensive_dry_run
```

### Web API Trigger
Call HTTP endpoint (once web server is fully implemented):
```
GET /test
```

---

## What The Test Does

The **Smial Inspection Test** validates all hardware components across three hobbit holes (smials) in sequence:

### Timeline (~60-70 seconds total)

**Smial 1 (Bag End): first stage block**
- Door 1 open/close test
- Chimney relay 1 on/off test
- Spot speaker track 310
- Smial 1 light fade in/out

**Smial 2: second stage block**
- Door 2 open/close test
- Chimney relay 2 on/off test
- Spot speaker track 312
- Smial 2 light fade in/out

**Smial 3 (The Great Smial): third stage block**
- Door 3 open/close test
- Chimney relay 3 on/off test
- Spot speaker track 314
- Smial 3 grouped light fade in/out (`smial_3_lower`, `smial_3_main`, `smial_3_upper`)

Each test verifies:
- ✓ Speaker audio output
- ✓ Servo door movement (open/close)
- ✓ LED lighting control (fade in/out)
- ✓ Chimney relay (per-smial on/off)

After the three smial checks, the comprehensive run also verifies:
- ✓ Fogger relay cycle (shared)
- ✓ Exciter track 1 and 2 playback checks
- ✓ Stream strip animation check
- ✓ Sky strip animation check

---

## Audio Files Needed

Ensure these Tsunami track numbers exist on SD:

| Track | Purpose |
|------|---------|
| `310` | Smial 1 spot speaker check |
| `312` | Smial 2 spot speaker check |
| `314` | Smial 3 spot speaker check |
| `001` | Exciter 1 check |
| `002` | Exciter 2 check |

**Note:** If tracks are missing, the sequence still runs but you should mark the relevant audio check as failed.

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
| No audio | Audio stubs active or Tsunami UART miswired | Check `ENABLE_AUDIO_UART`, UART pin wiring on GPIO17/18, and `tsunami.ini` on the Tsunami SD card |
| Fogger doesn't spray | Relay stuck or unplugged | Inspect GPIO39 relay wiring (or GPIO47 fallback if remapped) |

---

## Repeating the Test

The test is a one-shot sequence and then stops automatically. To repeat:
1. Wait for previous test to complete
2. Run `test_comprehensive_dry_run.py` again

Alternatively, integrate into a continuous loop for stress testing.

---

## Advanced: Custom Test Sequence

To modify the comprehensive dry-run flow, edit `logic/dry_run_scene.py`:
- Adjust stage timing in `_build_stage_plan()`
- Add/remove stage checks
- Change Smial track mapping in `ComprehensiveDryRunScene.__init__()`
- Change light behavior in `_mk_smial_light_tick()`

Remember to use `time.monotonic()` for non-blocking timing!