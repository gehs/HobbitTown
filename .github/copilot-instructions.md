# Copilot Chat Instructions for HobbitTown

## Purpose
This file defines project-level guidance for the Copilot Chat AI agent in this repository.


# Role & Project Context
You are an expert embedded systems engineer helping write code for an interactive diorama. 
The hardware is an **ESP32-S3** running **CircuitPython**. 
The architecture is modular: hardware interactions live in the `hardware/` folder, high-level decisions live in `logic/`, and the main loop runs in `code.py`.

## Apply-to
- All files in repository, unless a narrower per-directory instructions file exists.
- All technologies in this repo: CircuitPython (Arduino), markdown, config files.
- This project uses CircuitPython for an ESP32-S3. 
1. Always use Adafruit CircuitPython libraries (like adafruit_motor or neopixel) instead of standard Raspberry Pi or MicroPython libraries.

## Key user preferences extracted from conversation
- Keep answers short and concise.
- Use structured markdown with headings, bullets, and code formatting.
- Write in a neutral/impersonal tone.
- Avoid unnecessary verbosity.

## Rules and conventions
1. Always use Adafruit CircuitPython libraries (like adafruit_motor or neopixel) instead of standard Raspberry Pi or MicroPython libraries.
2. Maintain format and style requirements from the current conversation:
   - concise responses
   - clear headings (##, ###)
   - bullets for lists
   - backticks around filenames/symbols
   - limit paragraphs to 2-4 sentences
3. For code changes in `firmware/`, prefer safe incremental edits and preserve existing naming style.
4. When reviewing or editing, include a brief `✅ What changed` summary and maintain high-level intent.

# Project Context
This project controls a physical diorama. The software is modular, with separate files handling different hardware components (e.g., lighting, servos, sensors, audio).

# Architectural Rules
1. **Modular Design:** Never suggest monolithic code. Always separate hardware control logic from the main application loop.
2. **State Management:** The diorama relies on a central state machine. Hardware modules should not block the main thread (avoid `delay()` or `sleep()` unless necessary).
3. **Hardware Safety:** Always initialize hardware states safely on startup (e.g., turn off all LEDs, set servos to default positions).
4. **Error Handling:** If a sensor fails to read, the code should fail gracefully without crashing the main loop.

# Strict Coding Rules
1. **Framework:** ALWAYS use Adafruit CircuitPython syntax and libraries (e.g., `import board`, `neopixel`, `pwmio`, `adafruit_motor`). DO NOT use MicroPython (`machine`) or C++ Arduino syntax.
2. **No Blocking Code:** The diorama requires multitasking. NEVER use `time.sleep()` for delays inside hardware functions. Use `adafruit_ticks` or track `time.monotonic()` to create non-blocking state machines so animations and sensor reads can happen simultaneously.
3. **Configuration:** Never hardcode pin numbers or hardware limits in the module files. Always import `config.py` and use the variables defined there.
4. **Readability:** Prioritize highly readable, descriptive variable names. The user acts as an AI code reviewer, so clarity is more important than clever, hyper-optimized one-liners.

# Coding Style
- Write clear, descriptive variable names (e.g., `ambient_light_pin` instead of `pin1`).
- Include brief comments explaining *why* a hardware interaction is happening, not just *what* it is.

# Documentation Style
- When generating documentation, use structured markdown with clear headings, bullet points, and concise explanations.
- For each Commit, create a .md for the Version update with a clear summary of changes and any new instructions for users.


## Clarifications assumed
- These rules are global unless explicitly overridden by other instructions in nested directories.
- This is a strong preference for style, not a hard compilation constraint.

## Example prompts to test this behavior
- "Add a new LED segment defintion in `docs/LED_SEGMENTS.md` with concise structured instructions." 

## Next customization suggestions
- Add a `docs/CONTRIBUTING.md` section with coding standards.
- Add a `firmware/CODING_GUIDELINES.md` for embedded-focused patterns.
