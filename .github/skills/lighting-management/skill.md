---
name: lighting-management
description: Design, modify, and review non-blocking CircuitPython lighting modules for the HobbitTown diorama. Use when asked to implement LED segments, SK6812 or WS2812 strips, lighting presets such as storm, calm, party, or test, lights.json mappings, brightness scaling, color ordering, or hardware/lighting_manager.py behavior.
---

# Lighting Management

## Goal
Create safe, non-blocking lighting behavior for HobbitTown while keeping hardware control separate from scene logic.

## Before editing
Inspect the project before writing code:
- `hardware/lighting_manager.py` or any existing lighting module.
- `config.py` for brightness, pin names, LED counts, and feature flags.
- `lights.json` or other segment maps.
- `requirements.txt` and `/lib` for CircuitPython library dependencies.

If one of these files is missing, state the assumption and create the smallest useful scaffold instead of inventing a large architecture.

## Workflow
1. Keep lighting hardware logic in `hardware/lighting_manager.py` unless the repository already uses a different name.
2. Provide or preserve these public functions when appropriate:
   - `init_lighting()`
   - `update_lighting(current_time=None)`
   - `set_segment_color(segment_id, rgb)`
   - `apply_preset(preset_name)`
   - `stop_lighting()`
3. Use `time.monotonic()` or a supplied `current_time` value for all timers.
4. Keep `update_lighting()` fast. It should compute the next state and return without blocking.
5. Load LED segment definitions from `lights.json` when available. Validate segment IDs before use.
6. Scale RGB values with `config.BRIGHTNESS` or the project brightness constant before writing to LEDs.
7. Track strip type per segment. Use the correct color order for SK6812 versus WS2812 when the hardware/library requires it.
8. Handle invalid preset names by logging or printing a clear warning and leaving the current state safe.

## Preset behavior
Implement presets as named state machines, not as blocking loops.

Minimum expected presets:
- `storm`: intermittent lightning flashes with safe return to ambient state.
- `calm`: steady low-brightness warm/ambient lighting.
- `party`: repeating color changes using elapsed-time checks.
- `test`: simple deterministic segment check for physical verification.

## Dependency rules
Use Adafruit CircuitPython libraries only. If a new library is needed:
1. Check whether the import already exists in the repo or `/lib`.
2. Add the dependency to `requirements.txt` if it is newly required.
3. Include all imports at the top of the file.

## Verification checklist
After changes, explain how to verify:
- `init_lighting()` turns all LEDs off.
- Each known preset can be selected without crashing.
- Unknown presets do not crash.
- Missing segment IDs do not crash.
- The main loop remains responsive while lighting effects run.
