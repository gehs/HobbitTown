#!/usr/bin/env python3
"""Extract HobbitTown pin constants and cross-check against board_profile_hybrid.json.

Usage:
  python extract_hobbittown_hardware.py /path/to/HobbitTown
  python extract_hobbittown_hardware.py /path/to/HobbitTown/config.py --board-profile /path/to/board_profile_hybrid.json

The script writes a markdown report to stdout. It does not modify repository files.
"""
from __future__ import annotations

import argparse
import ast
import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

PIN_RE = re.compile(r"^\s*([A-Z][A-Z0-9_]*)\s*=\s*board\.GPIO(\d+)\b")
BOOL_RE = re.compile(r"^\s*([A-Z][A-Z0-9_]*)\s*=\s*(True|False)\b")
NUM_RE = re.compile(r"^\s*([A-Z][A-Z0-9_]*)\s*=\s*(0x[0-9A-Fa-f]+|\d+(?:\.\d+)?)\b")


def resolve_paths(input_path: Path, board_profile: Optional[Path]) -> Tuple[Path, Optional[Path], Path]:
    if input_path.is_dir():
        repo_root = input_path
        config_path = repo_root / "config.py"
        profile_path = board_profile or repo_root / "board_profile_hybrid.json"
    else:
        config_path = input_path
        repo_root = config_path.parent
        profile_path = board_profile

    if not config_path.exists():
        raise FileNotFoundError(f"config.py not found: {config_path}")

    if profile_path is not None and not profile_path.exists():
        profile_path = None

    return config_path, profile_path, repo_root


def extract_config(config_path: Path) -> Dict[str, Any]:
    pins: List[Dict[str, Any]] = []
    flags: List[Dict[str, Any]] = []
    constants: List[Dict[str, Any]] = []

    for line_no, line in enumerate(config_path.read_text(encoding="utf-8").splitlines(), start=1):
        pin_match = PIN_RE.match(line)
        if pin_match:
            name, gpio = pin_match.groups()
            pins.append({"name": name, "gpio": f"GPIO{gpio}", "circuitpython_name": f"board.GPIO{gpio}", "line": line_no})
            continue

        bool_match = BOOL_RE.match(line)
        if bool_match:
            name, value = bool_match.groups()
            flags.append({"name": name, "value": value == "True", "line": line_no})
            continue

        num_match = NUM_RE.match(line)
        if num_match:
            name, value_text = num_match.groups()
            try:
                value = ast.literal_eval(value_text)
            except Exception:
                value = value_text
            constants.append({"name": name, "value": value, "line": line_no})

    return {"pins": pins, "flags": flags, "constants": constants}


def load_profile(profile_path: Optional[Path]) -> Dict[str, Any]:
    if profile_path is None:
        return {"pins_by_gpio": {}, "profile_loaded": False}
    data = json.loads(profile_path.read_text(encoding="utf-8"))
    pins_by_gpio: Dict[str, Dict[str, Any]] = {}
    for pin in data.get("pins", []):
        key = pin.get("pin")
        if key:
            pins_by_gpio[key] = pin
    return {"pins_by_gpio": pins_by_gpio, "profile_loaded": True, "raw": data}


def classify_pin(config_pin: Dict[str, Any], profile_pin: Optional[Dict[str, Any]]) -> Tuple[str, str]:
    if profile_pin is None:
        return "unknown", "pin not found in loaded board profile"
    configured_names = profile_pin.get("configured_names", []) or []
    if config_pin["name"] in configured_names:
        return "confirmed", "config constant appears in board profile configured_names"
    if configured_names:
        return "conflict", f"profile configured_names={configured_names}"
    if profile_pin.get("available_for_new_assignment") is False and profile_pin.get("assigned") is True:
        return "conflict", "profile marks pin assigned but not to this config constant"
    return "unknown", "profile does not name this config constant"


def make_markdown(config_path: Path, profile_path: Optional[Path], extracted: Dict[str, Any], profile: Dict[str, Any]) -> str:
    lines: List[str] = []
    lines.append("# HobbitTown hardware extraction report")
    lines.append("")
    lines.append(f"- config: `{config_path}`")
    lines.append(f"- board profile: `{profile_path}`" if profile_path else "- board profile: not loaded")
    lines.append("")

    lines.append("## Pin constants")
    lines.append("")
    lines.append("| constant | circuitpython pin | line | profile status | note |")
    lines.append("|---|---|---:|---|---|")
    profile_pins = profile.get("pins_by_gpio", {})
    for pin in extracted["pins"]:
        profile_pin = profile_pins.get(pin["gpio"])
        status, note = classify_pin(pin, profile_pin)
        lines.append(f"| `{pin['name']}` | `{pin['circuitpython_name']}` | {pin['line']} | {status} | {note} |")

    lines.append("")
    lines.append("## Hardware enable flags")
    lines.append("")
    lines.append("| flag | value | line |")
    lines.append("|---|---:|---:|")
    for flag in extracted["flags"]:
        lines.append(f"| `{flag['name']}` | `{flag['value']}` | {flag['line']} |")

    pixel_constants = [c for c in extracted["constants"] if c["name"].startswith("NUM_PIXELS") or c["name"] in {"BRIGHTNESS", "AUDIO_OUTPUT_COUNT", "AUDIO_UART_BAUDRATE"}]
    if pixel_constants:
        lines.append("")
        lines.append("## Selected numeric constants")
        lines.append("")
        lines.append("| constant | value | line |")
        lines.append("|---|---:|---:|")
        for const in pixel_constants:
            lines.append(f"| `{const['name']}` | `{const['value']}` | {const['line']} |")

    conflicts = []
    for pin in extracted["pins"]:
        status, note = classify_pin(pin, profile_pins.get(pin["gpio"]))
        if status == "conflict":
            conflicts.append((pin, note))

    lines.append("")
    lines.append("## Readiness")
    lines.append("")
    if conflicts:
        lines.append("`not ready for schematic capture`: one or more config/profile conflicts must be reconciled first.")
        for pin, note in conflicts:
            lines.append(f"- `{pin['name']}` on `{pin['circuitpython_name']}`: {note}")
    else:
        lines.append("`ready for reconciliation review`: no config/profile conflicts were detected by this script, but wiring docs still need manual cross-check.")

    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Extract HobbitTown hardware pin information.")
    parser.add_argument("path", help="Path to HobbitTown repo directory or config.py")
    parser.add_argument("--board-profile", help="Optional path to board_profile_hybrid.json")
    args = parser.parse_args()

    config_path, profile_path, _repo_root = resolve_paths(Path(args.path), Path(args.board_profile) if args.board_profile else None)
    extracted = extract_config(config_path)
    profile = load_profile(profile_path)
    print(make_markdown(config_path, profile_path, extracted, profile))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
