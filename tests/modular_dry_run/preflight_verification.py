"""Preflight checks for modular dry-run suite.

This script performs static validation before running on hardware:
- Confirms required ground segment IDs exist in lights.json.
- Confirms planned output numbers are in 1..8.
- Confirms planned track IDs are in 1..4096.
- Prints Tsunami CONTROL_TRACK frames with LE track bytes.

It avoids hardware imports so it can run as a quick host-side sanity check.
"""

import json
from pathlib import Path

from tests.modular_dry_run import Convert_for_Tsunami as cft

MIN_TRACK = 1
MAX_TRACK = 4096
MIN_OUTPUT = 1
MAX_OUTPUT = 8


AUDIO_PLAYS = [
    ("Smial1 start", 4, 310),
    ("Smial1 end", 4, 311),
    ("Smial2 start", 2, 312),
    ("Smial2 end", 2, 314),
    ("Smial3 start", 3, 314),
    ("Smial3 end", 3, 316),
    ("Stream start", 4, 316),
    ("Sky left", cft.physical_label_to_output_number("4L"), 1),
    ("Sky right", cft.physical_label_to_output_number("4R"), 2),
]

REQUIRED_GROUND_SEGMENTS = [
    "smial_1",
    "chimney_smial_1",
    "smial_2",
    "chimney_smial_2",
    "smial_3_lower",
    "smial_3_main",
    "smial_3_upper",
    "chimney_smial_3",
]


def _workspace_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _load_lights_json(root: Path) -> dict:
    lights_path = root / "lights.json"
    with lights_path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def _collect_segment_ids(lights_data: dict) -> set:
    segment_ids = set()
    for strip_name in (
        "strip_ground_effects",
        "strip_water_effects",
        "strip_sky_arc",
        "strip_standard_ws2812b",
    ):
        strip = lights_data.get(strip_name, {})
        for segment in strip.get("segments", []):
            seg_id = segment.get("id")
            if seg_id:
                segment_ids.add(seg_id)
    return segment_ids


def _validate_audio_plan() -> bool:
    print("[PRECHECK] Audio mapping and Tsunami frame validation")
    ok = True

    for label, output_number, track_number in AUDIO_PLAYS:
        if not (MIN_OUTPUT <= int(output_number) <= MAX_OUTPUT):
            ok = False
            print("  FAIL %-14s output %s is outside 1..8" % (label + ":", output_number))
            continue

        if not (MIN_TRACK <= int(track_number) <= MAX_TRACK):
            ok = False
            print("  FAIL %-14s track %s is outside 1..4096" % (label + ":", track_number))
            continue

        info = cft.describe_control_track(track_number, output_number)
        frame = cft.build_control_track(track_number=track_number, output_number=output_number)
        print(
            "  OK   %-14s out=%d idx=%d track=%d le=%02X %02X frame=%s"
            % (
                label + ":",
                info["output_number"],
                info["output_index"],
                info["track_number"],
                info["track_lsb"],
                info["track_msb"],
                frame.hex(),
            )
        )

    return ok


def _validate_segments(root: Path) -> bool:
    print("[PRECHECK] Ground segment coverage validation")
    lights_data = _load_lights_json(root)
    known_segment_ids = _collect_segment_ids(lights_data)

    missing = [seg for seg in REQUIRED_GROUND_SEGMENTS if seg not in known_segment_ids]
    if missing:
        print("  FAIL missing segment IDs: %s" % ", ".join(missing))
        return False

    print("  OK   all required smial/chimney ground segments exist")
    return True


def main() -> int:
    root = _workspace_root()
    print("[PRECHECK] Workspace root: %s" % root)

    audio_ok = _validate_audio_plan()
    segments_ok = _validate_segments(root)

    if audio_ok and segments_ok:
        print("[PRECHECK] PASS")
        return 0

    print("[PRECHECK] FAIL")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
