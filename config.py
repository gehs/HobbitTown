import board  # type: ignore

# --- STARTUP / DRY-LOAD ---
ALLOW_MISSING_HARDWARE = True  # Boot cleanly even if no external components are wired yet

# Default to zero-wire upload testing. Turn these on as each component is actually connected.
ENABLE_LIGHTING = False    # True when the external LED strip is connected
ENABLE_MOTION = False      # True when PCA9685 + servos/blowers/vapor channels are connected
ENABLE_ATMOSPHERE = False  # True when the fogger relay is connected
ENABLE_WEB = True          # Safe to leave enabled for browser-based testing

# --- LIGHTING ---
NEOPIXEL_SKY_PIN = board.GPIO4   # Sky arc strip on GPIO4: dawn (19) + noon SK6812 (91) + dusk (19)
NUM_PIXELS_SKY = 129             # Total sky arc pixels
NEOPIXEL_GROUND_PIN = board.GPIO2  # Ground effects strip on GPIO2
NUM_PIXELS_GROUND = 153      # Total ground pixels: terrain(100) + lanterns(6) + fireflies(12) + stars(10) + lightning(10) + chimneys(7) + bridge_mist(8)
BRIGHTNESS = 0.25             # 0.0 to 1.0, matches C++ LED_BRIGHTNESS 128/255

# NOTE: Ground lights are wired to GPIO2 and sky lights are wired to GPIO4.

# --- I2C for PCA9685 PWM Drivers ---
# This YD ESP32-S3 board does not expose GPIO22 in CircuitPython.
I2C_SDA = board.GPIO8
I2C_SCL = board.GPIO9
PCA9685_ADDR1 = 0x40
PCA9685_ADDR2 = 0x41

# --- ATMOSPHERE (Fogger) ---
FOGGER_RELAY_PIN = board.GPIO18  # GPIO18 relay control

# --- AUDIO (Tsunami Super WAV Trigger) ---
ENABLE_AUDIO = True  # Set True after wiring the WAV Trigger and validating audio control mode.
ENABLE_AUDIO_I2C = False  # Enable Qwiic/I2C command mode for the WAV Trigger Pro.
ENABLE_AUDIO_UART = True  # Enable UART command mode for the WAV Trigger.
ENABLE_AUDIO_TRIGGERS = False  # Enable direct trigger outputs if the WAV Trigger is wired to ESP32 GPIO pins.
AUDIO_I2C_ADDR = 0x13  # Default 7-bit Qwiic address for WAV Trigger Pro.
AUDIO_UART_TX = board.GPIO17  # Use UART1 TX (U1TXD) for Tsunami RXI.
AUDIO_UART_RX = board.GPIO18  # Use UART1 RX (U1RXD) for Tsunami TXO.
AUDIO_UART_BAUDRATE = 57600
AUDIO_UART_TIMEOUT = 0.1

AUDIO_TRIGGER_1_PIN = board.GPIO10  # Available GPIO for audio trigger 1
AUDIO_TRIGGER_2_PIN = board.GPIO11  # Available GPIO for audio trigger 2


# --- MOTION (Servos, Vapor Channels, Blowers, Speakers) ---
# Servo angles
SERVO_MIN_PULSE = 150
SERVO_MAX_PULSE = 600
DOOR_OPEN_ANGLE = 90
DOOR_CLOSED_ANGLE = 0

# --- TIMING ---
LOOP_DELAY = 0.01          # Main loop yield time
FOG_DURATION = 15           # seconds
FOG_INTERVAL = 300          # seconds (5 minutes)