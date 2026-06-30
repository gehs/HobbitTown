# Electrical rules for HobbitTown carrier PCB planning

## General

- Treat ESP32-S3 GPIO as 3.3 V logic.
- Do not connect 5 V signals directly to ESP32 GPIO.
- Use common ground between ESP32, LED strips, PCA9685, Tsunami, amplifiers, relay modules, and power supply.
- Do not let signal wires act as current return paths for LED strips, amplifiers, relays, foggers, servos, or exciters.
- Add test pads for every signal leaving the ESP32 dev board and for 5 V, 3.3 V, and GND.

## Power

- Separate logic distribution from high-current load distribution in the schematic and layout.
- Size connectors and traces from actual maximum current, not average current.
- Use a main fuse or replaceable protection element on the primary 5 V input.
- Consider per-branch protection for LED power branches and external load branches.
- Include reverse-polarity protection or a keyed input connector when practical.
- Include bulk capacitance near LED strip power outputs and amplifier/module power inputs.
- Keep high-current grounds and audio/signal grounds intentionally routed to the common ground system.

## Addressable LEDs

- Use a 5 V tolerant / 5 V powered logic buffer or level shifter for NeoPixel-style data lines when strips are powered at 5 V.
- Use one data-line series resistor per strip near the board connector, commonly in the 300 to 500 ohm range unless the user has selected a specific value.
- Provide bulk capacitance across 5 V/GND for each LED power branch.
- Keep LED data traces away from relay coil/load wiring and high-current amplifier traces.
- Do not casually low-side-switch LED strip ground. If LED branch switching is required, use an intentional high-side/load-switch design and handle data-line back-powering risk.

## I2C / PCA9685

- Share SDA/SCL only among I2C devices.
- Verify pull-ups. PCA9685 breakout boards often include pull-ups; bare-chip designs need explicit pull-ups to the correct logic voltage.
- Put I2C connector pins in a predictable order such as GND, VCC, SDA, SCL, with silkscreen labels.

## Audio

- ESP32 controls Tsunami over UART only; do not introduce SPI/I2S audio paths unless the user explicitly changes architecture.
- Treat speaker outputs as amplifier outputs, not GPIO outputs.
- Do not put flyback diodes across speaker outputs.
- Keep audio line-level traces away from relay wiring, LED power, and switching supply noise.
- Verify amplifier supply voltage, output topology, speaker impedance, and parallel speaker wiring before committing connector count or trace width.

## Relays / inductive or switched loads

- Relay coils must not be driven directly from GPIO.
- If using relay modules, confirm the module has an input driver and flyback protection.
- If using bare relays, require a transistor/MOSFET driver and flyback diode across the coil.
- Label relay connectors by controlled load and by control signal.
- Keep relay/load power wiring physically separated from LED data, I2C, UART, and audio signals.

## MOSFETs and diodes

- Add MOSFETs only for intentional power switching or load driving, not as decorative protection.
- Match MOSFET gate threshold and Rds(on) to 3.3 V drive if controlled directly by ESP32.
- Use flyback diodes for inductive DC coils, not for speakers or simple LED data lines.
- Use TVS/ESD protection where long external wires may be handled, unplugged, or routed outside the enclosure.
