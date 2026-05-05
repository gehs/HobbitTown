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
# Move the PCA9685 SCL wire to GPIO47 and keep SDA on GPIO21.
I2C_SDA = board.GPIO21
I2C_SCL = board.GPIO47
PCA9685_ADDR1 = 0x40
PCA9685_ADDR2 = 0x41

# --- ATMOSPHERE (Fogger) ---
FOGGER_RELAY_PIN = board.GPIO18  # GPIO18 relay control

# --- AUDIO (Tsunami Super WAV Trigger) ---
ENABLE_AUDIO = True  # Set True after wiring the WAV Trigger and validating audio control mode.
ENABLE_AUDIO_I2C = False  # Enable Qwiic/I2C command mode for the WAV Trigger Pro.
ENABLE_AUDIO_UART = True  # Enable UART command mode for the WAV Trigger.
ENABLE_AUDIO_TRIGGERS = False  # Optional direct trigger mode (GPIO pulses). Not needed for normal UART control.
AUDIO_I2C_ADDR = 0x13  # Default 7-bit Qwiic address for WAV Trigger Pro.
AUDIO_UART_TX = board.GPIO17  # Use UART1 TX (U1TXD) for Tsunami RXI.
AUDIO_UART_RX = board.GPIO18  # Use UART1 RX (U1RXD) for Tsunami TXO.
AUDIO_UART_BAUDRATE = 57600
AUDIO_UART_TIMEOUT = 0.1

# Tsunami supports 8 audio outputs. The current firmware sends track numbers over UART,
# and channel routing is determined by how tracks are prepared on the Tsunami SD card.
# These settings document a track-numbering convention so scene logic stays consistent.
AUDIO_OUTPUT_COUNT = 8
AUDIO_TRACK_RANGES_BY_OUTPUT = (
	(1, 99),
	(100, 199),
	(200, 299),
	(300, 399),
	(400, 499),
	(500, 599),
	(600, 699),
	(700, 799),
)

# If True, scene code should only use track IDs inside AUDIO_TRACK_RANGES_BY_OUTPUT.
# If False, any valid Tsunami track ID may be used.
ENFORCE_AUDIO_OUTPUT_TRACK_RANGES = True

# NOTE: GPIO18 is used for the Tsunami UART RX line when ENABLE_AUDIO_UART=True.
# If the fogger relay also needs GPIO18, move that relay to a different pin first.
# Trigger mode is optional legacy control for two dedicated tracks.
# hardware/audio.py will pulse these pins only when ENABLE_AUDIO_TRIGGERS=True
# and the requested track matches AUDIO_TRIGGER_1_TRACK or AUDIO_TRIGGER_2_TRACK.
AUDIO_TRIGGER_1_PIN = board.GPIO8
AUDIO_TRIGGER_2_PIN = board.GPIO9
AUDIO_TRIGGER_ACTIVE_LOW = True
AUDIO_TRIGGER_PULSE_MS = 100
AUDIO_TRIGGER_1_TRACK = 1
AUDIO_TRIGGER_2_TRACK = 2
AUDIO_TRACK_DAYTIME = 1
AUDIO_TRACK_SUNSET = 2
AUDIO_TRACK_NIGHTTIME = 3
AUDIO_TRACK_DRAGON_EVENT = 4
AUDIO_TRACK_PARTY_MUSIC = 5

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