# Fix `board.IO2` / pin-name error

If the serial monitor is only showing partial chat output, use this note directly.

## 1) Enter the CircuitPython REPL

- In the serial monitor, **press any key**.
- Then type these **one line at a time**:

```python
import board
print(board.board_id)
print(dir(board))
```

This shows the board name and the **actual pin names** supported by your device.

## 2) Quick `config.py` fix

Try replacing the top of `config.py` with this:

```python
import board  # type: ignore

# --- LIGHTING ---
NEOPIXEL_PIN = board.NEOPIXEL
NUM_PIXELS = 120
BRIGHTNESS = 0.5

# --- I2C for PCA9685 PWM Drivers ---
I2C_SDA = board.SDA
I2C_SCL = board.SCL
PCA9685_ADDR1 = 0x40
PCA9685_ADDR2 = 0x41

# --- ATMOSPHERE (Fogger) ---
FOGGER_RELAY_PIN = board.D18  # change if this pin name is not listed by dir(board)
```

## 3) If `board.D18` also fails

Run:

```python
print(dir(board))
```

Then use one of the **exact names shown there** instead of `board.D18`.

## 4) Reload after saving

Press:

```text
CTRL-D
```

That soft-reboots CircuitPython and reruns `code.py`.
