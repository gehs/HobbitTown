# HobbitTown

Hobby ESP32 project for synchronized audio, lighting (WLED), atmosphere, and web-triggered events.

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