import adafruit_pca9685  # type: ignore
import busio  # type: ignore
import config

i2c = None
pwm1 = None
pwm2 = None
hardware_ready = False


def setup_hardware():
    global i2c, pwm1, pwm2, hardware_ready

    if not getattr(config, "ENABLE_MOTION", True):
        i2c = None
        pwm1 = None
        pwm2 = None
        hardware_ready = False
        print("Hobbit Town Hardware: disabled (enable in config.py when PCA9685 hardware is connected)")
        return

    try:
        i2c = busio.I2C(config.I2C_SCL, config.I2C_SDA)
        pwm1 = adafruit_pca9685.PCA9685(i2c, address=config.PCA9685_ADDR1)
        pwm2 = adafruit_pca9685.PCA9685(i2c, address=config.PCA9685_ADDR2)
        pwm1.frequency = 60
        pwm2.frequency = 60
        hardware_ready = True
        reset_all()
        print("Hobbit Town Hardware: initialized")
    except Exception as exc:
        i2c = None
        pwm1 = None
        pwm2 = None
        hardware_ready = False
        print(f"Hobbit Town Hardware: dry-load mode ({exc})")


def servo_pulse_from_angle(deg):
    return int((deg / 180.0) * (config.SERVO_MAX_PULSE - config.SERVO_MIN_PULSE) + config.SERVO_MIN_PULSE)


def set_door(id, angle):
    if not hardware_ready or pwm1 is None:
        return
    if 1 <= id <= 3:
        pulse = servo_pulse_from_angle(angle)
        pwm1.channels[id - 1].duty_cycle = int(pulse / 4095.0 * 65535)


def set_mister(id, value):
    if not hardware_ready or pwm2 is None:
        return
    if 1 <= id <= 4:
        duty = int(value / 255.0 * 65535)
        pwm2.channels[id - 1].duty_cycle = duty


def set_speaker(channel, value):
    if not hardware_ready or pwm1 is None:
        return
    if 8 <= channel <= 11:
        pwm1.channels[channel].duty_cycle = 65535 if value > 0 else 0
    elif channel in (12, 13):
        duty = int(value / 255.0 * 65535)
        pwm1.channels[channel].duty_cycle = duty


def set_blower(id, value):
    if not hardware_ready or pwm2 is None:
        return
    if 1 <= id <= 3:
        duty = int(value / 255.0 * 65535)
        pwm2.channels[3 + id].duty_cycle = duty


def reset_all():
    if not hardware_ready or pwm1 is None or pwm2 is None:
        return
    for i in range(16):
        pwm1.channels[i].duty_cycle = 0
        pwm2.channels[i].duty_cycle = 0
    # Set servos to 90 degrees
    for i in range(1, 4):
        set_door(i, 90)
