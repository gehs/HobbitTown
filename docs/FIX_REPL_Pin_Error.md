# Fix `board.IO2` / pin-name error

If the serial monitor is only showing partial chat output, use this note directly.

## 1) Enter the CircuitPython REPL

1. Open the Serial Monitor in VS Code
Press Ctrl+Shift+P (or Cmd+Shift+P on Mac) to open the command palette
Type "Serial Monitor" and select "Serial Monitor: Open"
This should connect to your ESP32 board via USB
2. Enter the REPL
Once the serial monitor is open and showing CircuitPython output, press any key on your keyboard
You should see the >>> prompt appear
The board will pause its main program and enter interactive mode
3. Run Commands
At the >>> prompt, you can type Python commands
For example, to check your board pins as mentioned in the doc:

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
