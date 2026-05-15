---
name: new-hardware
description: Scaffold or revise CircuitPython hardware modules for the HobbitTown ESP32-S3 diorama. Use when adding sensors, servos, motors, relays, LED strips, buttons, audio boards, displays, or other physical components that need config.py pin definitions, hardware/ modules, non-blocking update functions, Adafruit library imports, and safe initialization behavior.
---

# New Hardware

## Goal
Create a small, readable hardware module that can be safely called from the main loop or a scene module.

## Before editing
Inspect existing project files first:
- `config.py` for pin names and shared constants.
- Existing modules in `hardware/` for naming and style.
- `requirements.txt` and `/lib` for available CircuitPython libraries.
- Related docs in `docs/` if present.

## Workflow
1. Create or update a file in `hardware/`, for example `hardware/servo_door.py` or `hardware/button_panel.py`.
2. Import `config` at the top. Do not hardcode board pins in the module unless the user explicitly asks for a temporary test file.
3. Include all required imports at the top.
4. Provide a simple public interface appropriate to the component. Prefer:
   - `init()` to configure hardware and enter a safe state.
   - `update(current_time=None)` for non-blocking runtime work.
   - `stop()` or `deinit()` when the component needs cleanup.
5. Keep `update()` fast and safe to call repeatedly from `code.py`.
6. Validate user inputs such as target angles, brightness, speed, relay state, or sensor thresholds.
7. If the component needs power or protection guidance, use the `tech-manual` skill as a secondary skill.

## Safety rules
- Never use blocking `time.sleep()` in runtime hardware modules.
- Use `time.monotonic()` for timed behavior.
- Prefer safe startup states: motors stopped, relays off, LEDs off, servos in neutral/default position.
- If a sensor read fails, return `None` or a documented fallback rather than crashing the main loop.
- Do not invent exact current draw or voltage limits. Use the part number or datasheet when available; otherwise label values as estimates.

## Dependency rules
Use Adafruit CircuitPython libraries only. If a new library is needed, add it to `requirements.txt` and mention the library in the response.

## Output checklist
After editing, include:
- `What changed`
- `Files changed`
- `Config additions needed`
- `How to test on the board`
