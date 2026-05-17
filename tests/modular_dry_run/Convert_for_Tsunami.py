"""Tsunami command conversion helpers.

Single source of truth for Tsunami serial framing, length calculation,
output index conversion, and little-endian encoding.
"""

SOM1 = 0xF0
SOM2 = 0xAA
EOM = 0x55

CMD_CONTROL_TRACK = 0x03
CMD_STOP_ALL = 0x04

PLAY_SOLO = 0x00
PLAY_POLY = 0x01
PAUSE = 0x02
RESUME = 0x03
STOP = 0x04
LOOP_ON = 0x05
LOOP_OFF = 0x06
LOAD = 0x07


# In mono firmware, Tsunami exposes 8 mono outputs. Physical stereo-pair labels
# map to mono output numbers as follows:
# 1L->1, 1R->2, 2L->3, 2R->4, 3L->5, 3R->6, 4L->7, 4R->8
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
    if out < 1 or out > 8:
        raise ValueError("output_number must be 1-8")
    return out - 1


def physical_label_to_output_number(label):
    """Convert physical Tsunami label (e.g. '4L') to mono output number (1-8)."""
    normalized = str(label).strip().upper()
    if normalized not in PHYSICAL_LABEL_TO_OUTPUT_NUMBER:
        raise ValueError("unknown physical label: %s" % label)
    return PHYSICAL_LABEL_TO_OUTPUT_NUMBER[normalized]


def physical_label_to_index(label):
    """Convert physical label to Tsunami command index (0-7)."""
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


def build_control_track(track_number, output_number, control_code=PLAY_POLY, lock_voice=False):
    """Build CONTROL_TRACK command frame.

    Data layout:
    - control code (1 byte)
    - track number LE (2 bytes)
    - output index 0-7 (1 byte)
    - flags (1 byte)
    """
    track = int(track_number)
    if track < 1 or track > 4096:
        raise ValueError("track_number must be 1-4096")

    output_index = output_number_to_index(output_number)
    flags = 0x01 if lock_voice else 0x00

    data = [int(control_code)]
    data += u16_le(track)
    data += [output_index, flags]

    return build_frame(CMD_CONTROL_TRACK, data)


def build_stop_all():
    """Build STOP_ALL frame."""
    return build_frame(CMD_STOP_ALL)


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
