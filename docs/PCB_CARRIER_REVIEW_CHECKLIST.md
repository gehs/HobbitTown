# HobbitTown PCB Carrier Review Checklist

Use this before schematic capture, layout review, and fabrication ordering.

## 1. Source reconciliation

- [ ] `config.py` GPIO constants extracted.
- [ ] `board_profile_hybrid.json` configured names extracted.
- [ ] `docs/WIRING_Revised_Connections.md` checked against code/profile.
- [ ] `docs/WIRING_AUDIO.md` checked against code/profile.
- [ ] GPIO5/GPIO6 Stream/Ground LED mapping resolved.
- [ ] Deprecated wiring assumptions identified.

## 2. GPIO / boot / pin risk

- [ ] Every GPIO appears in `board_profile_hybrid.json`.
- [ ] No nonexistent or wrong CircuitPython pin names.
- [ ] No USB serial, boot, onboard LED, failed, reserved, or do-not-use pins used unintentionally.
- [ ] `board.GPIO<n>` naming preserved.
- [ ] Pin changes reflected in both `config.py` and board profile.

## 3. Voltage domains

- [ ] ESP32 GPIO protected from 5 V signals.
- [ ] NeoPixel data level shifting included where LED strips are powered at 5 V.
- [ ] I2C pull-up voltage verified.
- [ ] UART voltage compatibility verified for Tsunami.

## 4. Power/current

- [ ] Main power input rating confirmed.
- [ ] Main fuse/protection strategy selected.
- [ ] LED worst-case current documented.
- [ ] Amplifier supply voltage and current documented.
- [ ] Relay/fogger module power documented.
- [ ] Trace widths and connector ratings checked against current.
- [ ] Bulk and local decoupling capacitors placed.

## 5. LED data integrity

- [ ] One level-shifted data channel per LED strip.
- [ ] One series resistor per LED data output.
- [ ] Bulk capacitor near each LED power branch.
- [ ] LED connectors clearly label 5V, GND, DATA, and direction.
- [ ] LED data traces kept away from relay/high-current wiring.

## 6. Audio/noise

- [ ] Tsunami UART TX/RX direction labeled correctly.
- [ ] Audio line-level routing kept away from relay and LED power wiring.
- [ ] Speaker/exciter outputs treated as amplifier outputs.
- [ ] No flyback diodes across speaker outputs.
- [ ] Amplifier module power decoupling included.

## 7. Relays / switched loads

- [ ] Relay coils are not driven directly from GPIO.
- [ ] Relay modules confirmed to include input drivers/flyback, or driver circuit added.
- [ ] Fogger relay GPIO39 boot behavior considered; GPIO47 backup noted if needed.
- [ ] Relay wiring physically separated from sensitive signals.

## 8. Connectors and mechanics

- [ ] Connector orientation checked against cable exit direction.
- [ ] Pin 1 markings and labels visible.
- [ ] Keyed connectors used where reversal would be damaging.
- [ ] Mounting holes match enclosure/mechanical plan.
- [ ] Strain relief or cable anchoring considered.

## 9. Fabrication / BOM

- [ ] ERC/DRC reviewed.
- [ ] BOM components available from chosen supplier.
- [ ] Footprints verified against datasheets.
- [ ] Optional footprints and jumpers documented.
- [ ] Silkscreen checked for every connector and test pad.

## 10. Prototype bring-up

- [ ] Power-only test planned before plugging ESP32 dev board.
- [ ] 5 V and 3.3 V rails measured.
- [ ] Continuity/short test planned for each connector.
- [ ] LED data outputs tested one strip at a time.
- [ ] I2C scan planned for PCA9685.
- [ ] UART test planned for Tsunami.
- [ ] Relay tests planned one output at a time.
- [ ] Audio tests planned at low volume first.
