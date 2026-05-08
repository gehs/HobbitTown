# Unit Tester Skill

## Purpose
This skill creates a **modular testing menu system** for ESP32-S3 CircuitPython. It generates a launcher `code.py` that sequentially runs separate test modules without file overwrites or drag-and-drop tedium. Each test module runs in isolation, and users interact via the serial terminal to proceed or pause.

## When to Use
- Testing multiple hardware modules (lighting, audio, motion, sensors) sequentially
- Before integrating components into main scenes
- When you need a clean test menu without modifying individual test files
- To isolate hardware testing from main application logic

## Requirements
- CircuitPython on ESP32-S3
- Serial terminal (PySerial, Arduino IDE Monitor, Thonny, or equivalent)
- Separate test files (e.g., `test_lighting.py`, `test_audio.py`, `test_motion.py`)
- `importlib.reload()` support in CircuitPython

## Generated Test Structure
The skill creates:
1. **Launcher `code.py`** — A menu system that:
   - Imports and runs test modules one at a time
   - Pauses between tests with `input()` prompts
   - Allows Y/N user input via serial terminal to proceed or stop
   - Uses `importlib.reload()` to re-import modules cleanly

2. **Modular test files** — Separate CircuitPython scripts (e.g., `test_lighting.py`, `test_audio.py`) that:
   - Initialize hardware (pins, objects, state)
   - Run hardware checks independently
   - Print status/results to serial for monitoring
   - Clean up or reset state on exit

## Usage
1. Invoke this skill to generate the launcher `code.py` and test module templates
2. Populate each test module with hardware initialization and test logic
3. Load `code.py` onto ESP32-S3 via USB or IDE
4. Open serial terminal (115200 baud)
5. Watch tests run; respond to prompts:
   - Type `Y` and press Enter to proceed to next test
   - Type `N` and press Enter to pause and standby
6. Monitor output for pass/fail indicators

## Example Launcher Pattern
```python
# code.py — Modular Test Menu Launcher
import importlib
import sys

print("=" * 50)
print("HobbitTown ESP32-S3 Test Menu")
print("=" * 50)

# List of test modules to run sequentially
TEST_MODULES = [
    "test_lighting",
    "test_audio",
    "test_motion",
]

for test_module in TEST_MODULES:
    print(f"\n[MENU] About to run: {test_module}")
    print("[MENU] Press Enter to start, or type 'SKIP' to skip this test...")
    
    user_input = input("> ").strip().upper()
    
    if user_input == "SKIP":
        print(f"[MENU] Skipped {test_module}. Moving to next...")
        continue
    
    try:
        print(f"[MENU] Loading {test_module}...")
        # Import the test module fresh each time
        if test_module in sys.modules:
            importlib.reload(sys.modules[test_module])
        else:
            importlib.import_module(test_module)
        
        print(f"[✓] {test_module} completed successfully.")
    
    except Exception as e:
        print(f"[✗] {test_module} failed: {e}")
    
    # Ask if user wants to continue
    print(f"\n[MENU] Continue to next test? (Y/N)")
    proceed = input("> ").strip().upper()
    
    if proceed != "Y":
        print("[MENU] Stopping. Entering standby mode.")
        print("[MENU] Press Ctrl+C to restart, or wait for watchdog...")
        while True:
            pass  # Hold until user manually resets

print("\n[MENU] All tests completed!")
print("[MENU] Entering standby mode...")
while True:
    pass  # Standby
```

## Example Test Module Structure
```python
# test_lighting.py — Isolated lighting test
import board
import neopixel
from config import *  # Import pin definitions

print("\n[TEST: lighting] Initializing...")

# Initialize hardware
strip = neopixel.NeoPixel(board.D1, NUM_LEDS, auto_write=False)

# Run tests
print("[TEST: lighting] Turning on all LEDs (white)...")
strip.fill((255, 255, 255))
strip.show()
print("[TEST: lighting] LEDs on. Check physical output.")

print("[TEST: lighting] Dimming to 50%...")
strip.fill((128, 128, 128))
strip.show()

print("[TEST: lighting] Turning off...")
strip.fill((0, 0, 0))
strip.show()

print("[✓ TEST: lighting] Complete!")
```

## Integration Notes
- Each test module should be **self-contained** — initialize hardware, run tests, clean up
- Use distinct print prefixes (e.g., `[TEST: module_name]`) for clarity in serial output
- Place test files in root or a dedicated `tests/` folder
- Do not modify test modules while launcher is running (let each reload complete first)
- Store pin definitions in `config.py` and import them in tests
- Use `importlib.reload()` to force fresh module state between test runs

## Skill Invocation
Use this skill when:
- Creating a multi-test menu launcher for ESP32-S3
- Testing hardware modules sequentially via serial terminal
- Building an interactive test harness without file overwrites
- Isolating hardware testing from main application logic

## Skill Restrictions
- Does not generate traditional host-side unit tests (use Python `unittest` elsewhere for that)
- Focuses on on-device CircuitPython testing, not integration tests
- Assumes CircuitPython 8.0+ with `importlib` support
- Test modules must be self-contained; do not share mutable global state between tests
