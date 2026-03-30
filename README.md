# HobbitTown

Hobby ESP32 project for synchronized audio, direct LED strip lighting, atmosphere, and web-triggered events.

## PlatformIO Support

This repository is now configured for PlatformIO so you can build and upload directly to an ESP32 Dev Module (ESP-WROOM-32) without changing the current folder layout.

### Target

- Board: `esp32dev` (ESP32 Dev Module / WROOM)
- Framework: Arduino
- Source directory: `firmware/`

### Prerequisites

- VS Code
- PlatformIO IDE extension
- USB driver for your ESP32 board (if required by your adapter/chipset)

### Build and Upload (CLI)

From the project root:

```bash
pio run
pio run -t upload
pio device monitor
```

### Build and Upload (VS Code)

1. Open the folder in VS Code.
2. Use PlatformIO actions:
	- Build
	- Upload
	- Monitor

### Serial Port Notes

If PlatformIO does not auto-detect your serial port, set it in `platformio.ini`:

```ini
upload_port = COM3
monitor_port = COM3
```

Replace `COM3` with your actual ESP32 port.

### WiFi and Hostname Setup

The firmware now starts WiFi and mDNS in the web module.

1. Copy `firmware/NetworkSecrets.h.example` to `firmware/NetworkSecrets.h`.
2. Set your local network credentials and preferred hostname.
3. Build and upload to the ESP32.
4. Open `http://hobbitt2.local` from a device on the same LAN.

If mDNS is not resolved by your client device, use the IP printed in serial logs.

---

## Hardware Connections (ESP32 + LED strip + Audio)

### 1) Power
- Provide **5V** to the ESP32 (via USB or 5V/VIN pin) and to your LED strip power supply.
- Connect all grounds together (ESP32, LED strip power supply, and relay modules).

### 2) LED Strip (direct control)
- Connect your LED strip data input to the GPIO pin defined by `LED_PIN` in `firmware/Lighting.h` (defaults to **GPIO 2**).
- Power the LED strip from a 5V supply capable of your strip’s current draw.
- Adjust `NUM_LEDS` in `firmware/Lighting.h` to match your strip length.

### 2.5) HobbitTown I2C + PCA9685 (Servos/Misters/Speakers)
- Connect the PCA9685 modules to the ESP32 I2C pins:
  - **SDA** → GPIO 21
  - **SCL** → GPIO 22
- Each PCA9685 is preconfigured at addresses **0x40** (pwm1) and **0x41** (pwm2).
- Servo channels (doors) are on PCA9685 #1 (0-2). Misters are on PCA9685 #2 (0-3).

### 3) Fog/Atmosphere Relay
- Connect the relay module input to **GPIO 18** (wired as active LOW in `firmware/Atmosphere.h`).
- Power the relay module from **5V**, and share ground with the ESP32.

---

## Configuring the Firmware

### LED Strip Configuration
- Update `firmware/Lighting.h` to set `LED_PIN` and `NUM_LEDS` to match your LED strip wiring and length.

### Network Credentials
- Update `firmware/NetworkSecrets.h` with your SSID and password.

### Customizing Behavior
- The main controller logic lives in `code.py` for CircuitPython.
- `hardware/atmosphere.py` controls fog timing and relay pin.
- `hardware/soundscape.py` defines audio sequences (future: replace audio stubs with actual playback)

---

## Connecting to the Web Interface

1. After uploading, open the serial monitor (`pio device monitor`) to see the IP address.
2. Visit `http://<DEVICE_IP>/` or `http://<HOSTNAME>.local` to access the controller UI.

### Hobbit Town Test UI

To manually exercise the servos, misters, speaker matrix, blowers, and audio players, open:

- `http://<DEVICE_IP>/hobbit`

This page provides quick controls so you can verify wiring and behavior without having to recompile.

If you want to change the hostname, edit it in `firmware/NetworkSecrets.h` and re-upload.