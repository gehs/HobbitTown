import board  # type: ignore

# --- STARTUP / DRY-LOAD ---
ALLOW_MISSING_HARDWARE = True  # Boot cleanly even if no external components are wired yet

# Default to zero-wire upload testing. Turn these on as each component is actually connected.
ENABLE_LIGHTING = False    # True when the external LED strip is connected
ENABLE_MOTION = False      # True when PCA9685 + servos/blowers/vapor channels are connected
ENABLE_ATMOSPHERE = False  # True when the fogger relay is connected
ENABLE_WEB = True          # Safe to leave enabled for browser-based testing

# --- LIGHTING ---
NEOPIXEL_PIN = board.GPIO2   # Sky arc strip on GPIO2: dawn (19) + noon SK6812 (91) + dusk (19)
NUM_PIXELS = 129             # Total sky arc pixels
NEOPIXEL_GROUND_PIN = board.GPIO4  # Ground effects strip on GPIO4
NUM_PIXELS_GROUND = 153      # Total ground pixels: terrain(100) + lanterns(6) + fireflies(12) + stars(10) + lightning(10) + chimneys(7) + bridge_mist(8)
BRIGHTNESS = 0.5             # 0.0 to 1.0, matches C++ LED_BRIGHTNESS 128/255

# --- I2C for PCA9685 PWM Drivers ---
# This YD ESP32-S3 board does not expose GPIO22 in CircuitPython.
# Move the PCA9685 SCL wire to GPIO47 and keep SDA on GPIO21.
I2C_SDA = board.GPIO21
I2C_SCL = board.GPIO47
PCA9685_ADDR1 = 0x40
PCA9685_ADDR2 = 0x41

# --- ATMOSPHERE (Fogger) ---
FOGGER_RELAY_PIN = board.GPIO18  # GPIO18 relay control

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