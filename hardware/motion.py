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
        pwm1_ready = False
        pwm2_ready = False

        try:
            pwm1 = adafruit_pca9685.PCA9685(i2c, address=config.PCA9685_ADDR1)
            pwm1.frequency = 60
            pwm1_ready = True
        except Exception as exc:
            pwm1 = None
            print(f"Hobbit Town Hardware: PCA9685 #1 missing at 0x{config.PCA9685_ADDR1:02X} ({exc})")

        try:
            pwm2 = adafruit_pca9685.PCA9685(i2c, address=config.PCA9685_ADDR2)
            pwm2.frequency = 60
            pwm2_ready = True
        except Exception as exc:
            pwm2 = None
            print(f"Hobbit Town Hardware: PCA9685 #2 missing at 0x{config.PCA9685_ADDR2:02X} ({exc})")

        hardware_ready = pwm1_ready or pwm2_ready
        if hardware_ready:
            reset_all()
            if pwm1_ready and pwm2_ready:
                print("Hobbit Town Hardware: initialized with both PCA9685 boards")
            elif pwm1_ready:
                print("Hobbit Town Hardware: initialized with PCA9685 #1 only")
            else:
                print("Hobbit Town Hardware: initialized with PCA9685 #2 only")
        else:
            print("Hobbit Town Hardware: no PCA9685 detected")
    except Exception as exc:
        i2c = None
        pwm1 = None
        pwm2 = None
        hardware_ready = False
        print(f"Hobbit Town Hardware: dry-load mode ({exc})")


def servo_pulse_from_angle(deg):
    return int((deg / 180.0) * (config.SERVO_MAX_PULSE - config.SERVO_MIN_PULSE) + config.SERVO_MIN_PULSE)


def set_servo_channel(channel, angle):
    """Set a PCA9685 PWM channel to the given servo angle."""
    if not hardware_ready or pwm1 is None:
        return
    if 0 <= channel <= 15:
        pulse = servo_pulse_from_angle(angle)
        pwm1.channels[channel].duty_cycle = int(pulse / 4095.0 * 65535)


def set_door(id, angle):
    if not hardware_ready or pwm1 is None:
        return
    if 1 <= id <= 3:
        set_servo_channel(id - 1, angle)


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
    if not hardware_ready:
        return

    if pwm1 is not None:
        for i in range(16):
            pwm1.channels[i].duty_cycle = 0
        # Set door servos to 90 degrees when PCA9685 #1 is present
        for i in range(1, 4):
            set_door(i, 90)

    if pwm2 is not None:
        for i in range(16):
            pwm2.channels[i].duty_cycle = 0


def get_bus_diagnostics():
    """Return read-only I2C and PCA9685 health details for UI diagnostics."""
    expected_addresses = [config.PCA9685_ADDR1, config.PCA9685_ADDR2]
    report = {
        "hardware_ready": hardware_ready,
        "i2c_present": i2c is not None,
        "sda": str(config.I2C_SDA),
        "scl": str(config.I2C_SCL),
        "expected": ["0x%02X" % addr for addr in expected_addresses],
        "found": [],
        "pca9685": {},
        "error": "",
    }

    if i2c is None:
        report["error"] = "I2C bus not initialized"
        for addr in expected_addresses:
            report["pca9685"]["0x%02X" % addr] = False
        return report

    try:
        if i2c.try_lock():
            try:
                scanned = i2c.scan()
                report["found"] = ["0x%02X" % addr for addr in scanned]
                for addr in expected_addresses:
                    report["pca9685"]["0x%02X" % addr] = addr in scanned
            finally:
                i2c.unlock()
        else:
            report["error"] = "I2C bus busy (could not lock)"
            for addr in expected_addresses:
                report["pca9685"]["0x%02X" % addr] = False
    except Exception as exc:
        report["error"] = str(exc)
        for addr in expected_addresses:
            report["pca9685"]["0x%02X" % addr] = False

    return report
