---
name: ui
description: Design or modify a local web UI for the HobbitTown ESP32-S3 CircuitPython diorama. Use when asked to add dashboards, local controls, browser pages, buttons, sliders, preset selectors, sensor displays, scene controls, lighting controls, audio controls, HTTP routes, or documentation for web-based interaction with the diorama.
---

# UI

## Goal
Create a simple, local, maintainable UI that helps control and observe the diorama without tangling UI code with hardware logic.

## Before editing
Inspect existing UI/server files and identify the current stack before adding libraries. Look for:
- HTTP server or Wi-Fi setup files.
- Static HTML/CSS/JS files.
- Existing route handlers.
- `config.py` network or feature flags.
- Hardware or scene APIs exposed to the UI.

## Workflow
1. Identify the user-facing control or display needed.
2. Reuse existing UI patterns, routes, naming, and styling when available.
3. Keep UI code separate from hardware modules and scene modules.
4. Add or update route handlers only when necessary.
5. Validate and clamp incoming values such as brightness, servo angle, effect speed, volume, scene name, or preset name.
6. Return clear success/error messages for failed hardware interactions or invalid input.
7. Update relevant docs with how to access and use the UI.

## Design rules
- Keep the interface usable on desktop and mobile browsers.
- Prefer simple controls: buttons, sliders, selects, and status text.
- Include comments explaining why a control exists and how it maps to hardware or scene behavior.
- Avoid heavy frameworks unless the repository already uses them.
- Use Adafruit CircuitPython-compatible server libraries only when code runs on the board.

## Runtime rules
- UI request handlers must not block the main loop for long operations.
- Long-running scene or animation work should be started by the UI and advanced by non-blocking `update()` calls elsewhere.
- Failed sensor reads or hardware errors should produce safe UI feedback instead of crashing.

## Output checklist
After editing, include:
- New controls or routes.
- Files changed.
- Validation rules added.
- How to test from a phone or desktop browser.
