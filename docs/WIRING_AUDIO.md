# HobbitTown Audio Wiring Guide

## Purpose

This guide documents the confirmed audio hardware architecture for the HobbitTown diorama, including signal paths, amp roles, zone control, and wiring steps.

This version is written for bench wiring by beginners.
If you are new: follow the steps in order, test after each step, and only add one wire at a time.

## Confirmed Hardware Inventory

| Component | Qty | Role |
|---|---|---|
| Adafruit Music Maker FeatherWing (VS1053b) | 1 | Ambient audio source — SPI, analog stereo line-out, SD card playback |
| GF1002 (PAM8403) 2-channel amp board | 4 | Ambient speaker zones — analog L/R input from FeatherWing |
| MAX98357 I2S amp board | 4 | Event sounds — 4 spot speakers (one per smial + one extra), I2S from ESP32-S3 |
| LQ-AMP10W | 1 | Exciter amplifier — stereo, driven directly from FeatherWing L/R line-out |
| Audio Exciters | 2 (L + R) | Atmospheric vibration resonators — stereo pair driven by LQ-AMP10W |
| 1" spot speakers | 4 | Point-source event sounds — driven by MAX98357 #1-4 |
| PCA9685 #1 (0x40) | 1 | Zone mute control (CH8-11) via GF1002 SHDN pins |

## Confirmed Signal Path Overview

```
SD card → Music Maker FeatherWing (VS1053b, SPI)
               │
       Stereo analog line-out (L, GND, R)
       │                                    │
  L out (100Ω series)                  R out (100Ω series)
  ├── GF1002 #1 → Zone 1 speakers      ├── GF1002 #3 → Zone 3 speakers
  ├── GF1002 #2 → Zone 2 speakers      ├── GF1002 #4 → Zone 4 speakers
  └── LQ-AMP10W L input                └── LQ-AMP10W R input
                    │                              │
            Left Exciter                   Right Exciter
         (left 4' panel)                 (right 4' panel)

ESP32-S3 I2S (audiobusio.I2SOut) — shared BCLK / LRCLK / DIN bus
  MAX98357 #1 → 1" spot speaker (Smial 1 / Bag End)
  MAX98357 #2 → 1" spot speaker (Smial 2 / Great Smial)
  MAX98357 #3 → 1" spot speaker (Smial 3)
  MAX98357 #4 → 1" spot speaker (extra / Party Tree)

PCA9685 #1 (0x40) — zone enable / mute control only
  CH8  → GF1002 #1 SHDN
  CH9  → GF1002 #2 SHDN
  CH10 → GF1002 #3 SHDN
  CH11 → GF1002 #4 SHDN
  CH12 → spare
  CH13 → spare
```

### Why two separate signal paths?

- **FeatherWing → GF1002 (ambient):** The VS1053b chip handles seamless looping and crossfading entirely on-chip with no ESP32 CPU load. GF1002/PAM8403 accepts the analog line-level output directly — no conversion needed.
- **FeatherWing → LQ-AMP10W → Exciters (stereo surface):** The same L/R line-out that feeds the GF1002 ambient zones is also split (via a second 100Ω branch per channel) directly into the LQ-AMP10W stereo input. The exciters carry the ambient mix and make the physical box panels resonate in stereo — left exciter on the left 4' panel, right on the right. Rain sweeps left-to-right if panned that way in the ambient track. No separate content is needed; the ambient soundscape IS the exciter content.
- **ESP32-S3 I2S → MAX98357 (events):** `audiobusio.I2SOut` in CircuitPython plays WAV files from flash storage onto the I2S bus independently of the FeatherWing. Events (thunder crack, rooster, bell, dragon) fire on specific spot speakers while ambient loops and exciter vibration continue uninterrupted.

### Note on FeatherWing mono out

The VS1053b mono output pin is always a hardware sum of whatever is on the stereo outputs. There is no way to route content exclusively to mono. Do not use the FeatherWing mono pin — use the L and R line-out pads for the split to both GF1002 zones and LQ-AMP10W.

### Turn on PCA zone control (current firmware)

1. In `config.py`, set:
```python
ENABLE_MOTION = True
```
2. Reboot board.
3. Run `/api/test/diagnostics` and confirm both 0x40 and 0x41 are present.
4. Test zone mute: `/api/test/speaker?channel=8&value=255` (GF1002 #1 on) / `value=0` (muted).
5. Repeat for CH9 (zone 2), CH10 (zone 3), CH11 (zone 4).
6. Exciter has no firmware enable pin — it is always on with the FeatherWing ambient output.

---

## Quick Start (Beginner Bench Plan)

### What you are building

- **Ambient path:** FeatherWing SPI wired to ESP32 → FeatherWing L/R line-out → 4× GF1002 amp boards → ambient speakers (4 zones).
- **Exciter path:** Same FeatherWing L/R line-out (second split branch) → LQ-AMP10W L+R inputs → Left + Right exciter panels. Always on with the ambient mix.
- **Event path:** ESP32-S3 I2S GPIO → 4× MAX98357 amp boards → 4 spot speakers. Each board selectively enabled via SD_MODE.
- **Zone control:** PCA9685 CH8-11 → GF1002 SHDN pins (direct wire, no driver stage, no MOSFET). CH12-13 spare.

### Wire color convention (recommended)

- Red: +5V
- Black: GND
- Blue: SDA (I2C)
- Yellow: SCL (I2C)
- Orange: I2S BCLK
- Purple: I2S LRCLK
- Green: I2S DIN
- White: PCA channel control wires (CH8-CH13)
- Grey: Audio signal wires (FeatherWing L/R out)

If you are also cutting LED strips in this build, follow addressable reconnect pathway rules in [LED_STRIP_CUTTING_PLAN.md](LED_STRIP_CUTTING_PLAN.md) (DOUT -> next DIN continuity is mandatory).

### Bench order (do this in sequence)

1. Build the 5V and GND rails.
2. Power both PCA boards (0x40 and 0x41).
3. Wire SDA/SCL from ESP32 to both PCA boards.
4. Confirm I2C addresses with `/api/test/diagnostics`.
5. Solder and power the FeatherWing. Confirm SD card mounts.
6. Wire FeatherWing L/R line-out → one GF1002 board. Play a test file. Confirm audio.
7. Wire remaining GF1002 boards one at a time.
8. Wire FeatherWing L/R line-out second split branch → LQ-AMP10W L+R inputs. Confirm exciters vibrate with ambient audio.
9. Wire ESP32 I2S pins → one MAX98357. Play a WAV. Confirm audio at spot speaker.
10. Wire remaining 3 MAX98357 boards onto the shared I2S bus.
11. Wire PCA CH8 → GF1002 #1 SHDN. Test mute/unmute via API. Repeat for CH9-CH11.

---

## 1) Audio Control Architecture

### 1.1 Ambient path — Music Maker FeatherWing → GF1002 boards

The FeatherWing (VS1053b) plays looping MP3/WAV files from SD card over SPI. Its stereo analog line-out feeds all four GF1002/PAM8403 amp boards.

- FeatherWing L out → 100Ω resistor → two parallel branches → GF1002 #1 L input, GF1002 #2 L input
- FeatherWing R out → 100Ω resistor → two parallel branches → GF1002 #3 L input, GF1002 #4 L input
- GF1002 B (right input) wired to same signal as L for mono (or to matching R output for true stereo per board)
- GF1002 G → common GND bus
- All four GF1002 boards share the FeatherWing line-out simultaneously

GF1002/PAM8403 inputs **L, G, B** are analog, not digital. Do not wire ESP32 GPIO directly to GF1002 inputs.

### 1.2 Exciter path — FeatherWing L/R line-out → LQ-AMP10W → Stereo Exciters

The same FeatherWing L and R line-out pads that feed the GF1002 ambient zones are also split into the LQ-AMP10W stereo amp input. Each output requires a second 100Ω series resistor on its split branch before reaching the LQ-AMP10W.

- FeatherWing L out → 100Ω → junction: GF1002 #1/#2 L inputs + LQ-AMP10W L input
- FeatherWing R out → 100Ω → junction: GF1002 #3/#4 L inputs + LQ-AMP10W R input
- LQ-AMP10W L output → Left exciter (mounted on left panel of 2'×4' box)
- LQ-AMP10W R output → Right exciter (mounted on right panel of 2'×4' box)

The exciters always carry the ambient stereo mix. They do not have a separate enable pin — they are on whenever the FeatherWing is playing. This is by design: in a 2'×4'×16" enclosure, making the box itself resonate in stereo with the ambient soundscape is the best use of exciter transducers.

### 1.3 Event path — ESP32-S3 I2S → MAX98357 boards

The ESP32-S3 drives a shared I2S bus using `audiobusio.I2SOut`. All four MAX98357 boards share the same three wires:
- BCLK (bit clock)
- LRCLK (left/right clock)
- DIN (data in)

All four MAX98357 boards hear the same I2S stream simultaneously. Scene logic enables only the target board(s) via SD_MODE. The remaining boards are held in shutdown.

Event WAV files are stored on the ESP32-S3 CIRCUITPY flash (12-13MB free on the N16R8 board). A 3-second mono WAV at 16-bit 44.1kHz is ~265KB. The flash has capacity for 40+ event sounds with no additional storage hardware needed.

### 1.4 What PCA9685 controls in this architecture

- PCA9685 CH8-11 go directly to GF1002 SHDN logic-level inputs (ambient zone mute).
- MAX98357 SD_MODE pins (#1-4) are controlled by spare ESP32-S3 GPIO pins or spare PCA channels.
- No MOSFET, no transistor, no driver stage required anywhere in the audio path.
- SHDN (GF1002/PAM8403): High = amp on, Low = amp muted.
- SD_MODE (MAX98357): High = amp on playing left channel, Low = shutdown.
- Both are logic-level inputs drawing less than 1mA. PCA9685 or GPIO drives them directly.
- Add a 10kΩ pull-up resistor from each SHDN/SD_MODE pin to 5V so amps default to ON at startup before firmware initializes.
- The LQ-AMP10W exciter path has no firmware enable — it follows the FeatherWing line-out passively.

Simple rule:
- PCA9685 or GPIO pin → amp SHDN or SD_MODE pin
- Never PCA9685 or GPIO pin → speaker + or speaker -

---

## 2) Pin/Channel Allocation Table

### PCA9685 #1 (0x40)

| Channel | Role | Target pin | Wire |
|---|---|---|---|
| 0 | Door servo 1 | PCA9685 PWM out | Signal wire |
| 1 | Door servo 2 | PCA9685 PWM out | Signal wire |
| 2 | Door servo 3 | PCA9685 PWM out | Signal wire |
| 3 | Spare servo / output | — | — |
| 8 | GF1002 #1 mute | PAM8403 SHDN pin | White, + 10kΩ pull-up to 5V |
| 9 | GF1002 #2 mute | PAM8403 SHDN pin | White, + 10kΩ pull-up to 5V |
| 10 | GF1002 #3 mute | PAM8403 SHDN pin | White, + 10kΩ pull-up to 5V |
| 11 | GF1002 #4 mute | PAM8403 SHDN pin | White, + 10kΩ pull-up to 5V |
| 12 | Spare | — | — |
| 13 | Spare | — | — |

### PCA9685 #2 (0x41)

| Channel | Role |
|---|---|
| 0 | Water mister #1 |
| 1-3 | Seuthe 117 chimney generators #1-#3 |
| 4-6 | Blowers |

Note: Firmware `set_mister(id, value)` maps id 1 = water mister, id 2-4 = Seuthe chimney generators.

### ESP32-S3 I2S Pin Assignments (shared bus)

| Signal | ESP32-S3 GPIO | All MAX98357 boards |
|---|---|---|
| BCLK | TBD (assign in firmware) | All 4 boards wired in parallel |
| LRCLK | TBD | All 4 boards wired in parallel |
| DIN | TBD | All 4 boards wired in parallel |
| SD_MODE #1 | GPIO or PCA spare | MAX98357 #1 SD_MODE (Smial 1 / Bag End) |
| SD_MODE #2 | GPIO or PCA spare | MAX98357 #2 SD_MODE (Smial 2 / Great Smial) |
| SD_MODE #3 | GPIO or PCA spare | MAX98357 #3 SD_MODE (Smial 3) |
| SD_MODE #4 | GPIO or PCA spare | MAX98357 #4 SD_MODE (Party Tree / extra) |

Note: SD_MODE pins are best driven from spare ESP32-S3 GPIO for fastest scene response. PCA9685 CH12-13 are spare and can be used if GPIO count is exhausted.

### Music Maker FeatherWing SPI Pins (from Adafruit documentation)

| Signal | ESP32-S3 pin |
|---|---|
| SCK | SPI clock |
| MISO | SPI MISO |
| MOSI | SPI MOSI |
| CS | FeatherWing CS |
| DREQ | Data request (interrupt) |
| RESET | VS1053b reset |

---

## 3) Power Distribution

### 3.1 Amplifier power requirements

| Amp | Supply | Max draw | Notes |
|---|---|---|---|
| GF1002 #1-4 (PAM8403) | 5V bus | ~1A per board at full volume | Power from 5V bus directly |
| MAX98357 #1-4 | 5V bus | ~1.5A per board at peak | Power from 5V bus directly |
| LQ-AMP10W | Check LQ-AMP10W rating | Up to 10W output | Confirm supply voltage from datasheet; fed from FeatherWing line-out, not ESP32-S3 |
| Music Maker FeatherWing | 5V USB or bus | ~20mA logic, ~85mA with headphones | Power from 5V bus |

### 3.2 Common ground — mandatory

All modules must share a common GND:
- ESP32-S3 GND
- PCA9685 #1 and #2 GND
- All GF1002 boards GND
- All MAX98357 boards GND
- LQ-AMP10W GND
- FeatherWing GND
- LRS-100-5 power supply GND

Floating or disconnected grounds cause hum, noise, and unreliable I2C/SPI.

### 3.3 Decoupling capacitors

- 10uF across VCC/GND at each PCA9685 board input
- 100uF across 5V/GND at each GF1002 board power input (PAM8403 can draw surge current)
- 10uF across 5V/GND at each MAX98357 board power input

### 3.4 Seuthe 117 chimney generators (non-audio, on PCA #2)

- Use an MT3608 boost converter stage (5V in → 16-18V out) per Seuthe channel.
- PCA9685 #2 channels control the driver stage only; never connect Seuthe heater directly to PCA output.
- MT3608 setup: adjust to 16.0V before connecting heater; verify with multimeter first.

Beginner-safe MT3608 setup order:
1. Disconnect Seuthe heater from MT3608 output.
2. Power MT3608 from 5V bus.
3. Measure MT3608 output with a multimeter.
4. Adjust trimmer to 16.0V.
5. Power off.
6. Connect Seuthe heater through driver path.
7. Power on and test briefly.

---

## 4) Recommended Protective Components

| Component | Where | Why |
|---|---|---|
| 4.7kΩ pull-up × 2 | SDA and SCL to 5V | I2C requires open-drain; pull-ups hold lines high when idle |
| 10kΩ pull-up per amp | Each SHDN / SD_MODE pin to 5V | Ensures amps default to ON at startup before firmware runs |
| 100Ω series resistor × 2 | FeatherWing L out and R out, before Y-split | Isolates FeatherWing output when driving multiple GF1002 inputs in parallel |
| 100uF electrolytic per GF1002 | Across 5V/GND at each GF1002 power input | Absorbs PAM8403 inrush current on loud transients |
| 10uF ceramic per MAX98357 | Across 5V/GND at each MAX98357 power input | Decouples I2S amp from supply noise |
| 10uF ceramic per PCA9685 | Across VCC/GND at each PCA board | Reduces I2C brownout events |
| Flyback diode (1N4007) | Relay coil only (fogger relay) | Not needed for amp control pins — only for inductive loads |
| MT3608 boost module | Per Seuthe channel requiring >5V | Provides correct heater voltage for Seuthe 117 generators |

No MOSFETs or transistor driver stages are required in the audio path. SHDN and SD_MODE are direct logic-level inputs on all amps in this build.

---

## 5) Step-by-Step Wiring

### 5.1 FeatherWing → GF1002 ambient zones + LQ-AMP10W exciter

Both the GF1002 ambient zones and the LQ-AMP10W exciter share the FeatherWing L/R line-out. Wire the split as follows:

1. Solder and seat the Music Maker FeatherWing on the ESP32 host board (or wire individually — see Section 10.1).
2. Insert a formatted microSD card with test audio files.
3. Wire FeatherWing L out pad → 100Ω resistor → junction node A.
   - Node A → GF1002 #1 L input
   - Node A → GF1002 #2 L input
   - Node A → LQ-AMP10W L input
4. Wire FeatherWing R out pad → 100Ω resistor → junction node B.
   - Node B → GF1002 #3 L input
   - Node B → GF1002 #4 L input
   - Node B → LQ-AMP10W R input
5. Wire FeatherWing GND → common GND bus.
6. Wire each GF1002 G (ground input) → common GND bus.
7. Wire each GF1002 B input to the same signal as its L input (mono per board) OR to the opposite channel output for true stereo per board. Mono is simpler and works well for ambient zone speakers.
8. Wire each GF1002 R+/-, L+/- outputs → speaker terminals.
9. Power each GF1002 from 5V bus; add 100uF capacitor at each board's power input.
10. Wire LQ-AMP10W L output → Left exciter transducer terminals.
11. Wire LQ-AMP10W R output → Right exciter transducer terminals.
12. Power LQ-AMP10W from appropriate supply (verify voltage from datasheet before connecting exciters).
13. Wire LQ-AMP10W GND → common GND bus.

Beginner checkpoint:
- Power on. Play a test file from FeatherWing.
- Confirm sound from all four GF1002 zones.
- Confirm both exciter panels vibrate with the audio.
- No heat, no hum, no distortion.

### 5.2 GF1002 SHDN zone mute via PCA9685 CH8-11

1. Wire a 10kΩ resistor from each GF1002 SHDN pin to 5V (pull-up).
2. Wire PCA9685 #1 CH8 signal pin → GF1002 #1 SHDN.
3. Wire PCA9685 #1 CH9 signal pin → GF1002 #2 SHDN.
4. Wire PCA9685 #1 CH10 signal pin → GF1002 #3 SHDN.
5. Wire PCA9685 #1 CH11 signal pin → GF1002 #4 SHDN.
6. Test: `/api/test/speaker?channel=8&value=0` should mute GF1002 #1. `value=255` unmutes it.

### 5.3 ESP32-S3 I2S → MAX98357 event spots (#1-4)

1. Choose three ESP32-S3 GPIO pins for BCLK, LRCLK, DIN. Add to `config.py`.
2. Wire BCLK → all four MAX98357 BCLK pins (daisy-chain).
3. Wire LRCLK → all four MAX98357 LRCLK pins.
4. Wire DIN → all four MAX98357 DIN pins.
5. Wire each MAX98357 Vdd → 5V bus. GND → GND bus. Add 10uF at each.
6. Wire MAX98357 #1 speaker output → spot speaker at Smial 1 / Bag End.
7. Wire MAX98357 #2 speaker output → spot speaker at Smial 2 / Great Smial.
8. Wire MAX98357 #3 speaker output → spot speaker at Smial 3.
9. Wire MAX98357 #4 speaker output → spot speaker at Party Tree / extra location.
10. Wire each MAX98357 SD_MODE → dedicated GPIO pin + 10kΩ pull-up to 5V.

Beginner checkpoint:
- Copy a short WAV file to CIRCUITPY flash (e.g., `/audio/events/test_click.wav`).
- Play it from CircuitPython REPL using `audiobusio.I2SOut`.
- Enable one MAX98357 at a time via its SD_MODE GPIO. Confirm sound only from that spot speaker.

---

## 6) Firmware Test Procedure

1. Enable motion in `config.py`:
```python
ENABLE_MOTION = True
```

2. Verify PCA9685 addresses:
- Open `/api/test/diagnostics`
- Confirm 0x40 and 0x41 appear.

3. Test GF1002 zone muting:
- Mute zone 1: `/api/test/speaker?channel=8&value=0`
- Unmute zone 1: `/api/test/speaker?channel=8&value=255`
- Repeat for CH9 (zone 2), CH10 (zone 3), CH11 (zone 4).
- Confirm ambient audio drops and returns for each zone.
- Confirm exciter vibration follows the ambient output (no separate enable needed).

4. Exciter path has no firmware control pin — it is always active while FeatherWing is playing.

5. I2S event audio test (CircuitPython REPL):
```python
import audiobusio, audiocore, board
audio = audiobusio.I2SOut(board.GPIOXX, board.GPIOXX, board.GPIOXX)  # BCLK, LRCLK, DIN
wav = audiocore.WaveFile(open('/audio/test.wav', 'rb'))
audio.play(wav)
```
- Enable one MAX98357 SD_MODE at a time.
- Confirm sound only from that spot speaker.

Beginner pass/fail rule:
- Pass: web command changes behavior, board stays stable, no hot components.
- Fail: reboot, bus errors, or unexpected heat. Stop and re-check wiring.

---

## 7) Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| GF1002 zone mute API has no effect | SHDN pin not wired, or pull-up missing | Check CH8-11 wiring and 10kΩ pull-up to 5V on each SHDN |
| All GF1002 zones silent | FeatherWing not playing, SD card missing, or L/R wiring open | Confirm SD card, test FeatherWing independently, check 100Ω series resistors |
| Exciters not vibrating | LQ-AMP10W not powered, GND floating, or L/R split wiring open | Check LQ-AMP10W supply, GND, and both 100Ω branch connections |
| Exciters vibrate but no zone speaker sound | GF1002 branch of split open or SHDN held low | Check junction node wiring; verify SHDN pull-up is present |
| Hum or buzz from GF1002 or exciters | Ground loop — one module GND floating | Verify common GND bus across all modules including LQ-AMP10W |
| No sound from spot speakers | MAX98357 SD_MODE held low (shutdown) | Check SD_MODE GPIO pull-up; verify GPIO drives it high |
| All MAX98357 play at once when only one expected | SD_MODE control not wired per board | Wire individual SD_MODE pin per MAX98357 |
| I2C diagnostics missing 0x40 or 0x41 | Address jumper or power wiring issue | Verify A0-A3 jumpers and board VCC/GND |
| FeatherWing not found on SPI bus | CS or RESET pin not connected, or SPI conflict | Check all five FeatherWing SPI pins; verify no shared CS conflict |
| ESP32 resets during audio playback | Shared supply sag | Add 100uF decoupling at GF1002 boards; verify 5V bus under load |

---

## 8) Bench Safety Rules (Read Before Power-On)

1. Power off before moving wires.
2. Keep one hand on the wire, one eye on labels. Do not move multiple wires at once.
3. Label all signal wires: CH8-CH11 (PCA zone mute), BCLK/LRCLK/DIN (I2S), L/R (FeatherWing), SD_MODE #1-4 (GPIO).
4. Test one amp board at a time — do not wire all simultaneously before confirming each one works.
5. Confirm LQ-AMP10W supply voltage before connecting exciter. An over-voltage supply will damage the exciter.
6. If anything gets warm unexpectedly, power off immediately.

---

## 9) First Power-On Solder QA (Pass/Fail)

Use this table before and during first power-on. If any line fails, stop and fix before continuing.

| Checkpoint | PASS if... | FAIL if... | Immediate action |
|---|---|---|---|
| Visual solder joints | Joints are shiny/cone-shaped, no bridges | Dull blobs, cracked joints, bridged pins | Power off, reflow with flux, inspect again |
| Continuity between adjacent pins | No short beep between neighboring pins (except intended nets) | Meter beeps where it should not | Remove excess solder, re-test continuity |
| Ground continuity | All modules share common GND | Floating/isolated grounds | Rewire GND bus before power-on |
| PCA9685 addresses | `/api/test/diagnostics` shows 0x40 and 0x41 | Missing one or both addresses | Check VCC/GND/SDA/SCL and address jumpers |
| FeatherWing SPI | FeatherWing appears on SPI bus; SD card mounts | No response or SD mount fail | Check CS, RESET, MOSI, MISO, SCK wiring |
| FeatherWing audio | Test MP3 plays through at least one GF1002 zone | Silence or distortion | Check L/R out wiring, 100Ω series resistors, GF1002 power |
| GF1002 zone mute | CH8 value=0 silences zone 1; value=255 restores it | No change | Check SHDN wiring and 10kΩ pull-up |
| MAX98357 spot speaker | One spot speaker plays WAV when SD_MODE GPIO high | Silence or all boards play | Check SD_MODE wiring per board; verify I2S bus |
| Exciter vibration | Both exciter panels vibrate when FeatherWing plays audio | No vibration or only one side | Check LQ-AMP10W L/R input wiring and supply voltage |
| LQ-AMP10W supply voltage | Supply voltage matches datasheet rating | Unknown or incorrect voltage | Measure with multimeter before connecting exciters |
| MT3608 setpoint for Seuthe | Output reads 16.0V before connecting heater | Output unknown or >18V | Disconnect heater, adjust and re-measure |
| LED reconnect direction (if cutting LEDs) | Data path is DOUT -> next DIN | DIN->DIN or DOUT->DOUT mistake | Rework wiring before further tests |

Go/No-Go rule:
- Continue only when all checkpoints pass.
- If two failures repeat on the same checkpoint, stop and troubleshoot that section in isolation.

---

## 10) Music Maker FeatherWing — Confirmed Audio Source

The Adafruit Music Maker FeatherWing (VS1053b) is the confirmed ambient audio source for this project. It is SPI-based, plays MP3/WAV/OGG/MIDI from microSD card, and provides a stereo analog line-level output that feeds the four GF1002 ambient amp zones.

- SPI interface: connects to ESP32-S3 SPI bus (MOSI, MISO, SCK, CS, DREQ, RESET)
- Analog line-level output: 3.5mm headphone jack or breakout pads (L, GND, R)
- Built-in 3W stereo amp (not used in this project — use the line-out pads to feed external GF1002 amps)
- MicroSD card slot: stores all ambient audio files
- On-chip VS1053b handles seamless looping and decoding with no ESP32 CPU overhead

### 10.1 Pinless Music Maker FeatherWing (Solder-First Workflow)

If your Music Maker FeatherWing is pinless (header holes only), complete all soldering before any wiring tests:

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

### 10.2 MicroSD card file organization

Organize audio files by soundscape folder:
```
/audio/
  /shire_spring_dawn/
    birds_chorus_spring.mp3
    stream_flowing_gentle.wav
    wind_foliage_rustle.wav
    rooster_distant_single.wav
    shire_bell_toll_single.wav
  /shire_spring_evening/
    birds_chorus_evening_spring.mp3
    crickets_frogs_chorus_spring.mp3
  /shire_summer_thunderstorm/
    thunderstorm_base_18m.mp3
    thunder_crack_1.wav
    thunder_crack_2.wav
    heavy_rain_3s.wav
  /events/
    dragon_roar.wav
    party_music_loop.mp3
    deep_rumble_exciter.wav
```

Format: FAT32. Long looping ambient tracks as MP3 (128 kbps). Short event WAVs at 16-bit 44.1kHz.
