---
name: new-scene
description: Scaffolds a new Scene orchestration module for the diorama (e.g., Thunderstorm, Party), coordinating multiple hardware components using non-blocking timers.
---

# Role
You are an expert CircuitPython developer. Your job is to create a new "Scene" module that orchestrates lighting, motion, and sound for the diorama over a timeline.

# Workflow
When the user asks to create a new scene (e.g., "Dragon Arrival", "Thunderstorm"):
1. Create a new `.py` file in the `logic/` directory (e.g., `logic/scene_dragon.py`).
2. Import `time`, `config`, and any necessary hardware modules (`hardware.lighting`, `hardware.motion`, etc.).
3. Scaffold a state-machine or step-based sequence. Provide these three standard functions:
   - `start()`: Sets up the initial hardware states for the start of the scene (e.g., dims the main lights, resets servos).
   - `update()`: A non-blocking function intended to run continuously in the main loop. It must use `time.monotonic()` to track how much time has passed since `start()` was called, and trigger the next step of the scene accordingly (e.g., "if 2 seconds have passed, flash lightning; if 3 seconds have passed, play thunder").
   - `stop()`: Cleans up the scene and safely resets all hardware before transitioning to a different scene.

# Constraints
- NEVER use `time.sleep()`. All animation and sequence timing MUST rely on `time.monotonic()`.
- The `update()` function must return instantly so it does not block the main `code.py` loop from reading sensors.
- Use highly descriptive variable names for timestamps (e.g., `scene_start_time`, `last_lightning_strike`).
- Add comments explaining the "script" of the scene (what happens at second 1, second 2, etc.).
- Include all library imports at the top of the file.
- When a New Library is added, verify it exists in /lib and add it to requirements.txt.
