# Hardware Test Scene: Usage Guide

## Quick Start

### Manual Trigger (Python)
```python
from logic.certification_dry_run_scene import run_comprehensive_dry_run
run_comprehensive_dry_run(smial_tracks=(310, 312, 314), exciter_tracks=(1, 2))
```

Or run the launcher script directly:
```python
import test_comprehensive_dry_run
```

### Modular Dry-Run Suite (Smial Modules)
```python
import test_modular_dry_run_suite
```

Interactive bench capture launcher (records operator pass/fail):
```python
import test_modular_bench_capture
```

This writes a report file at `modular_dry_run_bench_results.json` with per-module audio/segment outcomes.

This modular suite runs independent modules in sequence:
- `Smial1` module (door 1, chimney relay 1, spot speaker 1 range, Smial 1 light)
- `Smial2` module (door 2, chimney relay 2, spot speaker 2 range, Smial 2 light)
- `Smial3` module (door 3, chimney relay 3, spot speaker 3 range, grouped Smial 3 lights)
- `Stream` module (spot speaker 4 range + stream lights)
- `Sky` module (exciter checks + sky lights)

Track-to-output addressing in the modular suite is validated as:
- Output number must be 1..8
- Track number must be 1..4096

Exciter routing uses Tsunami physical labels as wiring labels only:
- `4L` -> mono output `7` -> command index `6`
- `4R` -> mono output `8` -> command index `7`

### Web API Trigger
Call HTTP endpoint (once web server is fully implemented):
```
GET /test
```

---

## What The Test Does

The **Smial Inspection Test** validates all hardware components across three hobbit holes (smials) in sequence:

### Timeline (~60-70 seconds total)

**Smial 1: first stage block**
- Door 1 open/close test
- Chimney relay 1 on/off test
- Spot speaker track 310
- Smial 1 light fade in/out

**Smial 2: second stage block**
- Door 2 open/close test
- Chimney relay 2 on/off test
- Spot speaker track 312
- Smial 2 light fade in/out

**Smial 3: third stage block**
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
| Lights don't change | Incorrect segment ID | Verify `ref/lights.json` segment ranges |
| No audio | Audio stubs active or Tsunami UART miswired | Check `ENABLE_AUDIO_UART`, UART pin wiring on GPIO17/18, and `tsunami.ini` on the Tsunami SD card |
| Fogger doesn't spray | Relay stuck or unplugged | Inspect GPIO39 relay wiring (or GPIO47 fallback if remapped) |

---

## Repeating the Test

The test is a one-shot sequence and then stops automatically. To repeat:
1. Wait for previous test to complete
2. Run `test_comprehensive_dry_run.py` again

Alternatively, integrate into a continuous loop for stress testing.

---

## Operator Checklist (Modular Dry Run)

Use this checklist to complete audio-output and segment-coverage verification on bench.

1. Run static preflight first:
	- `python -m tests.modular_dry_run.preflight_verification`
	- Confirm it prints `[PRECHECK] PASS`.

2. Start modular suite on device:
	- `import test_modular_dry_run_suite`

	Or run guided capture (recommended for bench sign-off):
	- `import test_modular_bench_capture`

3. Verify audio output mapping during runtime (watch serial logs and listen physically):
	- Smial1 start/end: output 4, tracks 310 and 311.
	- Smial2 start/end: output 2, tracks 312 and 314.
	- Smial3 start/end: output 3, tracks 314 and 316.
	- Stream start: output 4, track 316.
	- Sky left/right: physical labels `4L` and `4R` routed as output 7/index 6 and output 8/index 7.

4. Verify segment coverage visually:
	- Smial1 should light `smial_1` and `chimney_smial_1`.
	- Smial2 should light `smial_2` and `chimney_smial_2`.
	- Smial3 should light `smial_3_lower`, `smial_3_main`, `smial_3_upper`, and `chimney_smial_3`.
	- Stream module should animate stream strip and shut it off on stop.
	- Sky module should animate sky strip and shut it off on stop.

5. Confirm safe shutdown behavior:
	- Doors return to neutral.
	- Relays return off-safe state.
	- Ground, stream, and sky LEDs are off.
	- Tsunami STOP_ALL was sent at module stop/suite finish.

6. Record pass/fail notes per module:
	- Smial1
	- Smial2
	- Smial3
	- Stream
	- Sky

---

## Advanced: Custom Test Sequence

To modify the comprehensive dry-run flow, edit `logic/certification_dry_run_scene.py`:
- Adjust stage timing in `_build_stage_plan()`
- Add/remove stage checks
- Change Smial track mapping in `ComprehensiveDryRunScene.__init__()`
- Change light behavior in `_mk_smial_light_tick()`

Remember to use `time.monotonic()` for non-blocking timing!