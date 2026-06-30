---
name: pcb-wing-carrier
description: Plans and reviews a HobbitTown ESP32-S3 carrier/wing PCB from the existing CircuitPython code, board_profile_hybrid.json, config.py, and wiring docs. Use when converting breadboard wiring to schematic blocks, connector tables, EasyEDA/KiCad design notes, BOM/protection recommendations, or fabrication readiness checklists. Always reconcile code, board profile, and wiring docs before producing PCB-ready labels or net names.
---

# PCB Wing Carrier

## Purpose

Help convert the current HobbitTown breadboard wiring into a clean carrier/wing PCB while preserving the known-good ESP32-S3 dev board and existing CircuitPython architecture.

This skill does **not** design a bare ESP32-S3 board. Assume the first custom PCB is a carrier board for the UICPAL ESP32-S3-DevKitC-1 unless the user explicitly changes scope.

## Required source files

Read these before making PCB recommendations:

1. `config.py`
2. `board_profile_hybrid.json`
3. `docs/WIRING_Revised_Connections.md`
4. `docs/WIRING_AUDIO.md`
5. `.github/skills/board-pinout/SKILL.md`
6. relevant modules in `hardware/`

If sources disagree, produce a reconciliation table and stop before PCB-ready recommendations.

## First blocker to check

Check GPIO5/GPIO6 mapping before any schematic or connector-label work.

Known possible conflict:

- `config.py` may define `NEOPIXEL_GROUND_PIN = board.GPIO5` and `NEOPIXEL_STREAM_PIN = board.GPIO6`.
- `board_profile_hybrid.json` and/or wiring docs may identify GPIO5 as stream and GPIO6 as ground.

Do not label a connector, schematic net, PCB silkscreen, or cable harness for Stream/Ground LEDs until this is resolved.

## Required routing to other skills

- Use `board-pinout` before recommending or changing any pin.
- Use `tsunami-audio-control` for Tsunami serial, audio output mapping, WAV track routing, or UART command details.
- Use `new-hardware` if code changes are needed for new modules, pin constants, or safe hardware initialization.
- Use `lighting-management` for LED segment/preset logic.
- Use `tech-manual` when generating user-facing wiring documentation.

## Workflow

1. Extract all `board.GPIO` constants from `config.py`.
2. Compare those constants to `board_profile_hybrid.json` configured names.
3. Compare both to `docs/WIRING_Revised_Connections.md` and `docs/WIRING_AUDIO.md`.
4. Produce a status for every interface: `confirmed`, `conflict`, `unknown`, `deprecated`, or `not pcb relevant`.
5. Convert confirmed interfaces into schematic blocks.
6. Create connector tables only for confirmed interfaces.
7. Identify missing components: level shifters, resistors, capacitors, fuses, protection parts, drivers, connectors, jumpers, and test pads.
8. Produce a prototype-first PCB review checklist.

## Schematic block defaults

Use these default blocks unless current repo evidence says otherwise:

- ESP32-S3 dev board socket/header block
- 5 V input and power distribution block
- NeoPixel output block
- I2C/PCA9685 motion block
- Tsunami UART control block
- audio amplifier/output block
- chimney/fogger relay-control block
- test/debug block

## Electrical rules

- ESP32-S3 GPIO is 3.3 V logic.
- Do not drive speakers, relay coils, motors, foggers, solenoids, or high-current loads directly from GPIO.
- NeoPixel-style 5 V LED data should use a 5 V powered logic buffer/level shifter plus one series resistor per data line.
- Put bulk capacitance near LED strip power outputs and amplifier/module power inputs.
- Confirm I2C pull-ups before adding duplicates.
- Treat speaker outputs as amplifier outputs, not GPIO outputs.
- Do not put flyback diodes across speaker outputs.
- If using relay modules, confirm they include input drivers/flyback protection. If using bare relays, require a transistor/MOSFET driver and flyback diode.
- Keep relay/load wiring away from audio, UART, I2C, and LED data.
- Add test pads for every signal and power rail that matters.

## Output contract

For PCB planning, respond in this order:

1. Sources inspected
2. Conflicts or blockers
3. Confirmed interfaces
4. Schematic block plan
5. Connector table
6. Protection/component recommendations
7. Power/current assumptions and unknowns
8. Prototype PCB features
9. Pre-fabrication checklist
10. Bench-test sequence

Never claim the design is fabrication-ready while source conflicts or load/current unknowns remain.
