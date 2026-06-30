# ESP32 Drag/Drop Deploy Profile (Runtime Only)

Use this guide when you want the simplest safe copy to CIRCUITPY and want to omit non-runtime files.

## Copy These (Required Runtime)

- code.py
- config.py
- settings.toml (if your board workflow uses it)
- secrets.py (only when WiFi/web is enabled)
- logic/web_logic.py (only when web is enabled)
- logic/time_sync.py
- hardware/
- logic/
- lib/
- ref/lights.json
- static/ (only when web is enabled)

## Do Not Copy (Not Needed For Runtime)

- docs/
- tests/
- tools/
- __archival/
- .github/
- .venv/
- .vscode/
- README.md
- ref/board_profile_hybrid.json
- ref/materials.json
- ref/sounds.json
- ref/Components.json
- ref/shire_s3_pin_audit_v1.csv

## Minimal Profiles

### Profile A: Full Feature (Web On)
Copy: required runtime list above including secrets.py, logic/web_logic.py, and static/.

### Profile B: Minimal Runtime (Web Off)
Copy:
- code.py
- config.py
- hardware/
- logic/
- lib/
- ref/lights.json

Skip: secrets.py, static/.

## Common Failure Symptoms

- Missing ref/lights.json: lighting manager segment lookups fail.
- Missing lib/ modules: import errors at boot.
- Missing static/ with web enabled: web pages return file-not-found.
- Missing secrets.py with web enabled: WiFi setup is skipped/fails.

## Quick Verification After Copy

1. Board boots to REPL with no import exceptions.
2. Lighting setup initializes and segment map loads.
3. If web enabled, index and test pages open.
4. Scene loop runs without file-not-found errors.
