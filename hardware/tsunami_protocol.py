"""Tsunami Super WAV Trigger serial protocol helpers.

This module is the shared source of truth for serial framing, output mapping,
and little-endian encoding used across runtime and test code.
"""

SOM1 = 0xF0
SOM2 = 0xAA
EOM = 0x55

CMD_GET_VERSION = 0x01
CMD_GET_SYS_INFO = 0x02
CMD_CONTROL_TRACK = 0x03
CMD_STOP_ALL = 0x04
CMD_OUTPUT_VOLUME = 0x05
CMD_GET_STATUS = 0x07
CMD_TRACK_VOLUME = 0x08
CMD_TRACK_FADE = 0x0A

PLAY_SOLO = 0x00
PLAY_POLY = 0x01
PAUSE = 0x02
RESUME = 0x03
STOP = 0x04
LOOP_ON = 0x05
LOOP_OFF = 0x06
LOAD = 0x07

TSUNAMI_MIN_TRACK = 1
TSUNAMI_MAX_TRACK = 4096
TSUNAMI_MIN_OUTPUT_NUMBER = 1
TSUNAMI_MAX_OUTPUT_NUMBER = 8
TSUNAMI_MIN_GAIN_DB = -70
TSUNAMI_MAX_GAIN_DB = 10


PHYSICAL_LABEL_TO_OUTPUT_NUMBER = {
    "1L": 1,
    "1R": 2,
    "2L": 3,
    "2R": 4,
    "3L": 5,
    "3R": 6,
    "4L": 7,
    "4R": 8,
}


def output_number_to_index(output_number):
    """Convert user-facing output number 1-8 to Tsunami index 0-7."""
    out = int(output_number)
    if out < TSUNAMI_MIN_OUTPUT_NUMBER or out > TSUNAMI_MAX_OUTPUT_NUMBER:
        raise ValueError("output_number must be 1-8")
    return out - 1


def output_index_to_number(output_index):
    """Convert Tsunami index 0-7 to user-facing output number 1-8."""
    idx = int(output_index)
    if idx < 0 or idx > 7:
        raise ValueError("output_index must be 0-7")
    return idx + 1


def physical_label_to_output_number(label):
    """Convert physical Tsunami label (for example '4L') to output number."""
    normalized = str(label).strip().upper()
    if normalized not in PHYSICAL_LABEL_TO_OUTPUT_NUMBER:
        raise ValueError("unknown physical label: %s" % label)
    return PHYSICAL_LABEL_TO_OUTPUT_NUMBER[normalized]


def physical_label_to_index(label):
    """Convert physical Tsunami label (for example '4L') to index 0-7."""
    return output_number_to_index(physical_label_to_output_number(label))


def u16_le(value):
    """Encode unsigned 16-bit value as little-endian bytes (LSB first)."""
    val = int(value)
    if val < 0 or val > 65535:
        raise ValueError("unsigned 16-bit value out of range")
    return [val & 0xFF, (val >> 8) & 0xFF]


def s16_le(value):
    """Encode signed 16-bit value as little-endian bytes (two's complement)."""
    val = int(value)
    if val < -32768 or val > 32767:
        raise ValueError("signed 16-bit value out of range")
    if val < 0:
        val = 0x10000 + val
    return [val & 0xFF, (val >> 8) & 0xFF]


def build_frame(command, data=None):
    """Build Tsunami frame: SOM1 SOM2 LENGTH CMD DATA... EOM.

    LENGTH is total bytes including SOM, LENGTH, CMD, DATA, and EOM.
    """
    if data is None:
        data = []
    length = 2 + 1 + 1 + len(data) + 1
    return bytes([SOM1, SOM2, length, int(command)] + list(data) + [EOM])


def _validate_track_number(track_number):
    track = int(track_number)
    if track < TSUNAMI_MIN_TRACK or track > TSUNAMI_MAX_TRACK:
        raise ValueError("track_number must be 1-4096")
    return track


def _validate_gain_db(gain_db):
    gain = int(gain_db)
    if gain < TSUNAMI_MIN_GAIN_DB or gain > TSUNAMI_MAX_GAIN_DB:
        raise ValueError("gain_db must be from -70 to +10")
    return gain


def build_control_track(track_number, output_number, control_code=PLAY_POLY, lock_voice=False):
    """Build CONTROL_TRACK frame using output number 1-8."""
    output_index = output_number_to_index(output_number)
    return build_control_track_for_index(
        track_number=track_number,
        output_index=output_index,
        control_code=control_code,
        lock_voice=lock_voice,
    )


def build_control_track_for_index(track_number, output_index, control_code=PLAY_POLY, lock_voice=False):
    """Build CONTROL_TRACK frame using output index 0-7."""
    track = _validate_track_number(track_number)
    out_index = int(output_index)
    if out_index < 0 or out_index > 7:
        raise ValueError("output_index must be 0-7")

    flags = 0x01 if lock_voice else 0x00
    data = [int(control_code)]
    data += u16_le(track)
    data += [out_index, flags]
    return build_frame(CMD_CONTROL_TRACK, data)


def build_stop_all():
    """Build STOP_ALL frame."""
    return build_frame(CMD_STOP_ALL)


def build_output_volume(output_number, gain_db):
    """Build OUTPUT_VOLUME frame using output number 1-8."""
    output_index = output_number_to_index(output_number)
    return build_output_volume_for_index(output_index, gain_db)


def build_output_volume_for_index(output_index, gain_db):
    """Build OUTPUT_VOLUME frame using output index 0-7."""
    out_index = int(output_index)
    if out_index < 0 or out_index > 7:
        raise ValueError("output_index must be 0-7")
    gain = _validate_gain_db(gain_db)
    data = [out_index] + s16_le(gain)
    return build_frame(CMD_OUTPUT_VOLUME, data)


def build_track_volume(track_number, gain_db):
    """Build TRACK_VOLUME frame."""
    track = _validate_track_number(track_number)
    gain = _validate_gain_db(gain_db)
    data = u16_le(track) + s16_le(gain)
    return build_frame(CMD_TRACK_VOLUME, data)


def build_track_fade(track_number, target_gain_db, milliseconds, stop_at_end=False):
    """Build TRACK_FADE frame."""
    track = _validate_track_number(track_number)
    gain = _validate_gain_db(target_gain_db)
    millis = int(milliseconds)
    if millis < 0 or millis > 65535:
        raise ValueError("milliseconds must be 0-65535")
    stop_flag = 0x01 if stop_at_end else 0x00
    data = u16_le(track) + s16_le(gain) + u16_le(millis) + [stop_flag]
    return build_frame(CMD_TRACK_FADE, data)


def describe_control_track(track_number, output_number):
    """Return debug metadata for logs and troubleshooting."""
    lsb, msb = u16_le(track_number)
    return {
        "output_number": int(output_number),
        "output_index": output_number_to_index(output_number),
        "track_number": int(track_number),
        "track_lsb": lsb,
        "track_msb": msb,
    }


def frame_to_hex(frame_bytes):
    """Return frame bytes as uppercase hex string for debugging."""
    return " ".join("%02X" % byte for byte in frame_bytes)