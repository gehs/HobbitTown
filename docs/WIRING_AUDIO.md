# HobbitTown Audio Wiring Guide

## Purpose

This guide documents the confirmed audio hardware architecture for the HobbitTown diorama, including signal paths, amp roles, zone control, and wiring steps.

This version is written for bench wiring by beginners.
If you are new: follow the steps in order, test after each step, and only add one wire at a time.

## Confirmed Hardware Inventory

| Component | Qty | Role |
|---|---|---|
| Tsunami Super WAV Trigger | 1 | Primary audio controller — UART serial command, 44.1kHz mono WAV playback |
| GF1002 (PAM8403) 2-channel amp board | 1 | Speaker amplifier — analog line-level input from Tsunami Audio Out 1L |
| LQ-AMP10W | 1 | Exciter amplifier — stereo, driven via 3.5mm jack from Tsunami auxiliary output (or mono out) |
| Audio Exciters | 2 (L + R) | Atmospheric vibration resonators — stereo pair driven by LQ-AMP10W |
| 1" spot speakers | 4-8 | Point-source sounds — driven by GF1002 or wired in parallel groups |

## Confirmed Signal Path Overview

```
Tsunami SD card (.wav files, 44.1kHz mono)
    │
    ├─ Audio Out 1L → GF1002 amplifier → Spot speaker(s)
    │
    └─ Auxiliary output (3.5mm jack) → LQ-AMP10W → Left + Right Exciters

ESP32-S3 UART (GPIO17/18)
    │
    └─ TX/RX to Tsunami Super WAV Trigger (57600 baud)
```

**Key differences from prior architecture:**
- Single unified audio source: Tsunami plays all WAV files from SD card
- No FeatherWing, no VS1053b, no SPI
- No MAX98357 I2S boards; single GF1002 handles all speaker output
- No PCA9685 zone mute control (all speakers play the same content)
- Exciters driven by 3.5mm jack input to LQ-AMP10W (not controllable via GPIO)

---

## Quick Start

### What you are building

- **Primary path:** Tsunami SD card → Audio Out 1L → GF1002 amplifier → Spot speaker(s).
- **Exciter path:** Tsunami auxiliary output (3.5mm jack) → LQ-AMP10W L+R inputs → Left + Right exciter panels.
- **Control path:** ESP32-S3 UART (GPIO17/18) → Tsunami RXI/TXO at 57600 baud. Scene logic sends serial commands to play WAV files on demand.

### Wire color convention (recommended)

- Red: +5V
- Black: GND
- Orange: Tsunami Audio Out (unbalanced RCA or 1/8" aux)
- Grey: Audio signal ground (sleeve of jack/RCA)
- White: UART TX (GPIO17 → Tsunami RXI)
- Green: UART RX (GPIO18 → Tsunami TXO)

If you are also cutting LED strips in this build, follow addressable reconnect pathway rules in [LED_STRIP_CUTTING_PLAN.md](LED_STRIP_CUTTING_PLAN.md) (DOUT -> next DIN continuity is mandatory).

### Bench order (do this in sequence)

1. Power the Tsunami and copy `tsunami.ini` to the Tsunami SD card root with `BAUD=57600`, `MONO=1`, `SERIAL=1`.
2. Power the ESP32-S3. 
3. Wire ESP32 GPIO17 (TX) → Tsunami RXI, GPIO18 (RX) → Tsunami TXO, plus common ground. Verify UART connection.
4. Power the GF1002 amplifier. 
5. Wire Tsunami Audio Out 1L → GF1002 L input (or both L+R for stereo).
6. Connect a spot speaker to GF1002 output. Test by sending UART command to play a WAV file.
7. Power the LQ-AMP10W.
8. Wire Tsunami auxiliary output (3.5mm jack) → LQ-AMP10W L+R inputs.
9. Connect exciters to LQ-AMP10W outputs. Verify exciters vibrate when Tsunami plays audio.

---

## Tsunami WAV Trigger UART test (confirmed for Audio Out 1L)

- Use UART1 on the ESP32-S3: `GPIO17` -> Tsunami `RXI`, `GPIO18` -> Tsunami `TXO`, plus common ground.
- Set `AUDIO_UART_BAUDRATE = 57600` in `config.py` and upload the working `code.py` test harness.
- Confirm `tsunami.ini` is copied to the Tsunami SD card root and contains `BAUD=57600`, `MONO=1`, `SERIAL=1`.
- Run the board and verify the Tsunami green track indicator lights when `track_play_poly()` is called.
- This test currently validates the Tsunami output path for Audio Out 1L only. Other outputs should be tested in future wiring runs.

---

## 1) Audio Control Architecture

### 1.1 Tsunami → GF1002 speaker output

Tsunami Audio Out 1L is a mono, unbalanced 1V p-p line-level output. Connect it directly to the GF1002 L input:

- Tsunami Audio Out 1L (tip) → GF1002 L input
- Tsunami GND (sleeve) → GF1002 GND
- GF1002 R input → GF1002 GND (tie low for mono operation, or wire to Audio Out 1R for stereo if available)

The GF1002/PAM8403 amplifies the Tsunami line output and drives one or more 1" spot speakers in parallel.

### 1.2 Tsunami auxiliary output → LQ-AMP10W → Stereo Exciters

The Tsunami has an auxiliary 3.5mm jack output. This output is driven through a series resistor to the LQ-AMP10W L and R inputs. 

- Tsunami aux jack (left/tip) → LQ-AMP10W L input
- Tsunami aux jack (right/ring) → LQ-AMP10W R input  
- Tsunami aux jack (ground/sleeve) → LQ-AMP10W GND and ESP32-S3 GND (common reference)

The LQ-AMP10W drives stereo exciters. Both exciters play whenever the Tsunami is playing audio (no separate enable pin). This design makes the diorama box resonate in stereo with all soundscapes.

### 1.3 ESP32-S3 UART → Tsunami (serial control)

The ESP32-S3 sends serial commands to the Tsunami at 57600 baud to trigger WAV playback:

- ESP32-S3 GPIO17 (TX) → Tsunami RXI (receives commands from ESP32)
- ESP32-S3 GPIO18 (RX) → Tsunami TXO (receives status from Tsunami)
- Common GND between ESP32-S3 and Tsunami

Scene logic uses `hardware/audio.py` to send UART commands like `p001\r` (play track 1, mono) or `P001\r` (play track 1, looping).

---

## 2) Pin/Channel Allocation Table

### ESP32-S3 UART Pin Assignments (Tsunami control)

| Signal | ESP32-S3 GPIO | Tsunami pin |
|---|---|---|
| TX (send commands) | GPIO17 | RXI |
| RX (receive status) | GPIO18 | TXO |
| GND | GND | GND |

Set `AUDIO_UART_TX = board.GPIO17` and `AUDIO_UART_RX = board.GPIO18` in `config.py`. Baudrate is fixed at 57600.

---

## 3) Power Distribution

### 3.1 Amplifier power requirements

| Component | Supply | Max draw | Notes |
|---|---|---|---|
| Tsunami Super WAV Trigger | 5V USB or bus | ~100mA | Power from 5V bus; also has SD card draw |
| GF1002 (PAM8403) | 5V bus | ~1A at full volume | Power from 5V bus directly |
| LQ-AMP10W | Check datasheet | Up to 10W output | Verify supply voltage from LQ-AMP10W datasheet |

### 3.2 Common ground — mandatory

All modules must share a common GND:
- ESP32-S3 GND
- Tsunami GND
- GF1002 GND
- LQ-AMP10W GND
- Speaker GND (if applicable)
- Exciter GND
- 5V power supply GND

Floating or disconnected grounds cause hum, noise, and unreliable UART.

### 3.3 Decoupling capacitors

- 10µF ceramic across 5V/GND at Tsunami power input
- 100µF electrolytic across 5V/GND at GF1002 power input (PAM8403 draws inrush surge current)
- 10µF ceramic across LQ-AMP10W power input

---

## 4) Recommended Protective Components

| Component | Where | Why |
|---|---|---|
| 100µF electrolytic | Across 5V/GND at GF1002 power input | Absorbs PAM8403 inrush current on loud transients |
| 10µF ceramic | Across 5V/GND at Tsunami power input | Decouples power from digital noise |
| 10µF ceramic | Across 5V/GND at LQ-AMP10W power input | Stabilizes exciter amp supply |

No MOSFETs, pull-up resistors, or transistor driver stages are required in the Tsunami audio path.

---

## 5) Step-by-Step Wiring

### 5.1 ESP32-S3 UART → Tsunami control

1. Wire ESP32-S3 GPIO17 (TX) → Tsunami RXI (serial receive).
2. Wire ESP32-S3 GPIO18 (RX) → Tsunami TXO (serial transmit).
3. Wire ESP32-S3 GND → Tsunami GND (common reference).
4. Set `AUDIO_UART_TX = board.GPIO17` and `AUDIO_UART_RX = board.GPIO18` in `config.py`.
5. Set `AUDIO_UART_BAUDRATE = 57600` in `config.py`.
6. Copy `tsunami.ini` to the Tsunami SD card root with the following content:
   ```
   BAUD=57600
   MONO=1
   SERIAL=1
   ```

### 5.2 Tsunami Audio Out 1L → GF1002 amplifier → speaker(s)

1. Connect Tsunami Audio Out 1L (RCA or 1/8" jack tip) → GF1002 L input.
2. Connect Tsunami GND (RCA shield or 1/8" jack sleeve) → GF1002 GND input.
3. Connect GF1002 R input → GF1002 GND (for mono operation). Alternatively, wire to Tsunami Audio Out 1R for stereo.
4. Wire GF1002 Vdd (+5V) → 5V bus. Add 100µF capacitor across Vdd/GND at the board.
5. Wire GF1002 GND → common GND bus.
6. Connect GF1002 speaker outputs (left and right RCA, or wires) → speaker terminals.
7. Test: Power on and send UART command `p001\r` (play track 1, once) or `P001\r` (play track 1, looping). Confirm sound from speaker.

### 5.3 Tsunami auxiliary output (3.5mm jack) → LQ-AMP10W → exciters

1. Connect Tsunami auxiliary output jack (left/tip) → LQ-AMP10W L input jack.
2. Connect Tsunami auxiliary output jack (right/ring) → LQ-AMP10W R input jack.
3. Connect Tsunami auxiliary output jack (ground/sleeve) → LQ-AMP10W GND.
4. Verify LQ-AMP10W supply voltage from datasheet (do this before connecting exciters).
5. Wire LQ-AMP10W Vdd → appropriate power supply for the amp.
6. Wire LQ-AMP10W GND → common GND bus (same as Tsunami and ESP32-S3).
7. Connect LQ-AMP10W L output → Left exciter transducer terminals.
8. Connect LQ-AMP10W R output → Right exciter transducer terminals.
9. Test: Power on and play audio. Both exciters should vibrate with the sound.

Beginner checkpoint:
- Tsunami green track indicator lights when you send a play command.
- GF1002-driven speaker has sound when Tsunami plays.
- Both exciters vibrate with audio output.
- No heat, no hum, no resets.

---

## 6) Firmware Test Procedure

1. In `config.py`, set:
   ```python
   ENABLE_AUDIO = True
   ENABLE_AUDIO_UART = True
   AUDIO_UART_TX = board.GPIO17
   AUDIO_UART_RX = board.GPIO18
   AUDIO_UART_BAUDRATE = 57600
   ```

2. Power on the ESP32-S3 and Tsunami.

3. Open the CircuitPython REPL and test a play command:
   ```python
   from hardware import audio
   audio.play_audio(None, 1, loop=False)  # Play track 1 once
   ```
   Confirm sound from speaker.

4. Test looping:
   ```python
   audio.play_audio(None, 1, loop=True)  # Play track 1, looping
   ```

5. Test stop:
   ```python
   audio.stop_all()  # Stop all playback
   ```

Beginner pass/fail rule:
- Pass: Play commands trigger sound, Tsunami responds reliably, no resets.
- Fail: Silent, error messages, or board resets. Stop and check wiring before continuing.

---

## 7) Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| Tsunami green track LED does not light | UART RXI/TXO wires swapped, or baud rate mismatch | Verify GPIO17/18 wiring; confirm `tsunami.ini` has `BAUD=57600` |
| No sound from GF1002 speaker | Audio Out 1L wiring open, or GF1002 not powered | Check Tsunami RCA/jack → GF1002 L input; confirm 100µF cap on GF1002 power |
| Exciters not vibrating | Auxiliary jack output not connected, or LQ-AMP10W not powered | Check 3.5mm jack wiring; verify LQ-AMP10W supply voltage matches datasheet |
| Distorted or weak audio | Tsunami output impedance too high for GF1002 input impedance; or GF1002 volume pot at minimum | Check GF1002 volume control; verify input wiring |
| UART errors in CircuitPython REPL | GPIO17/18 already claimed by another module, or UART timeout too short | Check `config.py` for GPIO conflicts; increase timeout if needed |
| One exciter works, other does not | LQ-AMP10W stereo channel broken, or right jack contact dirty | Clean 3.5mm jack contacts; test R output directly with multimeter |
| Hum from any output | Ground not shared between modules | Check that all GND wires connect to common bus (Tsunami, ESP32, GF1002, LQ-AMP10W, power supply) |

---

## 8) Bench Safety Rules (Read Before Power-On)

1. Power off before moving wires.
2. Verify UART baud rate in `config.py` before first power-on.
3. Confirm LQ-AMP10W supply voltage before connecting exciters — over-voltage damages the amp.
4. Connect Tsunami GND to ESP32-S3 GND before connecting any signal wires (UART, audio).
5. If anything gets warm unexpectedly, power off immediately.

---

## 9) Tsunami WAV File Storage & Organization

Store WAV files on the Tsunami SD card. Tsunami plays mono, 44.1kHz 16-bit WAV files up to ~100 seconds each. Organize by soundscape:

```
/audio/
  /shire_spring_dawn/
    track_001_birds_chorus.wav
    track_002_stream_flowing.wav
    track_003_wind_foliage.wav
    track_004_rooster_distant.wav
    track_005_bell_toll.wav
  /shire_spring_evening/
    track_010_crickets_frogs.wav
    track_011_evening_birds.wav
  /shire_summer_thunderstorm/
    track_020_thunder_base.wav
    track_021_thunder_crack_1.wav
    track_022_heavy_rain.wav
  /events/
    track_100_dragon_roar.wav
    track_101_party_music.wav
    track_102_deep_rumble_exciter.wav
```

Note: Tsunami track numbers are sequential from the SD card root. Use padding in the filename (001, 002, ...) to ensure correct numbering.
