import board

# --- LIGHTING ---
NEOPIXEL_PIN = board.IO2   # GPIO 2 for WS2812B LEDs
NUM_PIXELS = 120           # Total number of LEDs in the diorama
BRIGHTNESS = 0.5           # 0.0 to 1.0, matches C++ LED_BRIGHTNESS 128/255

# --- I2C for PCA9685 PWM Drivers ---
I2C_SDA = board.IO21
I2C_SCL = board.IO22
PCA9685_ADDR1 = 0x40
PCA9685_ADDR2 = 0x41

# --- AUDIO ---
AUDIO_TX_PIN = board.IO17
AUDIO_RX_PIN = board.IO16
GATE_VOICES_PIN = board.IO18  # For DFPlayer Spots
GATE_DEEP_PIN = board.IO19    # For DFPlayer Base
BASE_VOL = 15
SPOT_VOL = 15

# --- ATMOSPHERE (Fogger) ---
FOGGER_RELAY_PIN = board.IO18  # Note: Same as GATE_VOICES_PIN - potential conflict

# --- MOTION (Servos, Misters, Blowers, Speakers) ---
# Servo angles
SERVO_MIN_PULSE = 150
SERVO_MAX_PULSE = 600
DOOR_OPEN_ANGLE = 90
DOOR_CLOSED_ANGLE = 0

# --- TIMING ---
LOOP_DELAY = 0.01          # Main loop yield time
FOG_DURATION = 15           # seconds
FOG_INTERVAL = 300          # seconds (5 minutes)