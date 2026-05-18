import board  # type: ignore

# ============================================================================
# HOBBITTOWN HARDWARE CONFIGURATION
# ============================================================================
# Consolidated pin and hardware settings. All GPIO, I2C addresses, and
# hardware-specific limits are defined here. Hardware modules (lighting-*.py,
# motion.py, audio.py, atmosphere.py) import these values—they do NOT define
# pins directly.
# ============================================================================

# --- STARTUP / DRY-LOAD ---
ALLOW_MISSING_HARDWARE = True  # Boot cleanly even if no external components are wired yet
ENABLE_HARDWARE_VALIDATION = False  # Set True to run hardware diagnostics on startup

# Module enable flags - turn on as each component is actually wired
ENABLE_LIGHTING = False    # True when lighting strips are connected
ENABLE_MOTION = False      # True when PCA9685 + servos/blowers/vapor channels are connected
ENABLE_ATMOSPHERE = False  # True when the fogger relay is connected
ENABLE_AUDIO = True        # Set True after wiring the WAV Trigger and validating audio control mode
ENABLE_WEB = True          # Safe to leave enabled for browser-based testing

# ============================================================================
# HARDWARE: LIGHTING (NeoPixel LED Strips)
# ============================================================================
# Three independent lighting strips on separate GPIO pins.
# See lighting-sky.py, lighting-ground.py, lighting-stream.py for controllers.

# Sky arc strip: dawn (WS2812B, 19px) + noon (SK6812, 91px) + dusk (WS2812B, 19px)
NEOPIXEL_SKY_PIN = board.GPIO4
NUM_PIXELS_SKY = 129

# Ground effects strip: terrain(100) + lanterns(6) + fireflies(12) + stars(10) + lightning(10) + chimneys(7) + bridge_mist(8)
NEOPIXEL_GROUND_PIN = board.GPIO5  # Moved from GPIO2 for left-side NeoPixel grouping (GPIO4/5/6)
NUM_PIXELS_GROUND = 153

# Stream bead string: independent effect lighting
NEOPIXEL_STREAM_PIN = board.GPIO6
NUM_PIXELS_STREAM = 85

# Global lighting brightness limit (0.0 to 1.0; actual pin brightness adjusted per strip)
BRIGHTNESS = 0.25

# ============================================================================
# HARDWARE: I2C BUS (Shared by Motion and Audio)
# ============================================================================
# Note: This YD ESP32-S3 board does not expose GPIO22 in CircuitPython.
# I2C is used for PCA9685 PWM drivers (motion) and optional WAV Trigger Pro (audio).

I2C_SDA = board.GPIO8
I2C_SCL = board.GPIO9

# ============================================================================
# HARDWARE: MOTION (PCA9685 PWM Drivers, Servos, Blowers, Vapor Channels)
# ============================================================================
# Controlled via two PCA9685 boards on the shared I2C bus.

PCA9685_ADDR1 = 0x40  # Primary PCA9685 (servos)
PCA9685_ADDR2 = 0x41  # Secondary PCA9685 (vapor/blowers)

# Servo pulse limits (used by set_servo_channel)
SERVO_MIN_PULSE = 150
SERVO_MAX_PULSE = 600

# Door servo angles
DOOR_OPEN_ANGLE = 90
DOOR_CLOSED_ANGLE = 0

# ============================================================================
# HARDWARE: AUDIO (Tsunami Super WAV Trigger)
# ============================================================================
# Supports Qwiic/I2C command mode, UART command mode, and direct triggers.

ENABLE_AUDIO_I2C = False  # Enable Qwiic/I2C command mode for WAV Trigger Pro
ENABLE_AUDIO_UART = True  # Enable UART command mode for WAV Trigger
ENABLE_AUDIO_TRIGGERS = False  # Optional direct GPIO trigger outputs

# I2C mode (WAV Trigger Pro)
AUDIO_I2C_ADDR = 0x13  # Default 7-bit Qwiic address

# UART mode (WAV Trigger)
AUDIO_UART_TX = board.GPIO17  # UART1 TX (U1TXD) → Tsunami RXI
AUDIO_UART_RX = board.GPIO18  # UART1 RX (U1RXD) → Tsunami TXO
AUDIO_UART_BAUDRATE = 57600
AUDIO_UART_TIMEOUT = 0.1  # Timeout limit for UART read operations

# Direct trigger outputs (optional)
# AUDIO_TRIGGER_1_PIN = board.GPIO8
# AUDIO_TRIGGER_2_PIN = board.GPIO9
# AUDIO_TRIGGER_ACTIVE_LOW = True
# AUDIO_TRIGGER_PULSE_MS = 100

# Track assignment conventions
# AUDIO_TRIGGER_1_TRACK = 1
# AUDIO_TRIGGER_2_TRACK = 2
# AUDIO_TRACK_DAYTIME = 1
# AUDIO_TRACK_SUNSET = 2
# AUDIO_TRACK_NIGHTTIME = 3
# AUDIO_TRACK_DRAGON_EVENT = 4
# AUDIO_TRACK_PARTY_MUSIC = 5

# Output count and track ranges
AUDIO_OUTPUT_COUNT = 8
#AUDIO_TRACK_RANGES_BY_OUTPUT = (
#	(1, 99),
#	(100, 199),
#	(200, 299),
#	(300, 399),
#	(400, 499),
#	(500, 599),
#	(600, 699),
#	(700, 799),
#)

# If True, scene code must use track IDs within AUDIO_TRACK_RANGES_BY_OUTPUT.
# If False, any valid Tsunami track ID may be used.
ENFORCE_AUDIO_OUTPUT_TRACK_RANGES = False

# ============================================================================
# HARDWARE: ATMOSPHERE (Fogger Relay)
# ============================================================================
FOGGER_RELAY_PIN = board.GPIO39  # Right-side relay zone, adjacent to chimney relay block

# Fogger timing limits (used by atmosphere.py)
FOG_DURATION = 15  # seconds
FOG_INTERVAL = 300  # seconds (5 minutes) between fog cycles

# ============================================================================
# HARDWARE: CHIMNEY/SMOKE RELAYS
# ============================================================================
# Three independent relay controls for chimney smoke/fog effects.

CHIMNEY_RELAY_PIN1 = board.GPIO42  # Smial 1 (right-side pos 6, top of relay block)
CHIMNEY_RELAY_PIN2 = board.GPIO41  # Smial 2 (right-side pos 7)
CHIMNEY_RELAY_PIN3 = board.GPIO40  # Smial 3 (right-side pos 8)

# ============================================================================
# SYSTEM TIMING
# ============================================================================
LOOP_DELAY = 0.01  # Main loop yield time (seconds)