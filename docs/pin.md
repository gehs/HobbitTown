# Shire-S3 (UICPAL ESP32-S3) Pin Mapping

| Board Label | Silicon GPIO | Function/Note |
| :--- | :--- | :--- |
| BOOT | GPIO0 | |
| GPIO0 | GPIO0 | |
| GPIO1 | GPIO1 | |
| GPIO10 | GPIO10 | |
| GPIO11 | GPIO11 | |
| GPIO12 | GPIO12 | |
| GPIO13 | GPIO13 | |
| GPIO14 | GPIO14 | |
| GPIO15 | GPIO15 | |
| GPIO16 | GPIO16 | |
| GPIO17 | GPIO17 | UART1 TX (U1TXD) — preferred for Tsunami RXI in serial mode |
| GPIO18 | GPIO18 | UART1 RX (U1RXD) — preferred for Tsunami TXO in serial mode |
| GPIO2 | GPIO2 | Ground lights data pin — `NEOPIXEL_GROUND_PIN` |
| GPIO21 | GPIO21 | I2C SDA (Qwiic WAV Trigger Pro SDA) |
| GPIO3 | GPIO3 | |
| GPIO35 | GPIO35 | |
| GPIO36 | GPIO36 | |
| GPIO37 | GPIO37 | |
| GPIO38 | GPIO38 | |
| GPIO39 | GPIO39 | |
| GPIO4 | GPIO4 | Sky lights data pin — `NEOPIXEL_PIN` |
| GPIO40 | GPIO40 | |
| GPIO41 | GPIO41 | |
| GPIO42 | GPIO42 | |
| GPIO43 | GPIO43 | UART0 TX / USB console (avoid for Tsunami UART if using USB REPL) |
| GPIO44 | GPIO44 | UART0 RX / USB console (avoid for Tsunami UART if using USB REPL) |
| GPIO45 | GPIO45 | |
| GPIO46 | GPIO46 | |
| GPIO47 | GPIO47 | I2C SCL (Qwiic WAV Trigger Pro SCL) |
| GPIO48 | GPIO48 | |
| GPIO5 | GPIO5 | |
| GPIO6 | GPIO6 | |
| GPIO7 | GPIO7 | |
| GPIO8 | GPIO8 | I2C SDA (PCA9685 SDA) |
| GPIO9 | GPIO9 | I2C SCL (PCA9685 SCL) |
| NEOPIXEL | GPIO48 | |
| RX | GPIO44 | UART0 RX / USB console |
| TX | GPIO43 | UART0 TX / USB console |
| UART | Unknown | |
| board_id | Unknown | |