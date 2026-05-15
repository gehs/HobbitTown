---
name: tsunami-audio-control
description: Implements Tsunami Super WAV Trigger audio control for CircuitPython diorama projects using mono firmware, SD card WAV tracks, serial command framing, little-endian track/gain/time encoding, output routing, volume, fades, loop control, and safe helper functions. Use when generating or reviewing code that sends commands to a Tsunami Super WAV Trigger, maps WAV files to track numbers, controls mono outputs, sets gain, starts/stops tracks, fades audio, or debugs Tsunami serial hex messages.
---

# Tsunami Audio Control

## Purpose

Use this skill when implementing audio playback control for the Tsunami Super WAV Trigger in the HobbitTown / diorama CircuitPython project.

This skill focuses on implementation accuracy:

- Tsunami serial command framing
- Track number encoding
- Mono output routing
- Gain and volume encoding
- Fade timing encoding
- SD card WAV file naming
- Safe CircuitPython helper functions
- Debugging generated hex commands

This skill is not primarily for creative soundscape planning. For creative planning, scene mood, sound component selection, sample search terms, and narrative sound design, use the `music-scape` skill first. Use this skill when moving from plan to implementation.

## Operating Assumptions

Unless the user states otherwise, assume:

- Device: Tsunami Super WAV Trigger
- Firmware mode: mono
- Storage: microSD card
- Audio files: `.wav`
- Control method: asynchronous serial from CircuitPython
- Project style: non-blocking CircuitPython modules for an ESP32-S3 diorama
- User-facing output numbers are `1` through `8`
- Tsunami serial output indexes are `0` through `7`

## Source Facts to Preserve

Tsunami plays WAV files from a FAT16 or FAT32 microSD card. In mono firmware, the WAV files must be 16-bit, 44.1 kHz mono files. Files must not contain metadata before the start of the audio or they may not play. All WAV files must be located in the root directory of the microSD card. Track numbers are taken from the leading number in the filename, from `1` to `4096`.

Tsunami serial messages use this frame:

```text
SOM1, SOM2, LENGTH, COMMAND, DATA..., EOM
```

Where:

```text
SOM1 = 0xF0
SOM2 = 0xAA
EOM  = 0x55
```

The `LENGTH` byte is the total message length, including `SOM1`, `SOM2`, `LENGTH`, `COMMAND`, all data bytes, and `EOM`.

All 16-bit values, including track numbers, gain values, and millisecond values, must be sent little-endian: least significant byte first, then most significant byte.

## SD Card and WAV File Rules

When creating or reviewing Tsunami audio plans:

1. Require `.wav` files, not `.mp3`.
2. For mono firmware, require:
   - 44.1 kHz
   - 16-bit
   - mono
   - no metadata before audio data
3. Place all WAV files in the root directory of the microSD card.
4. Name each file with a leading track number from `1` to `4096`.
5. Leading zeroes are allowed but not required.
6. Remind the user to reset or power-cycle Tsunami after changing SD card contents so it re-indexes tracks.

Examples:

```text
001_thunder_close.wav      -> track 1
002_thunder_far.wav        -> track 2
010_market_ambience.wav    -> track 10
438_barking_dog.wav        -> track 438
```

Avoid recommending MP3 files for Tsunami playback.

## Mono Output Rules

In mono mode, Tsunami provides 8 mono outputs.

The user will usually describe outputs as `1` through `8`, but serial commands use zero-based output indexes.

| User-facing output | Tsunami serial output index | Hex byte |
|---:|---:|---:|
| 1 | 0 | `0x00` |
| 2 | 1 | `0x01` |
| 3 | 2 | `0x02` |
| 4 | 3 | `0x03` |
| 5 | 4 | `0x04` |
| 6 | 5 | `0x05` |
| 7 | 6 | `0x06` |
| 8 | 7 | `0x07` |

Always perform this conversion explicitly in code:

```python
output_index = output_number - 1
```

Validate:

```python
1 <= output_number <= 8
```

## Encoding Rules

### Unsigned 16-bit Little-Endian

Use for:

- Track numbers
- Milliseconds
- Other unsigned 16-bit values

Examples:

```text
1       -> 0x01, 0x00
2       -> 0x02, 0x00
7       -> 0x07, 0x00
438     -> 0xB6, 0x01
1000 ms -> 0xE8, 0x03
4096    -> 0x00, 0x10
```

CircuitPython helper:

```python
def _u16_le(value):
    """Return unsigned 16-bit value as little-endian bytes."""
    value = int(value)
    if value < 0 or value > 65535:
        raise ValueError("unsigned 16-bit value out of range")
    return [value & 0xFF, (value >> 8) & 0xFF]
```

### Signed 16-bit Little-Endian

Use for:

- Gain in dB
- Target gain in dB

Tsunami gain values are signed dB values. Encode them as signed 16-bit two's-complement little-endian.

Common examples:

```text
-70 dB -> 0xBA, 0xFF
-50 dB -> 0xCE, 0xFF
-20 dB -> 0xEC, 0xFF
-10 dB -> 0xF6, 0xFF
  0 dB -> 0x00, 0x00
+10 dB -> 0x0A, 0x00
```

CircuitPython helper:

```python
def _s16_le(value):
    """Return signed 16-bit value as little-endian two's-complement bytes."""
    value = int(value)
    if value < -32768 or value > 32767:
        raise ValueError("signed 16-bit value out of range")
    if value < 0:
        value = 0x10000 + value
    return [value & 0xFF, (value >> 8) & 0xFF]
```

## Serial Frame Helper

Always build messages through a helper instead of manually writing long byte arrays.

```python
SOM1 = 0xF0
SOM2 = 0xAA
EOM = 0x55


def _frame(command, data=None):
    """Build a Tsunami serial command frame."""
    if data is None:
        data = []

    length = 2 + 1 + 1 + len(data) + 1
    return bytes([SOM1, SOM2, length, command] + data + [EOM])
```

Length reasoning:

```text
2 start bytes
+ 1 length byte
+ 1 command byte
+ N data bytes
+ 1 end byte
= total message length
```

Examples:

```text
No data bytes:  length = 5
1 data byte:    length = 6
3 data bytes:   length = 8
4 data bytes:   length = 9
5 data bytes:   length = 10
7 data bytes:   length = 12
```

## Command Constants

Use named constants.

```python
CMD_GET_VERSION = 0x01
CMD_GET_SYS_INFO = 0x02
CMD_CONTROL_TRACK = 0x03
CMD_STOP_ALL = 0x04
CMD_OUTPUT_VOLUME = 0x05
CMD_GET_STATUS = 0x07
CMD_TRACK_VOLUME = 0x08
CMD_TRACK_FADE = 0x0A
CMD_RESUME_ALL_SYNC = 0x0B
CMD_SAMPLERATE = 0x0C
CMD_SET_REPORTING = 0x0E
CMD_SET_INPUT_MIX = 0x0F
CMD_SET_MIDI_BANK = 0x10

PLAY_SOLO = 0x00
PLAY_POLY = 0x01
PAUSE = 0x02
RESUME = 0x03
STOP = 0x04
LOOP_ON = 0x05
LOOP_OFF = 0x06
LOAD = 0x07
```

## Required Command Builders

### Stop All Tracks

Purpose: stop all tracks immediately.

Frame:

```text
F0 AA 05 04 55
```

Code:

```python
def tsunami_stop_all():
    return _frame(CMD_STOP_ALL)
```

### Control Track

Purpose: play, pause, resume, stop, loop, unloop, or load a specific track.

Data layout:

```text
control code
track number LSB
track number MSB
output index, 0-7 in mono mode
flags
```

Length: `10`

Flags:

```text
0x00 = normal
0x01 = lock voice / prevent voice stealing
```

Code:

```python
def tsunami_control_track(track_number, control_code=PLAY_POLY, output_number=1, lock_voice=False):
    """Build CONTROL_TRACK command.

    track_number: 1-4096
    output_number: user-facing mono output number, 1-8
    lock_voice: True prevents the track voice from being stolen
    """
    if track_number < 1 or track_number > 4096:
        raise ValueError("track_number must be 1-4096")
    if output_number < 1 or output_number > 8:
        raise ValueError("output_number must be 1-8 in mono mode")

    output_index = output_number - 1
    flags = 0x01 if lock_voice else 0x00

    data = [control_code]
    data += _u16_le(track_number)
    data += [output_index, flags]

    return _frame(CMD_CONTROL_TRACK, data)
```

Example:

```python
cmd = tsunami_control_track(
    track_number=7,
    control_code=PLAY_POLY,
    output_number=4,
    lock_voice=True,
)
```

Expected hex:

```text
F0 AA 0A 03 01 07 00 03 01 55
```

Reasoning:

```text
F0 AA = start
0A    = total length 10
03    = CONTROL_TRACK
01    = PLAY_POLY
07 00 = track 7, little-endian
03    = serial output index 3, meaning user output 4
01    = lock voice flag
55    = end
```

### Output Volume

Purpose: set output/bus gain after tracks have been mixed.

Use this for final output level, not for preventing pre-mix clipping.

Data layout:

```text
output index, 0-7
gain LSB
gain MSB
```

Length: `8`

Gain range:

```text
-70 dB to +10 dB
```

Code:

```python
def tsunami_output_volume(output_number, gain_db):
    """Build OUTPUT_VOLUME command.

    output_number: user-facing mono output number, 1-8
    gain_db: signed dB value from -70 to +10
    """
    if output_number < 1 or output_number > 8:
        raise ValueError("output_number must be 1-8 in mono mode")
    if gain_db < -70 or gain_db > 10:
        raise ValueError("gain_db must be from -70 to +10")

    output_index = output_number - 1
    data = [output_index] + _s16_le(gain_db)

    return _frame(CMD_OUTPUT_VOLUME, data)
```

Example:

```python
cmd = tsunami_output_volume(output_number=2, gain_db=-10)
```

Expected hex:

```text
F0 AA 08 05 01 F6 FF 55
```

Reasoning:

```text
F0 AA = start
08    = total length 8
05    = OUTPUT_VOLUME
01    = serial output index 1, meaning user output 2
F6 FF = -10 dB, signed 16-bit little-endian
55    = end
```

### Track Volume

Purpose: set individual track gain before mixing.

Use this to reduce individual loud tracks before they mix together. If multiple full-scale tracks are mixed together, clipping can occur before output volume is applied. Lowering output volume will not repair clipping that already happened in the mix.

Data layout:

```text
track number LSB
track number MSB
gain LSB
gain MSB
```

Length: `9`

Gain range:

```text
-70 dB to +10 dB
```

Code:

```python
def tsunami_track_volume(track_number, gain_db):
    """Build TRACK_VOLUME command.

    track_number: 1-4096
    gain_db: signed dB value from -70 to +10
    """
    if track_number < 1 or track_number > 4096:
        raise ValueError("track_number must be 1-4096")
    if gain_db < -70 or gain_db > 10:
        raise ValueError("gain_db must be from -70 to +10")

    data = _u16_le(track_number)
    data += _s16_le(gain_db)

    return _frame(CMD_TRACK_VOLUME, data)
```

Example:

```python
cmd = tsunami_track_volume(track_number=1, gain_db=-10)
```

Expected hex:

```text
F0 AA 09 08 01 00 F6 FF 55
```

### Track Fade

Purpose: fade a track to a target gain over a specified number of milliseconds, optionally stopping the track at the end.

Data layout:

```text
track number LSB
track number MSB
target gain LSB
target gain MSB
milliseconds LSB
milliseconds MSB
stop flag, 0 or 1
```

Length: `12`

Code:

```python
def tsunami_track_fade(track_number, target_gain_db, milliseconds, stop_at_end=False):
    """Build TRACK_FADE command.

    track_number: 1-4096
    target_gain_db: signed dB value from -70 to +10
    milliseconds: 0-65535
    stop_at_end: True sends stop flag 1
    """
    if track_number < 1 or track_number > 4096:
        raise ValueError("track_number must be 1-4096")
    if target_gain_db < -70 or target_gain_db > 10:
        raise ValueError("target_gain_db must be from -70 to +10")
    if milliseconds < 0 or milliseconds > 65535:
        raise ValueError("milliseconds must be 0-65535")

    stop_flag = 0x01 if stop_at_end else 0x00

    data = _u16_le(track_number)
    data += _s16_le(target_gain_db)
    data += _u16_le(milliseconds)
    data += [stop_flag]

    return _frame(CMD_TRACK_FADE, data)
```

Example:

```python
cmd = tsunami_track_fade(
    track_number=2,
    target_gain_db=-50,
    milliseconds=1000,
    stop_at_end=True,
)
```

Expected hex:

```text
F0 AA 0C 0A 02 00 CE FF E8 03 01 55
```

Reasoning:

```text
F0 AA = start
0C    = total length 12
0A    = TRACK_FADE
02 00 = track 2, little-endian
CE FF = -50 dB, signed 16-bit little-endian
E8 03 = 1000 milliseconds, unsigned 16-bit little-endian
01    = stop at end
55    = end
```

### Reporting

Purpose: enable or disable track start/stop reporting from Tsunami.

Data layout:

```text
reporting state, 0 or 1
```

Length: `6`

Code:

```python
def tsunami_set_reporting(enabled=True):
    state = 0x01 if enabled else 0x00
    return _frame(CMD_SET_REPORTING, [state])
```

Example:

```python
cmd = tsunami_set_reporting(True)
```

Expected hex:

```text
F0 AA 06 0E 01 55
```

## Debug Output Requirement

When generating code that sends Tsunami commands, include a debug helper unless the project already has one:

```python
def hex_string(command_bytes):
    return " ".join("{:02X}".format(byte) for byte in command_bytes)
```

Example use:

```python
cmd = tsunami_output_volume(output_number=2, gain_db=-10)
print("[TSUNAMI]", hex_string(cmd))
uart.write(cmd)
```

Expected serial debug output:

```text
[TSUNAMI] F0 AA 08 05 01 F6 FF 55
```

## CircuitPython Serial Pattern

When creating a Tsunami audio module, use a project-specific UART setup. Do not guess pins if the project has `config.py`.

Prefer:

```python
import busio
import board
import config

tsunami_uart = busio.UART(
    config.TSUNAMI_TX_PIN,
    config.TSUNAMI_RX_PIN,
    baudrate=57600,
    timeout=0.01,
)
```

Then send commands using:

```python
def send_tsunami_command(command_bytes):
    print("[TSUNAMI]", hex_string(command_bytes))
    tsunami_uart.write(command_bytes)
```

If the project does not define Tsunami pins in `config.py`, ask the user or add a clear reminder:

```python
# Add these to config.py:
# TSUNAMI_TX_PIN = board.IOxx
# TSUNAMI_RX_PIN = board.IOyy
```

Do not introduce blocking delays. Use `time.monotonic()` for scheduled audio behavior.

## Safe High-Level Helpers

When useful, wrap low-level command builders in readable functions:

```python
def play_track(track_number, output_number=1, gain_db=None, lock_voice=False):
    if gain_db is not None:
        send_tsunami_command(tsunami_track_volume(track_number, gain_db))

    command = tsunami_control_track(
        track_number=track_number,
        control_code=PLAY_POLY,
        output_number=output_number,
        lock_voice=lock_voice,
    )
    send_tsunami_command(command)


def stop_track(track_number, output_number=1):
    command = tsunami_control_track(
        track_number=track_number,
        control_code=STOP,
        output_number=output_number,
        lock_voice=False,
    )
    send_tsunami_command(command)


def fade_out_track(track_number, milliseconds=1000, stop_at_end=True):
    command = tsunami_track_fade(
        track_number=track_number,
        target_gain_db=-70,
        milliseconds=milliseconds,
        stop_at_end=stop_at_end,
    )
    send_tsunami_command(command)


def set_output_gain(output_number, gain_db):
    command = tsunami_output_volume(output_number, gain_db)
    send_tsunami_command(command)
```

## Volume and Clipping Guidance

Distinguish clearly between output volume, track volume, and source file gain.

### Output Volume

Output volume is post-mix bus gain.

Use for:

- Lowering an entire speaker or output
- Balancing outputs
- Global scene loudness adjustment

Do not claim it prevents clipping caused by too many loud tracks being mixed.

### Track Volume

Track volume is pre-mix individual track gain.

Use for:

- Reducing a loud thunder track before it mixes with rain ambience
- Balancing individual samples
- Preventing multiple simultaneous tracks from clipping the mix

### Source File Gain

If a soundscape regularly plays multiple simultaneous tracks, recommend preparing the WAV files with conservative levels before loading them onto the SD card.

For layered ambience, recommend starting individual WAV files lower rather than trying to fix all loudness in code.

## Soundscape Implementation Flow

When implementing a soundscape from a `music-scape` plan:

1. Identify required tracks and assign stable track numbers.
2. Create an SD card file map.
3. Confirm each file is a 44.1 kHz, 16-bit mono WAV file.
4. Assign each track to a user-facing output number, 1-8.
5. Convert each output number to a serial output index, 0-7.
6. Set individual `TRACK_VOLUME` values if multiple tracks will mix together.
7. Use `CONTROL_TRACK` to play, stop, pause, resume, loop, or load tracks.
8. Use `TRACK_FADE` for transitions instead of abrupt stops when appropriate.
9. Print generated hex commands during development.
10. Remind the user to reset or power-cycle Tsunami after changing SD card files.

## Example Track Map Output

When asked to produce an implementation plan, include a table like this:

| Track | Filename | Purpose | User output | Serial output index | Initial track gain | Notes |
|---:|---|---|---:|---:|---:|---|
| 1 | `001_rain_loop.wav` | background rain | 1 | 0 | -12 dB | loop/long ambience |
| 2 | `002_thunder_close.wav` | close thunder | 2 | 1 | -8 dB | triggered after lightning |
| 3 | `003_wind_gust.wav` | wind gust | 1 | 0 | -16 dB | random occasional layer |

## Example Implementation Snippet

```python
# Example: thunderstorm scene audio commands

# Start rain ambience on user output 1 at reduced pre-mix gain.
send_tsunami_command(tsunami_track_volume(track_number=1, gain_db=-12))
send_tsunami_command(
    tsunami_control_track(
        track_number=1,
        control_code=PLAY_POLY,
        output_number=1,
        lock_voice=True,
    )
)

# Play thunder on user output 2 after a lightning event.
send_tsunami_command(tsunami_track_volume(track_number=2, gain_db=-8))
send_tsunami_command(
    tsunami_control_track(
        track_number=2,
        control_code=PLAY_POLY,
        output_number=2,
        lock_voice=False,
    )
)

# Fade out rain over 3 seconds and stop.
send_tsunami_command(
    tsunami_track_fade(
        track_number=1,
        target_gain_db=-70,
        milliseconds=3000,
        stop_at_end=True,
    )
)
```

## Validation Checklist

Before finalizing Tsunami code, verify:

- `SOM1` is `0xF0`.
- `SOM2` is `0xAA`.
- `EOM` is `0x55`.
- `LENGTH` is total framed message length, not just data length.
- Track numbers are encoded little-endian.
- Gain values are signed 16-bit little-endian.
- Millisecond values are unsigned 16-bit little-endian.
- User output `1-8` is converted to serial output index `0-7`.
- Gain values are within `-70` to `+10`.
- Track numbers are within `1` to `4096`.
- WAV files are in the SD card root.
- WAV files are 44.1 kHz, 16-bit mono for mono firmware.
- The user is reminded to reset or power-cycle after SD card changes.
- No `time.sleep()` is used in runtime scene code.
- Debug hex output is available during testing.

## Common Mistakes to Avoid

- Do not use MP3 files for Tsunami playback.
- Do not place WAV files in SD card subfolders.
- Do not forget to reset Tsunami after SD card changes.
- Do not treat the length byte as data length.
- Do not send 16-bit values big-endian.
- Do not send negative gain as a text string or unsigned decimal byte.
- Do not confuse user output `4` with serial output byte `0x04`; user output `4` is serial output index `0x03`.
- Do not lower output volume and claim it fixes pre-mix clipping.
- Do not block the main CircuitPython loop with `time.sleep()`.