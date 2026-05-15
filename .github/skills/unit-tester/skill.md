---
name: unit-tester
description: Create on-device CircuitPython hardware test launchers and serial-terminal test modules for HobbitTown. Use when asked to test multiple hardware modules, build a safe test menu, run lighting/audio/motion/sensor checks one at a time, isolate board tests from production code.py, or create repeatable ESP32-S3 validation scripts before integrating a scene.
---

# Unit Tester

## Goal
Create a practical on-device test harness for ESP32-S3 CircuitPython hardware modules. This is not host-side `pytest`; it is for serial-terminal hardware verification on the board.

## Before editing
Inspect existing files:
- Production `code.py`.
- Existing test files in root or `tests/`.
- `config.py` for pins and hardware constants.
- Hardware modules under `hardware/`.

## Workflow
1. Do not overwrite production `code.py` unless the user explicitly asks for a board-ready test launcher.
2. Prefer creating `tests/test_<component>.py` modules plus a documented copy/rename step.
3. If a board-ready launcher must replace `code.py`, first preserve or document the existing production entrypoint, for example `code_main.py`.
4. Create a menu launcher that runs test modules one at a time through the serial terminal.
5. Each test module should initialize only the hardware it needs, print clear status messages, run a short visible/audible/physical check, then clean up or return hardware to a safe state.
6. Use distinct prefixes such as `[TEST: lighting]` so serial output is easy to scan.
7. Use `config.py` names instead of hardcoded pins.

## Launcher pattern
A launcher may:
- List test modules.
- Ask the user to run, skip, or stop.
- Import one module at a time.
- Catch exceptions and continue safely.
- Enter a clear standby state when finished.

## Test module pattern
Each module should include:
- Imports at the top.
- Initialization.
- A small number of manual checks.
- Printed expected physical behavior.
- Cleanup or safe shutdown.

## Safety rules
- Keep tests short and reversible.
- Avoid leaving motors running, relays on, LEDs bright, or audio looping after a test.
- Explain any intentional blocking `input()` prompt in the launcher. Do not use blocking waits inside production runtime modules.
- When a new library is needed, update `requirements.txt`.

## Output checklist
After editing, include:
- Tests created.
- How to copy/run them on the board.
- Expected serial output.
- Physical behavior to verify.
- How to restore normal `code.py`.
