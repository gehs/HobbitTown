# Copilot Instructions for HobbitTown

## Project context
HobbitTown is an interactive physical diorama controlled by an ESP32-S3 running CircuitPython. Keep the code modular: hardware drivers live in `hardware/`, high-level orchestration lives in `logic/`, configuration lives in `config.py`, and the main loop lives in `code.py`, place modular testingig within `tests/` or root test files. The project includes a web dashboard for control and monitoring, but all core scene logic and hardware control must run on the ESP32-S3 without reliance on external servers or cloud services.

The user is learning embedded hardware and software. Favor clear, safe, educational changes over clever or compact code.

## Non-negotiable coding rules
- Use CircuitPython syntax and Adafruit-compatible libraries. Do not use Arduino C++, Raspberry Pi GPIO libraries, or MicroPython `machine` APIs.
- Do not use blocking timing such as `time.sleep()` inside runtime modules that must cooperate with the main loop. Use `time.monotonic()` or `adafruit_ticks` style elapsed-time checks.
- Keep hardware modules non-blocking. Each `update()` function must return quickly.
- Do not hardcode pins, LED counts, timing limits, brightness limits, or hardware capacities inside feature modules. Read them from `config.py` or documented JSON/config files.
- Initialize hardware into a safe state: LEDs off, servos/motors idle, relays off, audio stopped unless explicitly requested.
- Handle missing files, missing hardware IDs, bad preset names, sensor read failures, and unavailable audio assets without crashing the main loop.
- Add new Adafruit library dependencies to `requirements.txt` and, when possible, check whether the library is already present in `/lib`.

## Repository conventions
- `hardware/`: direct hardware control modules such as lighting, audio, motors, buttons, sensors, and displays.
- `logic/`: scene/state-machine orchestration that coordinates hardware modules.
- `docs/`: beginner-friendly wiring guides, soundscape plans, scene plans, and version notes.
- `tests/` or root test files: on-device hardware test scripts for the serial terminal.
- `config.py`: pin names, constants, limits, feature flags, and shared project configuration.
- `requirements.txt`: CircuitPython library bundle dependencies.

## Response style
- Use concise markdown with headings and bullets.
- Explain why a hardware safety choice matters.
- Include a short `What changed` section after edits.
- Include a `How to test` section when code changes are made.
- When uncertain about exact hardware limits, say so and ask for the component part number or datasheet instead of guessing.

## Skill routing
Project skills are stored in `.github/skills/`. Use the most specific skill for the task before falling back to general instructions.

| Request type | Primary skill | Secondary skill |
|---|---|---|
| Wiring, power, protection components, pin safety | `tech-manual` | `new-hardware` |
| New sensor, motor, LED strip, relay, display, audio board | `new-hardware` | `tech-manual` |
| New themed sequence such as storm, party, market, dragon arrival | `new-scene` | `lighting-management`, `music-scape`, `ui` |
| LED segments, presets, brightness, animations | `lighting-management` | `new-scene` |
| Ambient audio, sound effects, sample lists, trigger mapping | `music-scape` | `new-scene` |
| Web dashboard, controls, settings page, local UI | `ui` | `lighting-management`, `new-scene` |
| On-device serial hardware test launcher or test modules | `unit-tester` | `new-hardware` |

## Agent behavior
Before editing files, inspect the relevant existing files and preserve naming style. Prefer incremental edits over rewrites. When a request crosses multiple domains, start with the primary skill and then apply secondary skills only for the parts that need them.
