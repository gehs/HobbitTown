# Folder Structure And Naming

This project uses a role-based structure so runtime behavior stays clear and safe on the ESP32-S3.

## Core Rule

- hardware = direct device control modules (drivers/adapters)
- logic = orchestration/state-machine modules (scenes, web flow, timing helpers)
- tests = executable test launchers and bench validation scripts
- ref = runtime reference data files used by code
- docs = human-readable design, wiring, and operating guidance

## Why hardware has many Python files

Python files in hardware are expected. Those modules talk to physical subsystems:
- LEDs
- audio board protocol
- motion/PCA9685
- relays/fog

They should stay focused on low-level control and safe defaults.

## Why logic also has Python files

Logic modules coordinate behavior across hardware modules:
- full run sequences
- certification scenes
- web control routing
- timing helpers

They should avoid pin-level details and use hardware/config interfaces.

## Test Naming Rule

To avoid confusion with tests folder:
- Runtime orchestration files in logic should not use ambiguous names like test_scene.py.
- Prefer names like certification_scene.py or demo_scene.py for runtime scenes.
- Keep test launchers and bench scripts in tests/.

## Current Runtime Scene Naming

- logic/full_run_scene.py
- logic/certification_scene.py
- logic/certification_dry_run_scene.py

## Quick Placement Checklist

If a new file:
- directly controls pins, UART, I2C, NeoPixels, relays, servos: put it in hardware
- coordinates multiple modules over time: put it in logic
- is a one-off validation launcher or operator test script: put it in tests
- stores runtime data maps/config JSON: put it in ref
- explains decisions, wiring, and usage: put it in docs
