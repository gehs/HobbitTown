# HobbitTown PCB Carrier Board Kickoff

## Purpose

This document starts the migration from the working breadboard build to a custom ESP32-S3 carrier/wing PCB. The first PCB should reduce wiring while preserving the existing UICPAL ESP32-S3-DevKitC-1 N16R8 dev board as a plug-in controller.

## Fabrication-readiness rule

Do not order a PCB until `config.py`, `board_profile_hybrid.json`, and wiring docs agree on every PCB-affecting signal.

## First reconciliation item

Resolve the GPIO5/GPIO6 LED mapping before schematic capture:

| Source | GPIO5 | GPIO6 | Status |
|---|---|---|---|
| `config.py` | check current `NEOPIXEL_*` assignment | check current `NEOPIXEL_*` assignment | must verify |
| `board_profile_hybrid.json` | check configured_names | check configured_names | must verify |
| `docs/WIRING_Revised_Connections.md` | check LED strip table | check LED strip table | must verify |

Do not create final connector labels or silkscreen for Stream/Ground LED outputs until this is resolved.

## Proposed schematic blocks

| Block | Purpose | Initial notes |
|---|---|---|
| ESP32-S3 header/socket | Receives the existing dev board | Avoid bare ESP32-S3 design in first spin |
| Main 5 V input | Power entry and distribution | Include fuse/reverse/keying strategy |
| NeoPixel output bank | Three LED data/power outputs | Level shift data, series resistors, bulk caps |
| I2C/PCA9685 connector | Motion control bus | Verify pull-ups and connector pinout |
| Tsunami UART connector | Audio controller serial link | GPIO17 TX to Tsunami RXI, GPIO18 RX from TXO |
| Audio module area | Speaker/exciter amplifier connections | Treat speakers as amp outputs, not GPIO loads |
| Relay-control bank | Chimney/fogger relay module inputs | Confirm relay modules include drivers/flyback |
| Test/debug pads | Bring-up and troubleshooting | Add pads for every signal/power rail |

## Interface table template

| Connector | Pin | Net | Voltage | Direction | Destination | Protection/series part | Current rating | Test pad |
|---|---:|---|---|---|---|---|---|---|

## Prototype-first design features

- Large enough board to inspect and rework.
- Clear silkscreen labels at every connector.
- Test pads for each signal and power rail.
- Optional footprints for uncertain protection parts.
- Solder jumpers where a source conflict or future choice may exist.
- Spare grounds near noisy or long-wire interfaces.
- Mounting holes and strain relief considerations.

## Information needed before layout

- Exact connector families and wire gauges.
- Maximum intended LED brightness and worst-case current assumption.
- Exact amplifier modules and speaker/exciter impedance wiring.
- Relay module input type and whether modules include flyback protection.
- Mechanical envelope, mounting holes, cable exit directions, and board orientation.
