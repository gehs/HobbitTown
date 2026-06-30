# ESP32-S3 CircuitPython Update Procedure

This document describes the safe step-by-step process for updating the ESP32-S3 CircuitPython project code on your `CIRCUITPY` drive.

For a faster runtime-only copy checklist, see `docs/DEPLOY_ESP32_DRAG_DROP.md`.

## What belongs on the ESP32 device

These files and folders should be copied to the device when updating the project:

- `code.py`
- `config.py`
- `logic/web_logic.py`
- `logic/time_sync.py`
- `hardware/`
- `logic/`
- `lib/`
- `ref/lights.json`
- `secrets.py` (only if you are using WiFi and have configured it)

### Why each item matters

- `code.py`: main CircuitPython loop and startup.
- `config.py`: pin assignments, feature flags, hardware mappings.
- `logic/web_logic.py`: local web UI, audio test endpoints, WiFi setup.
- `logic/time_sync.py`: clock/time helper used by scenes.
- `hardware/`: all hardware modules (lighting, motion, audio, atmosphere, etc.).
- `logic/`: scene and test orchestration code.
- `lib/`: CircuitPython library dependencies required by the code.
- `ref/lights.json`: lighting segment definitions used by `hardware/lighting_manager.py`.
- `secrets.py`: WiFi credentials.

## What stays on your PC and is not required on the device

These files are useful for development and documentation, but should not be copied to `CIRCUITPY` every update:

- `docs/`
- `.github/`
- `.git/`
- `README.md`, `docs/VSCODE_SETUP.md`
- `materials.json` (not referenced by runtime code)
- any editor or version-control files such as `.vscode/`

## Safe update workflow

1. Connect the ESP32-S3 to your PC by USB.
2. Wait for the `CIRCUITPY` drive to appear.
3. Back up the current device contents first.
   - Copy the existing `CIRCUITPY` contents to a local backup folder.
   - If you are using `secrets.py`, make sure to keep that backup.
4. If you want a fresh update, delete the old project files from `CIRCUITPY`:
   - `code.py`, `config.py`, `logic/web_logic.py`, `logic/time_sync.py`
   - `hardware/`, `logic/`, `lib/`
   - `ref/lights.json`
   - `secrets.py` only if you are replacing it intentionally
5. Copy the updated project files and folders from the repo to `CIRCUITPY`.
6. Leave any device-only files or settings alone.
   - Common examples: hidden CircuitPython system folders, `settings.toml`, old package caches.
7. Safely eject `CIRCUITPY` or press the reset button on the board after copy completes.

## Recommended “mistake-proof” method

### Option 1: mirror the project root into `CIRCUITPY`

Use a file-sync tool that compares and copies changed files rather than depending on manual drag-and-drop.

- Windows users: `FreeFileSync`, `SyncToy`, or `Robocopy`
- macOS/Linux users: `rsync`

This avoids missing files while copying. Only sync the project files listed in this guide.

### Option 2: use a simple PowerShell copy command

If you want a repeatable command instead of manual selection, use a folder sync command like this (example only):

```powershell
$source = 'C:\hTown\HobbitTown'
$dest = 'E:\'
robocopy $source $dest code.py config.py secrets.py /E
robocopy $source $dest ref\lights.json /E
robocopy $source $dest hardware logic lib /E
```

Notes:

- Replace `E:\` with your actual `CIRCUITPY` drive letter.
- The `/E` option copies subfolders including empty ones.
- This command does not delete extra files on the device; it only copies the repo contents.

### Option 3: build a dedicated sync profile

A GUI tool such as FreeFileSync can save a profile that:

- Copies `code.py`, `config.py`, `ref/lights.json`, `secrets.py`
- Copies `hardware/`, `logic/`, and `lib/`
- Excludes `docs/`, `.git/`, `.github/`, `README.md`, and other non-runtime paths
- Optionally shows you a preview before syncing

## When you can copy less

If only a single source file changed, you can copy just that file instead of the whole project.

Typical small updates:

- `config.py` change → copy only `config.py`
- `code.py` change → copy only `code.py`
- `hardware/audio.py` change → copy only `hardware/audio.py`
- library change → copy the changed file(s) in `lib/`

However, if you are not sure which files changed, copying the full runtime set is safer.

## Quick checklist for each ESP update

- [ ] `code.py`
- [ ] `config.py`
- [ ] `logic/web_logic.py`
- [ ] `logic/time_sync.py`
- [ ] `hardware/`
- [ ] `logic/`
- [ ] `lib/`
- [ ] `ref/lights.json`
- [ ] `secrets.py` if WiFi is used

## Troubleshooting

- If the board fails to boot after update, check the CIRCUITPY serial REPL for errors.
- Make sure the file names are correct and the folder structure on `CIRCUITPY` matches the repo.
- Keep `lib/` on the device if the project depends on the CircuitPython libraries in it.
- If you see stale behavior, try a clean copy:
  1. backup device files
  2. delete the project files from `CIRCUITPY`
  3. copy the runtime files/folders from the repo again
