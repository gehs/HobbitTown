---
name: hobbit-town-pcb-wing
description: project-specific workflow for turning the HobbitTown ESP32-S3 CircuitPython breadboard build into a custom carrier, wing, or PCB interface board. Use when reviewing HobbitTown wiring, extracting pin usage from config.py or board_profile_hybrid.json, reconciling docs with code, planning EasyEDA/KiCad schematic blocks, identifying missing resistors, level shifters, capacitors, fuses, relays, MOSFETs, connector ratings, or producing a pre-fabrication review checklist for LEDs, Tsunami audio, PCA9685 motion, relays, fogger, and power distribution.
---

# HobbitTown PCB Wing

## Operating stance

Treat this as a carrier/wing PCB migration project, not a bare ESP32-S3 module design, unless the user explicitly requests a custom ESP32-S3 board. Preserve the existing UICPAL ESP32-S3-DevKitC-1 N16R8 dev board as a plug-in module to avoid unnecessary RF, USB, boot/reset, antenna, flash, and power-supply risk.

Prioritize evidence already present in the repo. Do not recommend copper, connectors, components, or PCB routing based only on memory. When the repo is available, inspect these first:

1. `config.py`
2. `board_profile_hybrid.json`
3. `docs/WIRING_Revised_Connections.md`
4. `docs/WIRING_AUDIO.md`
5. `.github/skills/board-pinout/SKILL.md`
6. existing hardware modules under `hardware/`

If these sources disagree, stop and present a reconciliation table before continuing.

## Critical source-of-truth rule

Use `config.py` and `board_profile_hybrid.json` as the primary machine-readable sources, but do not blindly trust either. Cross-check them against wiring docs and hardware modules before producing PCB-ready outputs.

Known issue to check first: `config.py` may assign `NEOPIXEL_GROUND_PIN = board.GPIO5` and `NEOPIXEL_STREAM_PIN = board.GPIO6`, while `board_profile_hybrid.json` and the revised wiring guide may describe GPIO5 as stream and GPIO6 as ground. Flag this as a blocker until reconciled.

## Required companion skills / repo instructions

When working inside the HobbitTown repo:

- Use the `board-pinout` skill before changing or recommending pins.
- Use the `tsunami-audio-control` skill for Tsunami serial control, output routing, track ranges, or audio command framing.
- Use `new-hardware` when adding or revising CircuitPython hardware modules.
- Preserve `board.GPIO<n>` CircuitPython naming. Do not convert to `D<n>`, `IO<n>`, or raw integer GPIO names.

## Workflow

### 1. Build the evidence table

Create a project hardware table with one row per signal, output, bus, or power branch:

| Function | Source constant | GPIO / interface | Destination | Voltage domain | Direction | Current path | PCB treatment | Evidence | Open question |
|---|---|---|---|---|---|---|---|---|---|

Include power-only outputs even if no GPIO controls them. Include speakers/exciters as audio-power loads, not GPIO loads.

### 2. Reconcile conflicts

Before schematic planning, compare:

- `config.py` constants
- `board_profile_hybrid.json` configured names and connected hardware
- wiring guide tables
- hardware modules importing the constants

Produce:

- `confirmed`: safe to carry into PCB design
- `conflicting`: must be resolved before fabrication
- `unknown`: requires bench measurement or user confirmation
- `deprecated`: present in old code/docs but not current design

Do not continue to a fabrication-ready checklist if any PCB-affecting conflict remains.

### 3. Convert wiring to schematic blocks

Organize the carrier board into these blocks unless the repo evidence says otherwise:

1. ESP32-S3 dev board headers / socket footprint
2. main 5 V power input and distribution
3. NeoPixel output bank
4. I2C / PCA9685 motion connector
5. Tsunami UART/audio-control connector
6. amplifier/audio output connectors or module mounts
7. chimney/fogger relay-control connector block
8. test pads, labels, jumpers, and debug headers

Keep schematic blocks separate from board layout notes. Never jump directly from code to PCB routing.

### 4. Apply electrical rules

Load `references/electrical-rules.md` before recommending components. Do not invent exact current ratings, fuse sizes, speaker impedance limits, or supply limits; state when values require measurement, datasheet lookup, or part confirmation.

### 5. Design for one intentional prototype

Recommend a generous first prototype rather than a dense final board:

- larger board
- labeled connectors
- test pads on every GPIO-derived signal and power rail
- solder jumpers for uncertain signals
- optional footprints for protection components
- spare connector pins for GND and future use
- mounting holes and strain relief

The goal is one deliberate prototype that is close to the final board, not repeated production spins.

## Output modes

### Pin/component extraction

Return:

1. source files inspected
2. extracted pin map
3. conflicts and uncertainties
4. signals ready for schematic
5. signals blocked from PCB finalization

### PCB planning

Return:

1. carrier-board architecture
2. schematic blocks
3. connector proposal
4. protection/component proposal
5. power-distribution assumptions
6. review checklist
7. unresolved questions that affect copper

### Pre-fabrication review

Return the checklist in this order:

1. source-of-truth reconciliation
2. GPIO and boot/strap risk
3. voltage-domain review
4. power/current review
5. LED data integrity
6. audio/noise review
7. relay/inductive load review
8. connector and mechanical review
9. fabrication/BOM risk
10. bench-test plan for the prototype

## Tooling guidance

Use EasyEDA/JLCPCB-style component availability notes when the user wants a board assembled through that flow. Use KiCad-style neutral footprints when the user wants portable design files. In either case, keep the authoritative design intent in repo markdown tables so the schematic can be reviewed before layout.

If asked to create files, prefer these repo paths:

- `.github/skills/pcb-wing-carrier/SKILL.md`
- `.github/agents/pcb-wing.agent.md`
- `docs/PCB_CARRIER_BOARD_KICKOFF.md`
- `docs/PCB_CARRIER_REVIEW_CHECKLIST.md`

## Safety boundaries

Do not claim a board is fabrication-ready unless the repo sources are reconciled and the user has confirmed the exact board, connectors, power supplies, amplifier modules, speaker impedance/load wiring, LED strip type, and maximum LED brightness/current assumptions.

Never recommend driving speakers, relay coils, motors, foggers, solenoids, or high-current loads directly from ESP32 GPIO.
