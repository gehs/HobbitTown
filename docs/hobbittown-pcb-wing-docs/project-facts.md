# Project facts to preserve

Use these as starting assumptions only when they are still supported by the current repo.

## Board

- Project: HobbitTown
- Controller: UICPAL ESP32-S3-DevKitC-1
- Variant: N16R8, 16 MB flash, 8 MB PSRAM
- Firmware: CircuitPython
- GPIO logic voltage: 3.3 V
- Required CircuitPython naming: `board.GPIO<n>`

## Current hardware architecture from inspected repo

- `config.py` centralizes GPIO, I2C addresses, hardware enable flags, and hardware-specific limits.
- Runtime hardware modules should import pin constants from `config.py`; they should not define pins directly.
- Three addressable LED strips are controlled independently.
- Motion uses a PCA9685 PWM driver on I2C.
- Audio control uses UART to a Tsunami Super WAV Trigger at 57600 baud.
- Tsunami mono firmware exposes 8 outputs.
- Chimney smoke/fog relays use GPIO outputs to relay modules, not direct relay coils.

## Pin assignments to verify from current repo

| Function | Expected current assignment | Notes |
|---|---|---|
| Sky NeoPixel data | GPIO4 | 129 pixels in `config.py` |
| Ground NeoPixel data | GPIO5 or GPIO6 | Known conflict between sources; verify before PCB |
| Stream NeoPixel data | GPIO5 or GPIO6 | Known conflict between sources; verify before PCB |
| I2C SDA | GPIO8 | PCA9685 bus |
| I2C SCL | GPIO9 | PCA9685 bus |
| Audio UART TX | GPIO17 | ESP32 TX to Tsunami RXI |
| Audio UART RX | GPIO18 | ESP32 RX from Tsunami TXO |
| Fogger relay control | GPIO39 | Backup noted in docs: GPIO47 if GPIO39 causes boot issues |
| Chimney relay 1 | GPIO42 | Relay module input |
| Chimney relay 2 | GPIO41 | Relay module input |
| Chimney relay 3 | GPIO40 | Relay module input |

## Known source conflict to check

Check whether `config.py`, `board_profile_hybrid.json`, and `docs/WIRING_Revised_Connections.md` agree on GPIO5/GPIO6 mapping.

Do not produce a PCB connector label, net name, silkscreen label, or schematic net for the ground/stream LED outputs until this is resolved.
