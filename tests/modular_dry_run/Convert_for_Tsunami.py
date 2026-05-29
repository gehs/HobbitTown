"""Compatibility wrapper around the shared Tsunami protocol helpers.

Use this module in modular dry-run scripts while relying on the production
protocol implementation in hardware/tsunami_protocol.py.
"""

import os
import sys

try:
    from hardware.tsunami_protocol import (
        CMD_CONTROL_TRACK,
        CMD_OUTPUT_VOLUME,
        CMD_STOP_ALL,
        CMD_TRACK_FADE,
        CMD_TRACK_VOLUME,
        EOM,
        LOAD,
        LOOP_OFF,
        LOOP_ON,
        PAUSE,
        PHYSICAL_LABEL_TO_OUTPUT_NUMBER,
        PLAY_POLY,
        PLAY_SOLO,
        RESUME,
        SOM1,
        SOM2,
        STOP,
        build_control_track,
        build_control_track_for_index,
        build_frame,
        build_output_volume,
        build_output_volume_for_index,
        build_stop_all,
        build_track_fade,
        build_track_volume,
        describe_control_track,
        frame_to_hex,
        output_index_to_number,
        output_number_to_index,
        physical_label_to_index,
        physical_label_to_output_number,
        s16_le,
        u16_le,
    )
except ImportError:
    # Allow direct execution from tests/modular_dry_run on desktop Python.
    REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    if REPO_ROOT not in sys.path:
        sys.path.insert(0, REPO_ROOT)

    from hardware.tsunami_protocol import (
        CMD_CONTROL_TRACK,
        CMD_OUTPUT_VOLUME,
        CMD_STOP_ALL,
        CMD_TRACK_FADE,
        CMD_TRACK_VOLUME,
        EOM,
        LOAD,
        LOOP_OFF,
        LOOP_ON,
        PAUSE,
        PHYSICAL_LABEL_TO_OUTPUT_NUMBER,
        PLAY_POLY,
        PLAY_SOLO,
        RESUME,
        SOM1,
        SOM2,
        STOP,
        build_control_track,
        build_control_track_for_index,
        build_frame,
        build_output_volume,
        build_output_volume_for_index,
        build_stop_all,
        build_track_fade,
        build_track_volume,
        describe_control_track,
        frame_to_hex,
        output_index_to_number,
        output_number_to_index,
        physical_label_to_index,
        physical_label_to_output_number,
        s16_le,
        u16_le,
    )


__all__ = [
    "CMD_CONTROL_TRACK",
    "CMD_OUTPUT_VOLUME",
    "CMD_STOP_ALL",
    "CMD_TRACK_FADE",
    "CMD_TRACK_VOLUME",
    "EOM",
    "LOAD",
    "LOOP_OFF",
    "LOOP_ON",
    "PAUSE",
    "PHYSICAL_LABEL_TO_OUTPUT_NUMBER",
    "PLAY_POLY",
    "PLAY_SOLO",
    "RESUME",
    "SOM1",
    "SOM2",
    "STOP",
    "build_control_track",
    "build_control_track_for_index",
    "build_frame",
    "build_output_volume",
    "build_output_volume_for_index",
    "build_stop_all",
    "build_track_fade",
    "build_track_volume",
    "describe_control_track",
    "frame_to_hex",
    "output_index_to_number",
    "output_number_to_index",
    "physical_label_to_index",
    "physical_label_to_output_number",
    "s16_le",
    "u16_le",
]


def run_protocol_vector_checks(verbose=True):
    """Validate core Tsunami command builders against known-good vectors."""
    vectors = [
        (
            "stop_all",
            build_stop_all(),
            bytes([0xF0, 0xAA, 0x05, 0x04, 0x55]),
        ),
        (
            "control_track",
            build_control_track(track_number=7, output_number=4, control_code=PLAY_POLY, lock_voice=True),
            bytes([0xF0, 0xAA, 0x0A, 0x03, 0x01, 0x07, 0x00, 0x03, 0x01, 0x55]),
        ),
        (
            "output_volume",
            build_output_volume(output_number=2, gain_db=-10),
            bytes([0xF0, 0xAA, 0x08, 0x05, 0x01, 0xF6, 0xFF, 0x55]),
        ),
        (
            "track_volume",
            build_track_volume(track_number=1, gain_db=-10),
            bytes([0xF0, 0xAA, 0x09, 0x08, 0x01, 0x00, 0xF6, 0xFF, 0x55]),
        ),
    ]

    all_ok = True
    for name, actual, expected in vectors:
        ok = actual == expected
        all_ok = all_ok and ok
        if verbose:
            status = "PASS" if ok else "FAIL"
            print("%s: %s" % (name, status))
            print("  actual:   %s" % frame_to_hex(actual))
            print("  expected: %s" % frame_to_hex(expected))

    return all_ok


if __name__ == "__main__":
    success = run_protocol_vector_checks(verbose=True)
    if success:
        print("All Tsunami protocol vectors passed.")
    else:
        print("One or more Tsunami protocol vectors failed.")
