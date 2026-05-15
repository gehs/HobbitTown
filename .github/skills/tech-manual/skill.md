---
name: tech-manual
description: Write beginner-friendly HobbitTown hardware documentation, wiring guides, and safety notes for ESP32-S3 CircuitPython components. Use when asked about wiring, pin choice, voltage, current draw, external power, resistors, capacitors, flyback diodes, level shifting, grounding, or physical installation of sensors, servos, motors, relays, LEDs, speakers, amplifiers, and displays.
---

# Tech Manual

## Goal
Create clear, cautious hardware documentation for a hobbyist building an ESP32-S3 CircuitPython diorama.

## Critical safety rule
Do not invent exact electrical limits. If the exact part number or datasheet is not available, label values as estimates and ask the user to confirm the module. Always choose conservative power guidance.

## Workflow
When asked for a wiring guide or tech manual, create or update a document in `docs/`, for example `docs/wiring_servo.md`.

Use this structure:

```markdown
# Wiring Guide: <component>

## Component overview
Plain-English description of what it does.

## Assumptions
Board, component part number, supply voltage, and any unknowns.

## ESP32-S3 pin assignment
Recommended pin type, pins to avoid, and why.

## Power and current
Expected current draw, whether external power is required, and grounding rules.

## Protective components
- Resistors
- Diodes
- Capacitors
- Level shifting
- Fuses or current limiting when relevant

## Step-by-step wiring
Every connection: power, ground, signal/data, enable, and shared ground.

## CircuitPython notes
Libraries, config names, and testing approach.

## Safety checklist
What to verify before powering the circuit.
```

## Guidance standards
- Explain why each protective component matters.
- Emphasize common-ground requirements when using external power.
- Warn that ESP32-S3 GPIO pins are signal pins, not power supplies for motors, long LED strips, relays, or speakers.
- For NeoPixels/LED strips, consider a data-line resistor, power-injection needs, and a smoothing capacitor across power leads when appropriate.
- For motors, solenoids, and relays, consider flyback protection unless the driver board already includes it.
- For 5V logic devices, consider whether level shifting is needed.

## Output checklist
Include:
- Parts list.
- Wiring steps.
- Power warning.
- First-power test procedure.
- Follow-up question for unknown part numbers if needed.
