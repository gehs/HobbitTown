# Output templates

## Reconciliation table

| Item | `config.py` | `board_profile_hybrid.json` | wiring docs | status | action before PCB |
|---|---|---|---|---|---|

Status values:

- confirmed
- conflict
- unknown
- deprecated
- not pcb relevant

## PCB interface table

| Connector | Pin | Net name | Voltage | Direction | Destination | Protection / series part | Current rating | Test pad |
|---|---:|---|---|---|---|---|---|---|

## Schematic block plan

| Block | Purpose | Inputs | Outputs | Required components | Optional footprints | Risks |
|---|---|---|---|---|---|---|

## Fabrication readiness decision

Use exactly one of these conclusions:

- `ready for schematic capture`: source facts reconciled; PCB design can begin.
- `not ready for schematic capture`: source facts conflict or essential load details are missing.
- `ready for prototype fabrication review`: schematic and layout exist and checklist can be run.
- `not ready for fabrication`: unresolved electrical/mechanical/BOM risks remain.

Always explain the decision with specific blockers or evidence.
