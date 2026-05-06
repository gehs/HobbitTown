# Unit Tester Skill

## Purpose
This skill generates isolated unit tests for `code.py` to verify the relay control logic without requiring actual hardware connections or modifications to `config.py`, `hardware/`, or other modules. Tests run in a mocked environment to confirm pin/wiring logic before integration.

## When to Use
- When developing or modifying `code.py` logic
- Before wiring hardware to ensure code correctness
- To isolate testing from config changes or hardware dependencies

## Requirements
- Python 3.8+ on host machine for running tests
- `unittest` and `unittest.mock` (standard library)
- No CircuitPython dependencies needed for tests

## Generated Test Structure
The skill creates `test_code.py` with:
- Mocked `digitalio` and `config` modules
- Tests for relay state changes, countdowns, and error handling
- Assertions for expected pin values and print outputs
- No actual GPIO access

## Usage
1. Invoke the skill to generate `test_code.py`
2. Run `python test_code.py` on host
3. Fix any failing tests in `code.py`
4. Only after all tests pass, update `config.py` or wire hardware

## Example Test Cases
- Test initial relay OFF state
- Test ON/OFF transitions with countdown
- Test active-low relay logic (if applicable)
- Test error handling for invalid pins

## Integration Notes
- Do not modify `config.py` or hardware modules until tests pass
- Do not modify `lighting.py` or other scene modules for these tests
- Do not modify `audio.py` or music-scape modules for these tests
- Do not modify `ui.py` or dashboard modules for these tests
- Do not modify `motion.py` of similar modules for these tests
- Confirm pin assignments match Current pinout before wiring
- Use this skill to validate logic before physical testing

## Skill Invocation
Use this skill when: creating unit tests for code.py, verifying relay logic without hardware, isolating code changes from config updates.

## Skill Restrictions
- Does not 'imagine' Pins or GPIO logic beyond what is defined in pin.md
- Focuses solely on code.py logic, not on config or hardware changes
- Requests Pin Updates prior to Guessing at Pin Assignments for tests
