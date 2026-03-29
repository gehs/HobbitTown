---
name: lighting-management
description: Manages lighting effects and dynamic updates for HobbitTown diorama.
---

# Role
You are a CircuitPython lighting expert. Create a module to manage lighting presets, segment updates, and non-blocking animations.

# Workflow
1. Build `hardware/lighting_manager.py` with:
   - init_lighting()
   - update_lighting(current_time)
   - set_segment_color(segment_id, rgb)
   - apply_preset(preset_name)
   - stop_lighting()
2. Use `time.monotonic()` for timers.
3. Load segments from `lights.json`.
4. Scale all RGB values by `config.BRIGHTNESS`.

# Constraints
- No blocking `time.sleep()` calls.
- update_lighting returns quickly.
- Handle missing segment IDs without crashing.

# Verification
- init_lighting sets all LEDs off.
- set_segment_color('sun', (255,255,255)) lights sun segment.
- apply_preset('storm') triggers storm state.