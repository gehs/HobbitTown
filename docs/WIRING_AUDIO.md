# HobbitTown Audio Wiring Guide (PCA9685-Specific)

## Purpose

This guide explains the current audio-related wiring strategy used by the firmware, with a specific focus on PCA9685 channel usage.

This version is written for bench wiring by beginners.
If you are new: follow the steps in order, test after each step, and only add one wire at a time.

Current project state:
- Speaker control lines are implemented through PCA9685 channel outputs in `hardware/motion.py`.
- Actual audio playback in `hardware/audio.py` is currently a stub (no active DAC/decoder playback path yet).

### Stubbed -> Testable (What changed)

You can now test real hardware channel activity without full audio playback hardware.

`hardware/audio.py` now drives PCA9685 speaker-control channels in non-blocking test mode:
- Digital control channels: 8-11
- Level control channels: 12-13

This means audio commands now produce real output changes on PCA channels, which you can verify with LEDs on a driver board, a meter, or downstream amplifier control pins.

### Turn it on

1. In `config.py`, set:
```python
ENABLE_MOTION = True
```
2. Reboot board.
3. Confirm startup prints show motion ready and audio PCA test mode ready.
4. Run `/api/test/diagnostics` and confirm both 0x40 and 0x41 are present.
5. Run `/api/test/audio?player=1&track=1&loop=0`.
6. Confirm speaker-control channels toggle on PCA #1.

---

## Quick Start (Beginner Bench Plan)

### What you are building right now

- You are NOT wiring speaker power from PCA9685.
- You ARE wiring PCA9685 channels as control signals.
- Think of PCA channels as "switch commands" or "volume command signals," not as speaker power outputs.

### Wire color convention (recommended)

- Red: +5V
- Black: GND
- Blue: SDA
- Yellow: SCL
- White: PCA channel signal wires (CH8-CH13)

If you are also cutting LED strips in this build, follow addressable reconnect pathway rules in [LED_STRIP_CUTTING_PLAN.md](LED_STRIP_CUTTING_PLAN.md) (DOUT -> next DIN continuity is mandatory).

### Bench order (do this in sequence)

1. Build the 5V and GND rails.
2. Power both PCA boards (0x40 and 0x41).
3. Wire SDA/SCL from ESP32 to both PCA boards.
4. Confirm addresses with diagnostics.
5. Wire only CH8 through one driver stage.
6. Test CH8 on/off from API.
7. Repeat for CH9-CH13 one channel at a time.

---

## 1) Audio Control Architecture (Current Firmware)

### 1.1 What is controlled by PCA9685

PCA9685 #1 at address 0x40 is used for speaker control channels:
- Channels 8-11: digital-style control lines (on/off behavior)
- Channels 12-13: PWM level control lines

Reference behavior in firmware:
- `set_speaker(channel, value)` supports channels 8-13
- Channels 8-11 are forced to full-on or full-off
- Channels 12-13 map 0-255 to PWM duty

### 1.2 What is NOT controlled by PCA9685

- PCA9685 does not drive speaker coils directly.
- PCA9685 outputs must feed control inputs only (amp enable, mute, gain-control input, or transistor/MOSFET driver stage input).

Simple rule:
- PCA9685 pin -> control input
- Never PCA9685 pin -> speaker + or speaker -

---

## 2) Pin/Channel Allocation Table

| Device | I2C Address | Channel | Role |
|---|---|---:|---|
| PCA9685 #1 | 0x40 | 0-2 | Door servos |
| PCA9685 #1 | 0x40 | 3 | Spare servo/output |
| PCA9685 #1 | 0x40 | 8-11 | Speaker control (digital on/off lines) |
| PCA9685 #1 | 0x40 | 12-13 | Speaker control (PWM level lines) |
| PCA9685 #2 | 0x41 | 0 | Water mister #1 |
| PCA9685 #2 | 0x41 | 1-3 | Seuthe 117 chimney generators #1-#3 |
| PCA9685 #2 | 0x41 | 4-6 | Blowers |

Note:
- Older code paths still use the name `set_mister(id, value)` for channels 1-4.
- In your updated hardware this means: id 1 = water mister, id 2-4 = Seuthe chimney generators.

---

## 3) Current Loading and Power Rules

### 3.1 PCA9685 output limits

Treat PCA outputs as logic/control only.
- Do not connect speakers, motors, relays, or other power loads directly.
- Use a driver stage (transistor/MOSFET/opto/relay module input) between PCA output and any load.

If you are unsure whether a part is a "load" or a "control input":
- If it powers something mechanical or a speaker cone, it is a load. Do not connect directly.
- If it is labeled EN, IN, MUTE, GAIN, CTRL, or SIG, it is usually a control input.

### 3.2 Power distribution

For both PCA boards:
- VCC to 5V bus
- GND to common GND bus
- One 10uF capacitor across VCC/GND per board

For speaker amplifiers:
- Power amplifier modules from the main 5V bus (or their required supply rail)
- Share ground with ESP32 and PCA9685 boards

For Seuthe 117 chimney generators:
- Use an MT3608 boost converter stage (5V input -> Seuthe operating voltage output).
- Seuthe 117 packaging target: 16-18V operating range.
- Do not connect Seuthe heaters directly to the 5V rail if your target operating voltage is higher than 5V.
- Keep PCA9685 as control only; switch the boosted Seuthe supply through a driver stage.
- Beginner-safe recommendation: start at 16.0V, verify behavior/temperature, then increase only if needed.

Beginner-safe MT3608 setup order:
1. Disconnect Seuthe heater from MT3608 output.
2. Power MT3608 from 5V bus.
3. Measure MT3608 output with a multimeter.
4. Adjust trimmer to 16.0V first (Seuthe target range is 16-18V).
5. Power off.
6. Connect Seuthe heater through its driver path.
7. Power on and test briefly.

---

## 4) Recommended Protective Components

- I2C pull-ups: 4.7k ohm from SDA to 5V and SCL to 5V
- Decoupling: 10uF at each PCA board power input
- Driver-stage gate/base resistor: 1k to 4.7k (typical) between PCA output and transistor/MOSFET control pin
- Flyback diode: required only if you switch an inductive load (relay coil, motor), not for line-level amp control pins
- MT3608 boost module: required for each Seuthe channel that needs voltage above 5V

Why:
- Pull-ups keep I2C stable.
- Decoupling reduces brownout/noise.
- Gate/base resistors limit transient current.
- Flyback diodes absorb inductive kick.
- MT3608 provides correct heater voltage for Seuthe generators.

---

## 5) Step-by-Step Wiring (Speaker Control via PCA9685)

Example for one digital speaker control channel (ch8):
1. PCA9685 #1 CH8 signal pin -> 1k resistor -> transistor/MOSFET control input.
2. Driver output -> amplifier control pin (EN/MUTE/CTRL) or relay-module input.
3. Driver ground -> common GND bus.
4. Amplifier module power -> appropriate supply rail.
5. Amplifier module ground -> common GND bus.

Beginner checkpoint after step 5:
- No smell, no heat, no reset loops.
- ESP32 still responds to web UI.
- PCA diagnostics still show both addresses.

Repeat similarly for:
- CH9-CH11 for additional digital speaker control lines
- CH12-CH13 for PWM level control lines

For PWM level lines (CH12/CH13):
- If your amplifier expects analog control voltage, add a low-pass RC stage after the PCA output (for example, resistor + capacitor) before the amplifier control input.
- If your amplifier expects digital/PWM-compatible control, connect through a driver stage as above.

If you do not know what your amplifier expects:
- Start with CH8-CH11 only (on/off style).
- Leave CH12-CH13 disconnected until you confirm PWM/analog requirements from the amplifier datasheet.

---

## 6) Firmware-Accurate Test Procedure

1. Enable motion in config:
```python
ENABLE_MOTION = True
```

2. Verify both PCA9685 addresses are present:
- Open: `/api/test/diagnostics`
- Confirm 0x40 and 0x41 appear in scan results.

3. Test speaker channels from browser or API:
- Digital line on: `/api/test/speaker?channel=8&value=255`
- Digital line off: `/api/test/speaker?channel=8&value=0`
- PWM line mid-level: `/api/test/speaker?channel=12&value=128`
- PWM line max: `/api/test/speaker?channel=13&value=255`

4. Observe hardware behavior:
- Driver stage toggles cleanly
- Amplifier control pin responds
- No resets/brownouts on ESP32 or PCA boards

Beginner pass/fail rule:
- Pass: web command changes behavior and board stays stable.
- Fail: reboot, bus errors, or hot components. Stop and re-check wiring before continuing.

---

## 7) Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| Speaker control API responds but no hardware reaction | Channel wired to wrong PCA board/channel | Re-check channel map and wiring labels |
| I2C diagnostics missing 0x40 or 0x41 | Address jumper or power wiring issue | Verify A0-A3 jumpers and board VCC/GND |
| Audible noise when using PWM level lines | PWM fed directly into analog control input | Add RC low-pass stage and verify grounding |
| ESP32 resets when speaker path toggles | Shared supply sag or poor ground return | Improve power distribution and add local decoupling |

---

## 8) Bench Safety Rules (Read Before Power-On)

1. Power off before moving wires.
2. Keep one hand on the wire, one eye on labels. Do not move multiple wires at once.
3. Label each signal wire: CH8, CH9, CH10, CH11, CH12, CH13.
4. Test one channel at a time.
5. If anything gets warm unexpectedly, power off immediately.

---

## 9) First Power-On Solder QA (Pass/Fail)

Use this table before and during first power-on. If any line fails, stop and fix before continuing.

| Checkpoint | PASS if... | FAIL if... | Immediate action |
|---|---|---|---|
| Visual solder joints | Joints are shiny/cone-shaped, no bridges | Dull blobs, cracked joints, bridged pins | Power off, reflow with flux, inspect again |
| Continuity between adjacent pins | No short beep between neighboring pins (except intended nets) | Meter beeps where it should not | Remove excess solder, re-test continuity |
| Ground continuity | All modules share common GND | Floating/isolated grounds | Rewire GND bus before power-on |
| PCA9685 addresses | `/api/test/diagnostics` shows 0x40 and 0x41 | Missing one or both addresses | Check VCC/GND/SDA/SCL and address jumpers |
| MT3608 setpoint for Seuthe | Output reads 16.0V before connecting heater | Output is unknown or >18V | Disconnect heater, adjust and re-measure |
| First channel test | One channel toggles as expected and board remains stable | Resets, hot parts, or no response | Power off, inspect channel wiring + driver stage |
| FeatherWing pinless solder (if used) | Board is flat, headers solid, no loose pins | Wobble, intermittent contact | Re-solder headers/wires and continuity check |
| LED reconnect direction (if cutting LEDs) | Data path is DOUT -> next DIN | DIN->DIN or DOUT->DOUT mistake | Rework wiring before further tests |

Go/No-Go rule:
- Continue only when all checkpoints pass.
- If two failures repeat on the same checkpoint, stop and troubleshoot that section in isolation.

---

## 10) Optional Future Path: Music Maker FeatherWing

The Phase 1 guide mentions the Adafruit Music Maker FeatherWing as an optional advanced audio path.
- That path is SPI-based and separate from PCA speaker-control lines.
- If/when enabled, keep this PCA guide for control-line wiring and add a dedicated playback wiring section for FeatherWing SPI signals and audio routing.

### 10.1 Pinless Music Maker FeatherWing (Solder-First Workflow)

If your Music Maker FeatherWing is pinless (header holes only), do this before wiring tests:

1. Dry-fit the FeatherWing on the host board without solder to confirm orientation.
2. Insert headers or wires through the FeatherWing holes and make sure the board sits flat.
3. Tack-solder one corner pin only.
4. Re-check alignment (flat board, straight headers).
5. Solder the opposite corner pin.
6. Solder the remaining pins.
7. Inspect every joint for a clean cone shape and no solder bridges.
8. Run continuity checks between neighboring pins to confirm no short.

Beginner solder checklist:
- Use flux and a clean tip.
- Heat pad and pin together, then feed solder.
- If a joint looks dull/cracked, reflow it.

Important:
- Do not rely on friction fit for bench tests.
- Fully soldered pins are required for stable SPI/audio connections.
