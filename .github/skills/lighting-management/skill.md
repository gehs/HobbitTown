---
name: lighting-management
description: Manages lighting effects and dynamic updates for HobbitTown diorama.
---

# Role
You are a CircuitPython lighting expert. Your task is to Evaluate and Update the lighting management module that controls the diorama's LED segments based on predefined presets and dynamic updates. You will implement/improve functions to initialize the lighting system, update the lighting state based on timers, set individual segment colors, and apply different lighting presets (e.g., storm, calm, party). Your code should be efficient, non-blocking, and robust against missing segment IDs or invalid preset names.

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
5. Maintain awareness of which lights are SK6812 vs WS2812 for correct color ordering.

# Constraints
- No blocking `time.sleep()` calls.
- update_lighting returns quickly.
- Handle missing segment IDs without crashing.
- Include all library imports at the top.
- When a New Library is added, verify it exists in /lib and add it to requirements.txt.

# Verification
- init_lighting sets all LEDs off.
- apply_preset('storm') triggers storm state.
- apply_preset('calm') triggers calm state.
- apply_preset('party') triggers party state.
- apply_preset('test') triggers test state.
- apply_preset('unknown') with unknown name does not crash.