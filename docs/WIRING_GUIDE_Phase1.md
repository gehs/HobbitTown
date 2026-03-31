# HobbitTown Wiring & Connectivity Guide – Phase 1

## Overview

This guide provides a **build-up sequence** for wiring the diorama safely and methodically, starting with power infrastructure and simple components, then progressing to complex multi-wire systems. Each phase includes component specs, pin assignments, protective components, and validation steps.

---

## Phase 1: Power Infrastructure & Board Setup

### 1.1 Power Supply & Ground Bus

**Component:** Mean Well LRS-100-5 (18A 5V power supply)

**Power Budget:**
- Max total draw: 90W at 18A
- ESP32-S3: ~100 mA max
- WS2812B strip (300px @ full brightness): ~18A max
- SK6812 RGBW strip (144px @ full brightness): ~5.7A max
- PCA9685 (2 units) + servos: ~4A max
- Fogger relay: ~2A max
- Audio amplifiers: ~3A max

**Wiring Steps:**

1. **Main supply connector**: Mount a 5V power jack or Anderson connector on the diorama chassis.
   - Red wire (5V+) from LRS output
   - Black wire (GND) from LRS output
   - Ground the LRS chassis to the diorama frame for safety.

2. **Distribution bus**: Create a centralized 5V and GND rail using 10 AWG copper wire or bus bars.
   - 5V bus (RED): Main power distribution point
   - GND bus (BLACK): Return path for all ground connections

3. **ESP32-S3 Power**: Provide 5V and GND to the ESP32-S3 via USB or breadboard.
   - USB power is safe during development.
   - For final installation, use 5V bus + GND bus with a 100µF smoothing capacitor across the rails.

4. **Capacitors on power rails:**
   - **100µF electrolytic** (25V rated) across 5V/GND at the EP32-S3 power input.
   - **10µF ceramic** (25V rated) near each major component (PCA9685, audio amp, each LED strip).
   - Reason: Dampens voltage sag during inrush current (servos, LED changes).

---

### 1.2 Ground Connectivity

**Critical:** All grounds must be connected. Floating grounds cause noise and unreliable I2C/SPI communication.

**Wiring Steps:**

1. Connect GND from ESP32-S3 to the GND bus.
2. Connect GND from LRS-100-5 to the GND bus.
3. Connect GND from all subsystems (PCA9685, LED strips, audio amps, fogger relay) to the GND bus.
4. Use dedicated ground return wires; never rely on chassis conductivity alone.

---

### 1.3 Board Configuration Check (Dry-Load)

Before connecting external hardware, verify the board boots without errors.

**Steps:**

1. Connect ESP32-S3 to your computer via USB.
2. Open the CircuitPython REPL (Mu Editor or equivalent).
3. Run the test script:
   ```python
   import config
   print("Board Config OK: GPIO assignments loaded")
   print(f"  NEOPIXEL_PIN: {config.NEOPIXEL_PIN}")
   print(f"  I2C_SDA: {config.I2C_SDA}")
   print(f"  I2C_SCL: {config.I2C_SCL}")
   print(f"  FOGGER_RELAY_PIN: {config.FOGGER_RELAY_PIN}")
   ```

4. All pins should print successfully. If any raise exceptions, check CircuitPython version and board definitions.

---

## Phase 2: Lighting System

### 2.1 WS2812B Strip (Main LED Strip)

**Component Specs:**
- Type: WS2812B (5050 RGB addressable LEDs)
- Total count: 300 pixels
- Voltage: 5V
- Current per pixel: ~20 mA (at full white brightness)
- Max current for full strip: 300 × 20 mA = 6A
- Protocol: One-wire serial (NeoPixel protocol)
- Data rate: 800 kHz

**Pin Assignment (from `config.py`):**
- Data pin: **GPIO 2** (NEOPIXEL_PIN)

**Protective Components:**

1. **Data line resistor (470 Ω):**
   - Placement: Between GPIO 2 and the LED strip's DIN (data input) line.
   - Size: 1/4W resistor.
   - Purpose: Limits signal reflections and protects ESP32 GPIO from over-current.

2. **Smoothing capacitor (1000µF, 25V):**
   - Placement: Across 5V and GND at the LED strip's power input.
   - Reason: WS2812B draws large inrush currents during color changes. Capacitor buffers voltage sag.

3. **Diode (1N4007) — Optional but recommended:**
   - Placement: Inline with the 5V line feeding the LED strip (anode to supply, cathode to strip).
   - Purpose: Protects against reverse polarity if a connector is accidentally reversed.

**Wiring Steps:**

1. **5V power line:**
   - Strip positive wire → 1N4007 diode anode
   - Diode cathode → 1000µF capacitor positive (and 5V bus)
   - Capacitor negative → GND bus

2. **Data line:**
   - GPIO 2 → 470Ω resistor → LED strip DIN

3. **Ground:**
   - LED strip GND → GND bus

4. **Physical placement:**
   - Route data line away from power and motor wires to minimize EMI.
   - Separate data and power return paths if possible.

**Validation (Dry-Load):**

1. Enable lighting in `config.py`:
   ```python
   ENABLE_LIGHTING = True
   ```

2. Run the test:
   ```python
   import hardware.lighting as lighting
   lighting.setup_lighting()
   # Should print: "Lighting Controller: initialized"
   # (or "dry-load mode (...)" if strip not connected)
   ```

3. If strip is connected, test a simple color:
   ```python
   lighting.apply_lighting_preset(2)  # Day preset = white
   ```

---

### 2.2 SK6812 RGBW Strip (High-Density Light)

**Component Specs:**
- Type: SK6812 RGBW (4-in-1: Red, Green, Blue, White)
- Total count: 144 pixels (144 LEDs/meter = 1 meter strip)
- Voltage: 5V
- Current per pixel: ~24 mA (at full white, all four channels)
- Max current for strip: 144 × 24 mA = 3.5A
- Protocol: One-wire serial (compatible with WS2812B handling)
- Data rate: 800 kHz

**Pin Assignment (from `config.py`):**
- Data pin: **GPIO 4** (pin_high_density in lights.json)

**Protective Components:**
- Same as WS2812B: 470Ω data resistor, 1000µF capacitor, optional 1N4007 diode.

**Wiring Steps:**
- (Identical to WS2812B; use GPIO 4 instead of GPIO 2)

**Validation (Dry-Load):**
1. Enable lighting and connect strip.
2. Test via the test scene or direct color command.

---

## Phase 3: I2C Bus & PWM Drivers (PCA9685)

### 3.1 I2C Bus Setup

**Component:** Two PCA9685 PWM drivers at different I2C addresses (0x40 and 0x41).

**Pin Assignments (from `config.py`):**
- SDA (data): **GPIO 21**
- SCL (clock): **GPIO 47**
- Frequency: 100 kHz (standard I2C)

**Protective Components:**

1. **Pull-up resistors (4.7 kΩ × 2):**
   - One resistor: SDA (GPIO 21) to 5V
   - One resistor: SCL (GPIO 47) to 5V
   - Size: 1/4W resistor
   - Purpose: I2C requires open-drain drivers; pull-ups hold lines high when idle.

2. **Smoothing capacitor (10µF, 25V):**
   - Placement: Across 5V and GND at the PCA9685 power input.

3. **Series resistor (100Ω) — Optional:**
   - Placement: In-line with SCL and SDA lines (one per line).
   - Purpose: Limits current if multiple I2C masters or short circuits occur.

**Wiring Steps:**

1. **Power:**
   - PCA9685 VCC → 5V bus
   - PCA9685 GND → GND bus
   - 10µF capacitor across VCC/GND

2. **I2C lines:**
   - PCA9685 SDA → 4.7kΩ resistor to 5V (pull-up)
   - PCA9685 SDA → GPIO 21
   - PCA9685 SCL → 4.7kΩ resistor to 5V (pull-up)
   - PCA9685 SCL → GPIO 47
   - Optional: 100Ω series resistor on each line near the ESP32

3. **Address configuration (hardware):**
   - **PCA9685 #1 (address 0x40):** A0 pin to GND, A1 to GND, A2 to GND, A3 to GND
   - **PCA9685 #2 (address 0x41):** A0 pin to 5V, A1 to GND, A2 to GND, A3 to GND
   - (Check your PCA9685 pinout; address pins are typically solder jumpers or breakout legs.)

4. **Physical placement:**
   - Place resistors as close as possible to the PCA9685 or ESP32.
   - Keep I2C lines short (<1 meter recommended).

**Validation:**

1. Enable motion in `config.py`:
   ```python
   ENABLE_MOTION = True
   ```

2. Run the test:
   ```python
   import hardware.motion as motion
   motion.setup_hardware()
   # Should print: "Hobbit Town Hardware: initialized"
   # (or "dry-load mode (...)" if hardware not connected)
   ```

3. If PCA9685 boards are detected, test a PWM channel:
   ```python
   motion.set_door(1, 45)  # Move door 1 to 45 degrees
   ```

---

## Phase 4: Servos & Motion

### 4.1 Servo Motors (MG90S)

**Component Specs:**
- Type: MG90S micro servo
- Quantity: 4 (one for each door, one spare)
- Voltage: 4.8–6V (nominal 5V)
- Current stall: ~650 mA per servo
- Control: PWM at 50 Hz (20 ms period)
- Pulse range: 1000–2000 µs (approximately 150–600 µs on PCA9685)

**Pin Assignments (from `motion.py`):**
- Servo 1 (Smial 1 door): PCA9685 PWM channel 0
- Servo 2 (Smial 2 door): PCA9685 PWM channel 1
- Servo 3 (Smial 3 door): PCA9685 PWM channel 2
- Servo 4 (spare): PCA9685 PWM channel 3

**Protective Components:**

1. **Capacitor (100µF, 25V) per servo:**
   - Placement: Across 5V and servo GND near the servo connector.
   - Purpose: Absorbs inrush current spikes and prevents voltage sag.

2. **Servo power isolation (very important):**
   - Servo 5V and GND should come from the 5V bus directly.
   - Do NOT draw servo current through the PCA9685's 5V output pin (it has insufficient current capacity).

**Wiring Steps:**

1. **Power:**
   - Servo red wire → 100µF capacitor positive (and 5V bus)
   - Servo brown/black wire → Capacitor negative (and GND bus)

2. **Control signal:**
   - Servo yellow/orange wire → PCA9685 PWM channel N

3. **Multi-servo power distribution:**
   - Daisy-chain the servo 5V and GND wires using a bus layout (all reds to one 5V line, all browns to one GND line).
   - Add a 100µF capacitor for every 2 servos.

4. **Physical placement:**
   - Route servo power wires separately from signal and data lines.
   - Secure wires away from moving servo arms.

**Servo Angle Configuration (from `config.py`):**
```python
SERVO_MIN_PULSE = 150      # Micro seconds; corresponds to 0° (closed)
SERVO_MAX_PULSE = 600      # Micro seconds; corresponds to 180° (open)
DOOR_OPEN_ANGLE = 90       # Position for open door
DOOR_CLOSED_ANGLE = 0      # Position for closed door
```

**Testing:**

1. Set up servo power and control lines (see wiring above).
2. Run:
   ```python
   motion.set_door(1, 0)    # Door 1 closed
   motion.set_door(1, 90)   # Door 1 open
   motion.set_door(1, 45)   # Door 1 half-open
   ```

3. Observe smooth movement. If servo is jittery:
   - Check 100µF capacitor is present and fresh.
   - Verify servo power is coming from 5V bus, not PCA9685.

---

## Phase 5: Fogger Relay & Atmosphere

### 5.1 Fogger Control via Relay

**Component Specs:**
- Type: 5V DC relay (SPDT or DPDT)
- Coil voltage: 5V DC
- Coil current: ~70 mA
- Contact rating: Typically 30A @ 250V AC (more than adequate for a 12V fogger)

**Pin Assignment (from `config.py`):**
- Control pin: **GPIO 18** (FOGGER_RELAY_PIN)

**Protective Components:**

1. **Flyback diode (1N4007) — CRITICAL:**
   - Placement: Across the relay coil (cathode to coil positive, anode to coil negative).
   - Purpose: Prevents inductive kick when relay coil is de-energized. Without this, voltage spikes can damage the GPIO pin.

2. **Data line resistor (1 kΩ) — Recommended:**
   - Placement: Inline with GPIO 18 → relay coil.
   - Purpose: Limits current if GPIO is shorted to ground.

3. **Optional: NPN transistor (2N2222 or 2N7000):**
   - Only needed if the relay coil exceeds GPIO current limits (typically 12 mA continuous).
   - For a standard 5V relay (~70 mA coil), use a transistor stage.

**Wiring Steps (with NPN transistor):**

1. **Relay coil:**
   - Relay coil positive → 5V bus
   - Relay coil negative → NPN transistor collector

2. **Transistor driver:**
   - NPN transistor base → 1 kΩ resistor → GPIO 18
   - NPN transistor emitter → GND bus
   - NPN transistor collector → Relay coil negative (and diode anode)

3. **Flyback diode:**
   - Diode cathode → Relay coil positive (5V)
   - Diode anode → Relay coil negative (transistor collector)

4. **Relay contacts:**
   - Common → 12V fogger power source (positive)
   - Normally open (NO) → 12V fogger control wire
   - When relay activates, fogger power flows to the fogger unit.

**Validation:**

1. Enable atmosphere in `config.py`:
   ```python
   ENABLE_ATMOSPHERE = True
   ```

2. Test:
   ```python
   import hardware.atmosphere as atmosphere
   atmosphere.setup_atmosphere()
   # Should print: "Atmosphere ready" or similar
   ```

3. If relay is connected:
   ```python
   # Test file will activate fogger for 15 seconds
   # Listen for relay click and observe fog output
   ```

---

## Phase 6: Audio System (Optional – Advanced)

### 6.1 Adafruit Music Maker FeatherWing

**Component Specs:**
- Type: Adafruit Music Maker FeatherWing (3436)
- Chipset: VS1053b MP3/WAV codec
- Interface: SPI
- Output: 3W stereo amplifier built-in
- Power: 5V USB or external

**Wiring:** Follow Adafruit's official guide (SPI bus: MOSI, MISO, SCK, plus CS and reset pins).

(Full audio wiring is deferred to a separate `WIRING_AUDIO.md` due to complexity.)

---

## Validation Checklist

### Before enabling each subsystem:

- [ ] **Power:** All grounds connected to GND bus. 5V bus stable at 5.0V ±0.1V.
- [ ] **Lighting (WS2812B):**
  - [ ] 470Ω resistor between GPIO 2 and LED data line
  - [ ] 1000µF capacitor across 5V/GND at LED strip input
  - [ ] LED strip DIN, 5V, and GND properly wired
  - [ ] Enable `ENABLE_LIGHTING = True` in `config.py`
  - [ ] Run test and verify lights respond

- [ ] **I2C Bus:**
  - [ ] 4.7kΩ pull-up resistors on SDA (GPIO 21) and SCL (GPIO 47) to 5V
  - [ ] 10µF capacitor on PCA9685 power inputs
  - [ ] PCA9685 #1 at address 0x40, #2 at 0x41
  - [ ] Enable `ENABLE_MOTION = True`
  - [ ] Run test; console should report "initialized"

- [ ] **Servos:**
  - [ ] 100µF capacitor across 5V/GND for every 2 servos
  - [ ] Servo power from 5V bus (not PCA9685)
  - [ ] Servo control on correct PCA9685 channel
  - [ ] Test smooth movement at 0°, 45°, 90°

- [ ] **Fogger:**
  - [ ] 1N4007 diode across relay coil (protection)
  - [ ] Relay coil to 5V via GPIO 18 (with transistor if needed)
  - [ ] Relay contacts connected to fogger control line
  - [ ] Enable `ENABLE_ATMOSPHERE = True`
  - [ ] Test relay click and fog output

---

## Troubleshooting Quick Reference

| Symptom | Likely Cause | Fix |
|---------|--------------|-----|
| LED strip not responding | Missing 470Ω resistor or bad GPIO 2 connection | Check resistor; try GPIO 4 |
| I2C "Bus Error" | Missing pull-up resistors or loose wire | Verify 4.7kΩ resistors on SDA/SCL |
| Servo doesn't move | Servo power from PCA9685 instead of 5V bus | Rewire servo 5V directly to 5V bus |
| Servo jitter | Insufficient capacitor or noisy power supply | Add 100µF capacitor near servo |
| Fogger relay doesn't activate | Diode installed backwards or relay coil burnt | Verify diode polarity; test relay with 5V DC source |

---

## Next Steps

1. **Complete Phase 1–5 validation** using the REPL test commands above.
2. **Run the full hardware test scene** via:
   ```python
   from logic.test_scene import smial_test
   smial_test.start()
   ```
3. **Review [USAGE_Hardware_Test.md](USAGE_Hardware_Test.md)** for expected behavior.
4. **Proceed to audio wiring** once motion and atmosphere are stable (see future `WIRING_AUDIO.md`).

---

## References

- **ESP32-S3 GPIO pinout:** https://docs.espressif.com/projects/esp-idf/en/latest/esp32s3/hw-reference/esp32s3_devkitc_1_v1_pinout.csv
- **WS2812B datasheet:** https://cdn-shop.adafruit.com/datasheets/WS2812B.pdf
- **PCA9685 datasheet:** https://cdn-shop.adafruit.com/datasheets/PCA9685.pdf
- **MG90S servo specs:** https://eckstein-shop.de/MG90S-Servo-Specifications-En
- **CircuitPython NeoPixel library:** https://docs.circuitpython.org/projects/neopixel/en/latest/
