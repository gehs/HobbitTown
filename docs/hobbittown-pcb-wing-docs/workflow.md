# Carrier PCB migration workflow

## Phase 0: freeze the working prototype

Capture the known-good breadboard state before making PCB decisions.

Required outputs:

- current `config.py` pin map
- current `board_profile_hybrid.json` pin assignments
- wiring-guide reconciliation table
- photos or written notes for external connectors and cable directions when available

## Phase 1: extract and reconcile

1. Extract all `board.GPIO<n>` constants from `config.py`.
2. Extract assigned pins from `board_profile_hybrid.json`.
3. Compare against wiring docs.
4. Mark each signal as confirmed, conflicting, unknown, deprecated, or not-PCB-relevant.

Blocker rule: do not create final connector labels or schematic net names for conflicting signals.

## Phase 2: define interfaces

Convert subsystems into board interfaces:

- ESP32-S3 dev-board header interface
- LED output connector bank
- I2C/PCA9685 connector
- Tsunami UART connector
- audio module/amp connector area
- relay-control connector bank
- power input and distribution
- test/debug interface

Every connector needs:

- exact signal names
- voltage
- direction
- expected current or current unknown marker
- cable destination
- connector family proposal
- protection components
- test method

## Phase 3: schematic block review

Before PCB layout, provide a schematic block table:

| Block | Nets | Components | Connector | Why included | Open risks |
|---|---|---|---|---|---|

Make the user approve the block architecture before converting to layout advice.

## Phase 4: prototype layout intent

Recommend layout intent, not CAD-specific operations:

- group LED connectors with data resistors and level shifter nearby
- keep power distribution wide and direct
- keep audio line-level and UART away from relay/load wiring
- put relay-control connectors on the side closest to relay wiring
- put clear silkscreen labels by every connector
- expose test pads near each subsystem
- provide spare GND pins in connector banks where useful

## Phase 5: pre-fab checklist

Require a full checklist before ordering:

- repo-source reconciliation complete
- ERC/DRC clean or waivers documented
- connector pinouts reviewed against real cables
- power/current calculations documented
- trace widths checked
- silkscreen labels checked
- mounting holes and board outline checked
- BOM parts available
- optional footprints and jumpers documented
- bench-test sequence ready
