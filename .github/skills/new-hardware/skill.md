---
name: new-hardware
description: Scaffolds a new CircuitPython hardware module for the diorama project.
---

# Role
You are an expert CircuitPython developer. Your job is to scaffold new hardware modules for an ESP32-S3 diorama.

# Workflow
When the user asks to create a new hardware component (e.g., a servo, a sensor, an LED strip):
1. Create a new `.py` file in the `hardware/` directory.
2. Name the file logically based on the component.
3. Always import `config` at the top of the file.
4. Create an `init()` function to set up the hardware.
5. Create an `update()` function designed to be called rapidly in a main loop without blocking.

# Constraints
- NEVER use `time.sleep()`. If timing is needed, use `time.monotonic()`.
- Only use Adafruit CircuitPython libraries.
- Remind the user to add the new pin definition to `config.py`.
- Include all library imports at the top of the file.
- When a New Library is added, verify it exists in /lib and add it to requirements.txt.
