# HobbitTown Revised Connection Guide — Full Breadboard Test

> **Version:** 1.0 — May 2026
> **Board:** UICPAL ESP32-S3-DevKitC-1 (N16R8) running CircuitPython
> **Source of truth:** `board_profile_hybrid.json`, `config.py`

This guide documents the **optimized pin layout** for wiring a full-project breadboard test. All pin assignments have been reorganized to group related functions on the same board header side using consecutive pins.

---

## Beginner Bench Rules

1. **Power OFF** before changing any wire.
2. Use a **shared ground bus** for everything.
3. **Label wires** before plugging them in.
4. Add only **one new connection at a time**.
5. If anything gets **hot**, power off immediately.
6. Wire one subsystem at a time and **test after each** before adding more.

---

## Board Header Diagram

USB port is at the **top** of the board. Pin 1 is nearest the USB connector on each side.

```
                    ┌──────────────┐
                    │  Main Chip   │
         ┌──────────┤              ├──────────┐
         │          └──────────────┘          │
    LEFT │                                    │ RIGHT
    SIDE │                                    │ SIDE
         │                                    │
  1  GND ├────────────────────────────────────┤ GND   1
  2  3V3 ├────────────────────────────────────┤ GPIO1 2   (available)
  3  RST ├────────────────────────────────────┤ GPIO2 3   (available — freed)
  4  G4  ├─ NEOPIXEL_SKY_PIN ─────────────────┤ G43   4   (USB serial TX — do not use)
  5  G5  ├─ NEOPIXEL_STREAM_PIN ──────────────┤ G44   5   (USB serial RX — do not use)
  6  G6  ├─ NEOPIXEL_GROUND_PIN (NEW) ────────┤ G42   6 ─ CHIMNEY_RELAY_PIN1 (NEW)
  7  G7  ├─ (available) ──────────────────────┤ G41   7 ─ CHIMNEY_RELAY_PIN2
  8  G15 ├─ (available) ──────────────────────┤ G40   8 ─ CHIMNEY_RELAY_PIN3
  9  G16 ├─ (available) ──────────────────────┤ G39   9 ─ FOGGER_RELAY_PIN (NEW)
 10  G17 ├─ AUDIO_UART_TX ────────────────────┤ G38  10   (available)
 11  G18 ├─ AUDIO_UART_RX ────────────────────┤ G37  11   (available)
 12  G8  ├─ I2C_SDA ──────────────────────────┤ G36  12   (available)
 13  G19 ├─ (failed — do not use) ────────────┤ G35  13   (reserved — do not use)
 14  G20 ├─ (USB D+ — avoid)  ────────────────┤ G0   14   (BOOT — do not use)
 15  G3  ├─ (available) ──────────────────────┤ G45  15   (available)
 16  G46 ├─ (available — verify boot) ────────┤ G48  16   (onboard NeoPixel)
 17  G9  ├─ I2C_SCL  ─────────────────────────┤ G47  17   (available)
 18  G10 ├─ (available) ──────────────────────┤ G21  18   (available — freed)
 19  G11 ├─ (available) ──────────────────────┤ G14  19   (available)
 20  G12 ├─ (available) ──────────────────────┤ G13  20   (available)
 21  3V3 ├────────────────────────────────────┤ 5V0  21
         └── USB-C In ───────USB-C Spare ─────┘
```

### Pin Zones Summary

| Zone | Pins | Header Side | Positions |
|---|---|---|---|
| **NeoPixel data** | GPIO4, GPIO5, GPIO6 | Left | 4, 5, 6 (consecutive) |
| **Audio UART** | GPIO17, GPIO18 | Left | 10, 11 (consecutive) |
| **I2C bus** | GPIO8, GPIO9 | Left | 12, 17 |
| **Relay control** | GPIO42, GPIO41, GPIO40, GPIO39 | Right | 6, 7, 8, 9 (consecutive) |

---

## Wire Color Convention

| Color | Purpose |
|---|---|
| **Red** | +5V power |
| **Black** | GND |
| **White** | NeoPixel data (or UART TX) |
| **Green** | UART RX |
| **Blue** | I2C SDA |
| **Yellow** | I2C SCL |
| **Orange** | Relay control signal |
| **Grey** | Audio signal ground |

---

## 1) Power Infrastructure

Wire this first. Everything else depends on clean power and ground.

### 1.1 Power Supply

**Component:** Mean Well LRS-100-5 (18A, 5V)

| From | To | Wire | Notes |
|---|---|---|---|
| LRS-100-5 V+ | 5V bus rail | Red (10 AWG) | Main power distribution |
| LRS-100-5 V− | GND bus rail | Black (10 AWG) | Main ground return |
| 5V bus | ESP32 5V0 pin (right-21) | Red | Board power (or use USB during dev) |
| GND bus | ESP32 GND (left-1 or right-1) | Black | Board ground |

### 1.2 Capacitors

| Capacitor | Location | Purpose |
|---|---|---|
| 100 µF 25V electrolytic | Across 5V/GND at ESP32 power input | Voltage sag dampening |
| 1000 µF 25V electrolytic | Across 5V/GND at each LED strip power input | Inrush current buffer |
| 10 µF 25V ceramic | Near PCA9685, near each amplifier | Local decoupling |

### 1.3 Ground Bus

**Critical:** All subsystem grounds MUST connect to the shared GND bus.

| Device | Ground Connection |
|---|---|
| ESP32-S3 | GND pin → GND bus |
| LRS-100-5 | V− → GND bus |
| All LED strips | GND wire → GND bus |
| PCA9685 | GND → GND bus |
| Tsunami WAV Trigger | GND → GND bus |
| GF1002 amplifier | GND → GND bus |
| LQ-AMP10W | GND → GND bus |
| All relay modules | GND → GND bus |

---

## 2) NeoPixel Lighting

All three data lines are now on consecutive left-side pins (positions 4–6). Use a **single SN74AHCT125N** (4-channel level shifter) for all three.

### 2.1 Level Shifter Wiring (SN74AHCT125N)

| SN74AHCT125N Pin | Connection | Notes |
|---|---|---|
| VCC | 5V bus | Powers the output side |
| GND | GND bus | Common ground |
| 1OE (pin 1) | GND bus | Enable channel 1 |
| 2OE (pin 4) | GND bus | Enable channel 2 |
| 3OE (pin 10) | GND bus | Enable channel 3 |
| 1A (pin 2) | ESP32 GPIO4 | Sky data input (3.3V) |
| 1Y (pin 3) | → 470Ω → Sky strip DIN | Sky data output (5V) |
| 2A (pin 5) | ESP32 GPIO5 | Stream data input (3.3V) |
| 2Y (pin 6) | → 470Ω → Stream strip DIN | Stream data output (5V) |
| 3A (pin 9) | ESP32 GPIO6 | Ground data input (3.3V) |
| 3Y (pin 8) | → 470Ω → Ground strip DIN | Ground data output (5V) |
| 4OE (pin 13) | 3V3 (tied high) | Channel 4 disabled (spare) |

### 2.2 Strip Connections

| config.py Constant | Pin | Strip | Pixels | Type |
|---|---|---|---|---|
| `NEOPIXEL_SKY_PIN` | GPIO4 (left-4) | Sky arc | 129 | WS2812B + SK6812 |
| `NEOPIXEL_STREAM_PIN` | GPIO5 (left-5) | Stream beads | 85 | addressable |
| `NEOPIXEL_GROUND_PIN` | GPIO6 (left-6) | Ground effects | 153 | WS2812B |

| From | To | Wire | Protection |
|---|---|---|---|
| 5V bus | Each strip 5V | Red | 1N4007 diode (optional reverse polarity) |
| GND bus | Each strip GND | Black | — |
| SN74AHCT125N 1Y | Sky strip DIN | White | 470Ω inline resistor |
| SN74AHCT125N 2Y | Stream strip DIN | White | 470Ω inline resistor |
| SN74AHCT125N 3Y | Ground strip DIN | White | 470Ω inline resistor |

> **Safety:** Place the level shifter physically close to the ESP32. Route data wires away from power and relay wiring.

---

## 3) Tsunami Audio (UART)

UART TX/RX are adjacent on the left header (positions 10–11).

### 3.1 UART Connections

| config.py Constant | Pin | Direction | Connects To |
|---|---|---|---|
| `AUDIO_UART_TX` | GPIO17 (left-10) | ESP32 → Tsunami | Tsunami **RXI** |
| `AUDIO_UART_RX` | GPIO18 (left-11) | Tsunami → ESP32 | Tsunami **TXO** |

| From | To | Wire | Notes |
|---|---|---|---|
| ESP32 GPIO17 | Tsunami RXI | White | TX crosses to RX |
| ESP32 GPIO18 | Tsunami TXO | Green | RX crosses to TX |
| ESP32 GND | Tsunami GND | Black | **Common ground required** |

**Settings:** `AUDIO_UART_BAUDRATE = 57600` in config.py. Tsunami SD card must have `tsunami.ini` with `BAUD=57600`, `MONO=1`, `SERIAL=1`.

### 3.2 Audio Output Path

```
Tsunami SD card (.wav, 44.1kHz mono)
   ├─ Audio Out L1, R1 → GF1002 amp → Spot speakers 1, 2
   ├─ Audio Out L2, R2 → GF1002 amp → Spot speakers 3, 4
   ├─ Audio Out L3, R3 → null [Spare]
   └─ Audio Out L4, R4 → LQ-AMP10W → Left + Right exciters
```

See [WIRING_AUDIO.md](WIRING_AUDIO.md) for detailed amp and speaker wiring.

---

## 4) I2C Bus (PCA9685 PWM Drivers)

| config.py Constant | Pin | Function |
|---|---|---|
| `I2C_SDA` | GPIO8 (left-12) | I2C data |
| `I2C_SCL` | GPIO9 (left-17) | I2C clock |

### 4.1 I2C Device Addresses

| Device | Address | Purpose |
|---|---|---|
| PCA9685 #1 | 0x40 | Servos (doors), Blowers, Mister |


### 4.2 Wiring

| From | To | Wire | Notes |
|---|---|---|---|
| ESP32 GPIO8 | PCA9685 #1 SDA | Blue | data |
| ESP32 GPIO9 | PCA9685 #1 SCL | Yellow | clock |
| PCA9685 VCC | 5V bus | Red | Board logic power |
| PCA9685 GND | GND bus | Black | Common ground |
| PCA9685 V+ | 5V bus (servo power) | Red | Separate from logic if possible |

> **Pull-ups:** Most PCA9685 breakout boards include 10kΩ pull-ups on SDA/SCL. If using bare chips, add 4.7kΩ pull-ups to 3.3V on both lines.

---

## 5) Chimney Relays

All three chimney relays are now on consecutive right-side pins (positions 6–8).

| config.py Constant | Pin | Smial | Physical Position |
|---|---|---|---|
| `CHIMNEY_RELAY_PIN1` | GPIO42 (right-6) | Smial 1 | Top of relay block |
| `CHIMNEY_RELAY_PIN2` | GPIO41 (right-7) | Smial 2 | Middle |
| `CHIMNEY_RELAY_PIN3` | GPIO40 (right-8) | Smial 3 | Bottom |

### 5.1 Wiring

| From | To | Wire | Notes |
|---|---|---|---|
| ESP32 GPIO42 | Relay module 1 IN | Orange | Smial 1 chimney |
| ESP32 GPIO41 | Relay module 2 IN | Orange | Smial 2 chimney |
| ESP32 GPIO40 | Relay module 3 IN | Orange | Smial 3 chimney |
| Relay module VCC | 5V bus | Red | Relay board power |
| Relay module GND | GND bus | Black | Common ground |

> **Safety:** Relay modules include flyback diodes and optoisolation. If using bare relays, add a 1N4007 flyback diode across the coil and drive via a transistor/MOSFET — never drive relay coils directly from GPIO.

> **Isolation:** Route relay wiring physically away from NeoPixel data lines and I2C/UART signals to reduce EMI.

---

## 6) Fogger Relay

The fogger relay is immediately below the chimney block (position 9).

| config.py Constant | Pin | Physical Position |
|---|---|---|
| `FOGGER_RELAY_PIN` | GPIO39 (right-9) | Below chimney block |

| From | To | Wire | Notes |
|---|---|---|---|
| ESP32 GPIO39 | Fogger relay module IN | Orange | Fog machine control |
| Relay module VCC | 5V bus | Red | Relay board power |
| Relay module GND | GND bus | Black | Common ground |

> **Backup:** If GPIO39 causes boot issues (due to SUBSPICSI alternate function), rewire to GPIO47 (right-17) and update `FOGGER_RELAY_PIN` in config.py.

> **Timing:** Fog cycles are controlled by `FOG_DURATION` (15s) and `FOG_INTERVAL` (300s) in config.py. Enable with `ENABLE_ATMOSPHERE = True` after wiring.

---

## 7) Future / Unassigned Pins

These pins are available for expansion. All have `digital_out` capability at minimum.

### Left Side (available)

| Pin | Position | Capabilities | Notes |
|---|---|---|---|
| GPIO7 | left-7 | analog, touch, digital | Low risk |
| GPIO15 | left-8 | analog, digital, UART RTS | Low risk |
| GPIO16 | left-9 | analog, digital, UART CTS | Low risk |
| GPIO3 | left-15 | analog, touch, digital | Low risk (JTAG alt) |
| GPIO46 | left-16 | digital only | Medium risk — verify boot |
| GPIO10 | left-18 | analog, touch, digital, SPI | Medium risk |
| GPIO11 | left-19 | analog, touch, digital, SPI | Medium risk |
| GPIO12 | left-20 | analog, touch, digital, SPI | Medium risk |

### Right Side (available)

| Pin | Position | Capabilities | Notes |
|---|---|---|---|
| GPIO1 | right-2 | analog, touch, digital | Low risk |
| GPIO2 | right-3 | analog, touch, digital | Low risk — freed from NeoPixel |
| GPIO38 | right-10 | digital, SPI | Medium risk |
| GPIO37 | right-11 | digital, SPI | Medium risk |
| GPIO36 | right-12 | digital, SPI | Medium risk |
| GPIO45 | right-15 | digital | Medium risk — verify boot |
| GPIO47 | right-17 | digital, SPI | Low risk — fogger backup |
| GPIO21 | right-18 | digital, RTC | Low risk — freed from chimney relay |
| GPIO14 | right-19 | analog, touch, digital, SPI | Medium risk |
| GPIO13 | right-20 | analog, touch, digital, SPI | Medium risk |

### Blocked Pins (do NOT use)

| Pin | Reason |
|---|---|
| GPIO0 | Boot mode strapping pin |
| GPIO19 | Previously failed — do not use until retested |
| GPIO20 | Native USB D+ |
| GPIO35 | Reserved |
| GPIO43 | USB serial TX (console) |
| GPIO44 | USB serial RX (console) |
| GPIO48 | Onboard NeoPixel LED |

---

## Breadboard Bench-Test Order

Wire and test each subsystem in this order. **Do not proceed** to the next step until the current one validates.

### Step 1: Board Power

1. Connect ESP32 via USB (or wire 5V bus → 5V0 pin + GND bus → GND pin).
2. Verify board boots with `import config` in the REPL — no exceptions.

### Step 2: NeoPixel Lighting

1. Wire the SN74AHCT125N level shifter (VCC, GND, OE pins tied low).
2. Connect GPIO4 → channel 1 input, channel 1 output → 470Ω → Sky strip DIN.
3. Power the Sky strip (5V + GND from bus, 1000µF cap).
4. Set `ENABLE_LIGHTING = True` in config.py.
5. Test:
   ```python
   from hardware import lighting_sky
   lighting_sky.setup_lighting_sky()
   lighting_sky.apply_lighting_preset_sky(2)  # White
   ```
6. Repeat for GPIO5 → Stream strip and GPIO6 → Ground strip.

### Step 3: Tsunami Audio

1. Wire GPIO17 → Tsunami RXI, GPIO18 → Tsunami TXO, GND → GND.
2. Ensure `tsunami.ini` is on the SD card with `BAUD=57600`, `MONO=1`, `SERIAL=1`.
3. Set `ENABLE_AUDIO = True` in config.py (already default).
4. Test:
   ```python
   from hardware import audio
   audio.setup_audio()
   audio.play_audio(1, 310)
   ```

### Step 4: I2C / PCA9685

1. Wire GPIO8 (SDA) and GPIO9 (SCL) to PCA9685 #1.
2. Power PCA9685 board (5V + GND from bus).
3. Set `ENABLE_MOTION = True` in config.py.
4. Test:
   ```python
   from hardware import motion
   motion.setup_hardware()
   motion.set_door(1, 90)  # Should move Smial 1 door servo
   ```

### Step 5: Chimney Relays

1. Wire GPIO42 → Relay 1 IN, GPIO41 → Relay 2 IN, GPIO40 → Relay 3 IN.
2. Power relay modules (5V + GND from bus).
3. Run `test_comprehensive_dry_run.py` — the sequence includes one chimney relay check per smial.

### Step 6: Fogger Relay

1. Wire GPIO39 → Fogger relay module IN.
2. Power relay module.
3. Set `ENABLE_ATMOSPHERE = True` in config.py.
4. Test:
   ```python
   from hardware import atmosphere
   atmosphere.setup_atmosphere()
   # Should print "Atmosphere: initialized"
   ```

### Step 7: Full System Test

1. Enable all modules in config.py.
2. Run `test_comprehensive_dry_run.py` — verifies each smial door, chimney relay, spot track, and smial light, then verifies fogger, exciters, stream, and sky.
3. After successful full-system test, update `board_profile_hybrid.json` to promote all `proposed` pins to `proven_full_system`.

---

## Migration Changelog

These pins changed from previous wiring guides:

| Change | Old Pin | New Pin | Reason |
|---|---|---|---|
| Ground NeoPixel | GPIO2 (right-3) | **GPIO6** (left-6) | Group all NeoPixel on left side, consecutive |
| Chimney Relay 1 | GPIO21 (right-18) | **GPIO42** (right-6) | Group all relays consecutively |
| Chimney Relay 2 | GPIO40 (right-8) | **GPIO41** (right-7) | Reorder for physical top-to-bottom = Smial 1→3 |
| Chimney Relay 3 | GPIO41 (right-7) | **GPIO40** (right-8) | Reorder for physical top-to-bottom = Smial 1→3 |
| Fogger Relay | None | **GPIO39** (right-9) | New assignment, extends relay block |

> **Important:** If you previously wired to the old pins, you must rewire to the new pins. The old pins (GPIO2, GPIO21) are now freed and available for future use.

---

## Safety Notes

- **3.3V logic:** All GPIO pins output 3.3V. Use the SN74AHCT125N level shifter for 5V NeoPixel data lines. Do not connect 5V signals directly to GPIO inputs.
- **Relay isolation:** Never drive relay coils directly from GPIO. Use relay modules with built-in drivers, or add a transistor + flyback diode.
- **Ground loops:** All devices must share a common ground bus. Floating grounds cause I2C errors and unreliable NeoPixel data.
- **GPIO19:** This pin previously failed testing. Do not use it for any assignment until it has been retested and cleared.
- **GPIO39 backup:** If GPIO39 causes boot issues, fall back to GPIO47 (right-17). Update `FOGGER_RELAY_PIN` in config.py and `board_profile_hybrid.json`.
- **Power budget:** The LRS-100-5 provides 18A at 5V. Monitor total draw if all LEDs are at full brightness simultaneously.
