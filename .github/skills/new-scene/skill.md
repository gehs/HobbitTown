---
name: new-scene
description: Create or modify non-blocking CircuitPython scene orchestration modules for HobbitTown. Use when the user asks for themed sequences such as thunderstorm, party, market day, dragon arrival, sunrise, or night mode that coordinate lighting, audio, motion, sensors, UI controls, and timers through start(), update(), and stop() functions.
---

# New Scene

## Goal
Create a scene module that coordinates existing hardware modules over time without blocking the main loop.

## Before editing
Inspect existing files:
- `logic/` scene modules for naming and lifecycle style.
- `hardware/` modules that the scene will call.
- `config.py` for constants and feature flags.
- Relevant docs or asset plans in `docs/`.

## Workflow
1. Create or update a scene file in `logic/`, for example `logic/scene_thunderstorm.py`.
2. Import `time`, `config`, and only the hardware modules the scene actually uses.
3. Provide these lifecycle functions:
   - `start()` sets initial state and records `scene_start_time`.
   - `update(current_time=None)` advances the scene using elapsed-time checks.
   - `stop()` returns hardware to a safe idle state.
4. Use descriptive timestamp variables such as `scene_start_time`, `last_lightning_time`, and `next_thunder_time`.
5. Write scene behavior as a state machine or step table. Do not write blocking scripts.
6. Add comments that explain the story beats, for example what should happen at second 1, second 3, and second 10.
7. Coordinate with secondary skills when needed:
   - `lighting-management` for LED effects and presets.
   - `music-scape` for audio files and trigger timing.
   - `new-hardware` for missing hardware modules.
   - `ui` for controls or status display.

## Runtime rules
- Do not use `time.sleep()` in scene modules.
- `update()` must return quickly so `code.py` can keep reading sensors and handling UI.
- Missing optional hardware should not crash the scene. Print a warning or skip that feature.
- Scene code should call public hardware-module functions instead of directly manipulating pins whenever possible.

## Output checklist
After editing, include:
- Scene timeline summary.
- Files changed.
- Hardware modules used.
- Audio or lighting assets needed.
- How to test and how to stop the scene safely.
