---
name: board-pinout
description: Validates and optimizes ESP32-S3 dev board pin assignments for the HobbitTown CircuitPython project using hardware/board_profile.json. Use when asked to assign pins, review wiring, generate config.py pin constants, avoid nonexistent pins, reduce wiring crossovers, check reserved or risky pins, select UART/I2C/GPIO/PWM/ADC-capable pins, or update project pin assignments. Always use board.GPIO-style CircuitPython names from the board profile.
---

# Board Pinout

## Purpose

Prevent incorrect, nonexistent, unsafe, conflicting, or inefficient pin recommendations for the HobbitTown ESP32-S3 project.

Use this skill before any other skill recommends or changes pins.

This skill reads `hardware/board_profile_hybrid.json` as the source of truth for:

- exposed board pins
- CircuitPython pin names
- physical board side and header position
- available capabilities
- current project assignments
- reservation status
- known test status
- routing zones
- wiring efficiency notes
- pins to avoid

## Required Source File

Before recommending any pin, inspect:

```text
board_profile_hybrid.json
```

If the file is missing, ask the user to provide it or create a minimal board profile before assigning pins.

Do not recommend pins from memory.

Do not invent pins.

Do not use generic ESP32-S3 pinout assumptions unless the board profile hybrid explicitly marks the pin as exposed and usable.

## CircuitPython Naming Rule

This project uses `board.GPIO<n>` naming.

Correct examples:

```python
TSUNAMI_TX_PIN = board.GPIO17
TSUNAMI_RX_PIN = board.GPIO18
SKY_NEOPIXEL_PIN = board.GPIO4
```

Incorrect examples:

```python
TSUNAMI_TX_PIN = board.IO17
TSUNAMI_RX_PIN = board.IO18
SKY_NEOPIXEL_PIN = board.D4
```

Generated CircuitPython code must use the exact `circuitpython_name` value from `board_profile_hybrid.json`.

Do not convert `GPIO` names into `IO`, `D`, raw integers, or Arduino-style aliases.

## Pin Recommendation Rules

Only recommend a pin when all of the following are true:

1. The pin exists in `board_profile_hybrid.json`.
2. The pin has a valid `circuitpython_name`.
3. The pin is exposed on the dev board header.
4. The pin is not marked `reserved`, `avoid`, `do_not_use`, or equivalent.
5. The pin is not already assigned unless the requested function can safely share it.
6. The pin has the required capability for the requested use.
7. The pin does not conflict with boot mode, USB serial, onboard LEDs, flash/PSRAM, or known failed behavior.
8. The recommendation considers physical wiring efficiency.

If no safe pin exists, say so clearly. Do not guess.

## Assignment Status

Use assignment status to avoid losing known-good work.

Preferred statuses:

```text
unassigned
proposed
proven_isolated
proven_full_system
reserved
avoid
do_not_use
```

Interpretation:

- `unassigned`: available candidate if capabilities match.
- `proposed`: suggested but not tested yet.
- `proven_isolated`: tested successfully by itself, but not yet tested with all peripherals connected.
- `proven_full_system`: tested successfully with the full peripheral set connected.
- `reserved`: intentionally held for a known purpose.
- `avoid`: avoid unless the user explicitly overrides.
- `do_not_use`: do not recommend.

Do not replace a `proven_isolated` or `proven_full_system` assignment merely because another pin might be tidier. Instead, present a migration recommendation with tradeoffs.

## Wiring Efficiency Rules

When multiple safe pins are possible, prefer the pin that improves physical wiring.

Consider:

- same board side as the peripheral connector
- nearest header position
- fewer wire crossings
- grouping related signals together
- keeping UART TX/RX adjacent when possible
- keeping I2C SDA/SCL adjacent when possible
- keeping NeoPixel data lines away from noisy relay wiring when possible
- separating high-current relay/power wiring from sensitive signal wiring
- preserving flexible pins for future peripherals

Use `header_side`, `header_position`, `routing_zone`, and `bundle` fields from `board_profile.json` when present.

## Peripheral-Specific Guidance

### UART

For UART devices:

- Assign TX and RX as a pair.
- Prefer pins with `uart_tx` and `uart_rx` capability when identified.
- Keep TX/RX physically close where possible.
- Label direction clearly:
  - ESP32 TX connects to peripheral RX.
  - ESP32 RX connects to peripheral TX.
- Do not use USB serial pins unless the board profile explicitly allows it.

### I2C

For I2C devices:

- Prefer the existing project I2C bus if available.
- Do not create a second I2C bus unless there is a clear reason.
- SDA and SCL may be shared by multiple I2C devices.
- Check address conflicts separately.
- Recommend pull-ups only when the project hardware does not already provide them.

### NeoPixel / Addressable LEDs

For NeoPixel or one-wire LED data:

- Use a normal digital output pin.
- Avoid boot, USB, onboard LED, reserved, or known failed pins.
- Prefer pins already tested for LED data when adding segments to the same lighting system.
- Note level-shifting and data-line resistor requirements when relevant.

### Relays, Motors, Solenoids

For relays or inductive loads:

- Use digital output pins only.
- Do not power coils directly from GPIO.
- Require a driver/transistor/MOSFET or relay module input as appropriate.
- Keep relay wiring physically separated from sensitive audio, I2C, and NeoPixel data where possible.

### ADC / Analog Sensors

For analog sensors:

- Require `analog_in` capability.
- Prefer ADC1 pins when possible.
- Avoid pins already assigned to timing-sensitive outputs.

## Output Format

When recommending pins, provide a table:

| Function | Recommended pin | CircuitPython name | Status | Reason | Caution |
|---|---|---|---|---|---|

Also include a short wiring note when useful:

```text
ESP32 GPIO17 TX -> Tsunami RX
ESP32 GPIO18 RX -> Tsunami TX
Common GND required
```

## Review Mode

When asked to review existing assignments:

1. Load all current assignments from `board_profile_hybrid.json`.
2. Identify:
   - nonexistent pins
   - wrong CircuitPython names
   - duplicate assignments
   - reserved pin use
   - risky pins
   - current status: isolated-tested or full-system-tested
   - wiring crossover opportunities
3. Preserve working assignments unless there is a clear safety, conflict, or routing reason to change them.
4. Produce:
   - keep list
   - change candidates
   - avoid list
   - test plan

## Config.py Rule

When generating or updating `config.py`, use constants that point to board-profile names.

Example:

```python
import board

SKY_NEOPIXEL_PIN = board.GPIO4
STREAM_NEOPIXEL_PIN = board.GPIO5
TSUNAMI_TX_PIN = board.GPIO17
TSUNAMI_RX_PIN = board.GPIO18
I2C_SDA_PIN = board.GPIO8
I2C_SCL_PIN = board.GPIO9
```

Do not use raw integers for CircuitPython pin constants.

## Full-System Test Planning

Because isolated tests do not prove the full wiring set works together, recommend a staged test plan:

1. Confirm boot with all peripherals connected but inactive.
2. Confirm serial console remains usable.
3. Test I2C scan.
4. Test each NeoPixel chain at low brightness.
5. Test each relay one at a time.
6. Test Tsunami UART send-only command.
7. Test Tsunami UART bidirectional status, if RX is connected.
8. Test combined scene behavior with all peripherals connected.
9. Promote pins from `proven_isolated` to `proven_full_system` only after successful combined testing.

## Common Mistakes to Avoid

- Do not recommend `board.IO<n>` for this project.
- Do not recommend Arduino-style `D<n>` names.
- Do not recommend raw integer pins in CircuitPython code.
- Do not use pins absent from `hardware/board_profile_hybrid.json`.
- Do not reuse a pin unless the bus or signal type is explicitly shareable.
- Do not use boot, USB, onboard LED, reserved, or previously failed pins without a clear user override.
- Do not optimize for neat wiring at the expense of a proven safe assignment.
- Do not assume all ESP32-S3 GPIOs are exposed on this specific dev board.
- Do not forget common ground between external modules and the ESP32-S3.