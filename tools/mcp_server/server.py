"""
HobbitTown MCP Validation Server
Phase 0 + Phase 1: Hardware Inventory Validator

Runs on the host machine (not on the ESP32-S3).
Provides Copilot Chat tools to validate cross-file consistency
before flashing firmware to the device.

Tools (Phase 1):
    - validate_hardware_inventory: 5-rule cross-check across config.py, ref/materials.json, ref/lights.json
    - get_segment_ids:             returns all known LED segment IDs from ref/lights.json
    - get_device_inventory:        returns all device IDs and types from ref/materials.json
"""

import json
import re
import sys
from pathlib import Path

import mcp.server.stdio
import mcp.types as types
from mcp.server import Server

# ---------------------------------------------------------------------------
# Resolve repo root relative to this file (tools/mcp_server sits two levels down)
# ---------------------------------------------------------------------------
REPO_ROOT = Path(__file__).parent.parent.parent
CONFIG_PY   = REPO_ROOT / "config.py"
LIGHTS_JSON = REPO_ROOT / "ref" / "lights.json"
MATERIALS_JSON = REPO_ROOT / "ref" / "materials.json"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _load_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


def _parse_config_int(source: str, variable: str) -> int | None:
    """Extract an integer constant from config.py source text."""
    match = re.search(rf"^\s*{variable}\s*=\s*(\d+)", source, re.MULTILINE)
    return int(match.group(1)) if match else None


def _parse_config_hex(source: str, variable: str) -> str | None:
    """Extract a hex constant (e.g. 0x40) from config.py source text."""
    match = re.search(rf"^\s*{variable}\s*=\s*(0x[0-9a-fA-F]+)", source, re.MULTILINE)
    return match.group(1).lower() if match else None


def _parse_config_pin(source: str, variable: str) -> str | None:
    """Extract a board.GPIOx pin name from config.py source text."""
    match = re.search(rf"^\s*{variable}\s*=\s*board\.(\w+)", source, re.MULTILINE)
    return match.group(1) if match else None


def _parse_allow_missing(source: str) -> bool:
    """Return True if ALLOW_MISSING_HARDWARE is set to True in config.py."""
    match = re.search(r"^\s*ALLOW_MISSING_HARDWARE\s*=\s*(True|False)", source, re.MULTILINE)
    return match.group(1) == "True" if match else False


def _get_sky_segments(lights: dict) -> list:
    return lights.get("strip_sky_arc", {}).get("segments", [])


def _get_ground_segments(lights: dict) -> list:
    return lights.get("strip_ground_effects", {}).get("segments", [])


def _result_text(issues: list[dict]) -> str:
    """Format a list of validation issues as readable text."""
    if not issues:
        return "✅ All checks passed. No issues found."
    lines = []
    for issue in issues:
        icon = {"ERROR": "❌", "WARNING": "⚠️", "INFO": "ℹ️"}.get(issue["severity"], "•")
        lines.append(f"{icon} [{issue['severity']}] {issue['rule']}: {issue['message']}")
    errors   = sum(1 for i in issues if i["severity"] == "ERROR")
    warnings = sum(1 for i in issues if i["severity"] == "WARNING")
    summary  = f"\nSummary: {errors} error(s), {warnings} warning(s)."
    return "\n".join(lines) + summary


# ---------------------------------------------------------------------------
# Validation logic
# ---------------------------------------------------------------------------

def run_validate_hardware_inventory() -> str:
    issues: list[dict] = []

    # Load source files
    config_source = CONFIG_PY.read_text(encoding="utf-8")
    lights        = _load_json(LIGHTS_JSON)
    materials     = _load_json(MATERIALS_JSON)
    dry_load      = _parse_allow_missing(config_source)

    # Determine error severity — downgrade to INFO when dry-load is active
    hw_severity = "INFO" if dry_load else "ERROR"
    if dry_load:
        issues.append({
            "severity": "INFO",
            "rule": "DryLoad",
            "message": "ALLOW_MISSING_HARDWARE=True in config.py — hardware-presence errors reported as INFO.",
        })

    # --- Rule 1: NUM_PIXELS matches strip_sky_arc.total_pixels ---
    num_pixels_config = _parse_config_int(config_source, "NUM_PIXELS")
    num_pixels_lights = lights.get("strip_sky_arc", {}).get("total_pixels")
    if num_pixels_config is None:
        issues.append({"severity": "ERROR", "rule": "R1-SkyPixels",
                       "message": "NUM_PIXELS not found in config.py."})
    elif num_pixels_lights is None:
        issues.append({"severity": "ERROR", "rule": "R1-SkyPixels",
                       "message": "strip_sky_arc.total_pixels not found in lights.json."})
    elif num_pixels_config != num_pixels_lights:
        issues.append({"severity": hw_severity, "rule": "R1-SkyPixels",
                       "message": (
                           f"NUM_PIXELS in config.py ({num_pixels_config}) does not match "
                           f"strip_sky_arc.total_pixels in lights.json ({num_pixels_lights})."
                       )})

    # --- Rule 2: NUM_PIXELS_GROUND matches strip_ground_effects.total_pixels ---
    num_pixels_ground_config = _parse_config_int(config_source, "NUM_PIXELS_GROUND")
    num_pixels_ground_lights = lights.get("strip_ground_effects", {}).get("total_pixels")
    if num_pixels_ground_config is None:
        issues.append({"severity": "ERROR", "rule": "R2-GroundPixels",
                       "message": "NUM_PIXELS_GROUND not found in config.py."})
    elif num_pixels_ground_lights is None:
        issues.append({"severity": "ERROR", "rule": "R2-GroundPixels",
                       "message": "strip_ground_effects.total_pixels not found in lights.json."})
    elif num_pixels_ground_config != num_pixels_ground_lights:
        issues.append({"severity": hw_severity, "rule": "R2-GroundPixels",
                       "message": (
                           f"NUM_PIXELS_GROUND in config.py ({num_pixels_ground_config}) does not match "
                           f"strip_ground_effects.total_pixels in lights.json ({num_pixels_ground_lights})."
                       )})

    # --- Rule 3: Segment ranges do not overflow their strip pixel counts ---
    if num_pixels_config is not None:
        sky_max_allowed = num_pixels_config - 1
        for seg in _get_sky_segments(lights):
            seg_end = seg.get("range", [0, 0])[1]
            if seg_end > sky_max_allowed:
                issues.append({"severity": "WARNING", "rule": "R3-SkyRangeOverflow",
                               "message": (
                                   f"Sky segment '{seg['id']}' range end ({seg_end}) exceeds "
                                   f"max allowed index ({sky_max_allowed}) for NUM_PIXELS={num_pixels_config}."
                               )})

    if num_pixels_ground_config is not None:
        ground_max_allowed = num_pixels_ground_config - 1
        for seg in _get_ground_segments(lights):
            seg_end = seg.get("range", [0, 0])[1]
            if seg_end > ground_max_allowed:
                issues.append({"severity": "WARNING", "rule": "R3-GroundRangeOverflow",
                               "message": (
                                   f"Ground segment '{seg['id']}' range end ({seg_end}) exceeds "
                                   f"max allowed index ({ground_max_allowed}) for NUM_PIXELS_GROUND={num_pixels_ground_config}."
                               )})

    # --- Rule 4: PCA9685 addresses match between config.py and materials.json ---
    config_addr1 = _parse_config_hex(config_source, "PCA9685_ADDR1")
    config_addr2 = _parse_config_hex(config_source, "PCA9685_ADDR2")

    # Collect declared PCA9685 addresses from materials.json power_infrastructure
    materials_pca_addresses: list[str] = []
    for item in materials.get("power_infrastructure", []):
        if "PCA9685" in item.get("type", ""):
            raw = item.get("address", "")
            materials_pca_addresses.append(raw.lower())

    for config_var, config_val in [("PCA9685_ADDR1", config_addr1), ("PCA9685_ADDR2", config_addr2)]:
        if config_val is None:
            issues.append({"severity": "ERROR", "rule": "R4-PCA9685Address",
                           "message": f"{config_var} not found in config.py."})
        elif config_val not in materials_pca_addresses:
            issues.append({"severity": hw_severity, "rule": "R4-PCA9685Address",
                           "message": (
                               f"{config_var}={config_val} in config.py has no matching entry "
                               f"in materials.json power_infrastructure. "
                               f"Declared addresses: {materials_pca_addresses}."
                           )})

    # --- Rule 5: No duplicate GPIO pin assignments ---
    pin_vars = [
        "NEOPIXEL_PIN",
        "NEOPIXEL_GROUND_PIN",
        "FOGGER_RELAY_PIN",
        "I2C_SDA",
        "I2C_SCL",
    ]
    pin_map: dict[str, list[str]] = {}
    for var in pin_vars:
        pin = _parse_config_pin(config_source, var)
        if pin:
            pin_map.setdefault(pin, []).append(var)

    for pin, assigned_vars in pin_map.items():
        if len(assigned_vars) > 1:
            issues.append({"severity": "ERROR", "rule": "R5-DuplicateGPIO",
                           "message": (
                               f"GPIO pin {pin} is assigned to multiple variables: "
                               f"{', '.join(assigned_vars)}."
                           )})

    return _result_text(issues)


def run_get_segment_ids() -> str:
    lights = _load_json(LIGHTS_JSON)
    sky_ids    = [s["id"] for s in _get_sky_segments(lights)]
    ground_ids = [s["id"] for s in _get_ground_segments(lights)]
    trackers   = []
    if "sun_tracker" in lights.get("strip_sky_arc", {}):
        trackers.append(lights["strip_sky_arc"]["sun_tracker"]["id"])
    if "moon_tracker" in lights.get("strip_sky_arc", {}):
        trackers.append(lights["strip_sky_arc"]["moon_tracker"]["id"])

    lines = [
        f"Sky arc segments ({len(sky_ids)}): {', '.join(sky_ids)}",
        f"Ground segments ({len(ground_ids)}): {', '.join(ground_ids)}",
    ]
    if trackers:
        lines.append(f"Trackers: {', '.join(trackers)}")
    lines.append(f"\nTotal segments: {len(sky_ids) + len(ground_ids)}")
    return "\n".join(lines)


def run_get_device_inventory() -> str:
    materials = _load_json(MATERIALS_JSON)
    lines = []

    # Microcontrollers
    for mcu in materials.get("microcontrollers", []):
        lines.append(f"[mcu]    {mcu['id']} — {mcu['type']}")

    # Servos
    for group in materials.get("servos", []):
        for servo in group.get("assignments", []):
            lines.append(f"[servo]  {servo['id']} — {group['type']} at {servo['location']}")

    # Audio
    for group in materials.get("audio", []):
        for item in group.get("assignments", []):
            lines.append(f"[audio]  {item['id']} — {group['type']}")

    # LEDs
    for group in materials.get("leds", []):
        for item in group.get("assignments", []):
            lines.append(f"[led]    {item['id']} — {group['type']}")
        # Handle top-level SMD entry (no nested assignments)
        if "id" in group:
            lines.append(f"[led]    {group['id']} — {group['type']}")

    # Smoke generators
    for group in materials.get("smoke_generators", []):
        for item in group.get("assignments", []):
            lines.append(f"[smoke]  {item['id']} — {group['type']} at {item['location']}")

    # Power / infrastructure
    for item in materials.get("power_infrastructure", []):
        lines.append(f"[power]  {item['id']} — {item['type']}")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# MCP Server definition
# ---------------------------------------------------------------------------

server = Server("hobbittown-validator")


@server.list_tools()
async def list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="validate_hardware_inventory",
            description=(
                "Cross-validates config.py, lights.json, and materials.json for the HobbitTown diorama. "
                "Checks: (1) pixel counts match, (2) ground pixel counts match, "
                "(3) segment ranges don't overflow strip size, "
                "(4) PCA9685 I2C addresses are consistent, "
                "(5) no duplicate GPIO pin assignments. "
                "Returns ERRORs, WARNINGs, and INFOs. Use before editing firmware or wiring."
            ),
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
        types.Tool(
            name="get_segment_ids",
            description=(
                "Returns all valid LED segment IDs defined in lights.json, "
                "grouped by sky arc and ground effects. "
                "Use this when writing or reviewing scene files to ensure segment IDs are valid."
            ),
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
        types.Tool(
            name="get_device_inventory",
            description=(
                "Returns all device IDs and types declared in materials.json, "
                "including microcontrollers, servos, audio components, LEDs, smoke generators, and power. "
                "Use this when scaffolding new hardware modules or scene files."
            ),
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    if name == "validate_hardware_inventory":
        result = run_validate_hardware_inventory()
    elif name == "get_segment_ids":
        result = run_get_segment_ids()
    elif name == "get_device_inventory":
        result = run_get_device_inventory()
    else:
        result = f"Unknown tool: {name}"

    return [types.TextContent(type="text", text=result)]


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

async def main():
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options(),
        )


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
