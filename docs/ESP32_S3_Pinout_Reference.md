# ESP32-S3 Dev Board Pinout Reference (UICPAL ESP32-S3-N16R8)

This reference document compiles the pin functions for the ESP32-S3 development board based on the provided pinout diagrams.

## Left Side (Pins 1-21)
| Pin # | Label / GPIO | HobbitTown Use Case | Primary Function | Alternate / Specialized Functions |
| :--- | :--- | :--- | :--- | :--- |
| 1 | GND | Ground | Ground | |
| 2 | 3V3 | Power | Power Out (3.3V) | |
| 3 | RST | Reset | Reset / Enable | |
| 4 | GPIO4 | Sky Lighting (NeoPixel) | GPIO / RTC | ADC1_3, TOUCH4 |
| 5 | GPIO5 | Stream Bead Lighting (NeoPixel) | GPIO / RTC | ADC1_4, TOUCH5 |
| 6 | GPIO6 | Unassigned | GPIO / RTC | ADC1_5, TOUCH6 |
| 7 | GPIO7 | Unassigned | GPIO / RTC | ADC1_6, TOUCH7 |
| 8 | GPIO15 | Unassigned | GPIO / RTC | ADC2_4, U0RTS, XTAL_32K_P |
| 9 | GPIO16 | Unassigned | GPIO / RTC | ADC2_5, U0CTS, XTAL_32K_N |
| 10 | GPIO17 | Audio UART TX (Tsunami) | GPIO / RTC | ADC2_6, U1TXD |
| 11 | GPIO18 | Audio UART RX (Tsunami) | GPIO / RTC | ADC2_7, U1RXD, CLK_OUT3 |
| 12 | GPIO8 | I2C SDA (Motion/Audio) | GPIO / RTC | ADC1_7, TOUCH8 |
| 13 | GPIO19 | Unassigned (Previously failed) | GPIO / RTC | ADC2_8, USB_D-, CLK_OUT2, U1RTS |
| 14 | GPIO20 | Unassigned | GPIO / RTC | ADC2_9, USB_D+, U1CTS, CLK_OUT1 |
| 15 | GPIO3 | Unassigned | GPIO | ADC1_2, TOUCH3, JTAG |
| 16 | GPIO46 | Unassigned | GPIO | LOG |
| 17 | GPIO9 | I2C SCL (Motion/Audio) | GPIO / RTC | ADC1_8, TOUCH9, FSPIHD, SUBSPIHD |
| 18 | GPIO10 | Unassigned | GPIO / RTC | ADC1_9, TOUCH10, FSPICS0, SUBSPICSO |
| 19 | GPIO11 | Unassigned | GPIO / RTC | ADC2_0, TOUCH11, FSPID, SUBSPID |
| 20 | GPIO12 | Unassigned | GPIO / RTC | ADC2_1, TOUCH12, FSPICLK, SUBSPICLK |
| 21 | 3V3 | Power | Power Out (3.3V) | |

## Right Side (Pins 1-21)
| Pin # | Label / GPIO | HobbitTown Use Case | Primary Function | Alternate / Specialized Functions |
| :--- | :--- | :--- | :--- | :--- |
| 1 | GND | Ground | Ground | |
| 2 | GPIO1 | Unassigned | GPIO / RTC | ADC1_0, TOUCH1 |
| 3 | GPIO2 | Ground Lighting (NeoPixel) | GPIO / RTC | ADC1_1, TOUCH2 |
| 4 | GPIO43 | USB Serial TX | GPIO | U0TXD, SERIAL_TX, CLK_OUT1 |
| 5 | GPIO44 | USB Serial RX | GPIO | U0RXD, SERIAL_RX, CLK_OUT2 |
| 6 | GPIO42 | Unassigned | GPIO | MTMS |
| 7 | GPIO41 | Chimney Relay 3 | GPIO | MTDI, CLK_OUT1 |
| 8 | GPIO40 | Chimney Relay 2 | GPIO | MTDO, CLK_OUT2 |
| 9 | GPIO39 | Unassigned | GPIO | MTCK, SUBSPICSI, CLK_OUT3 |
| 10 | GPIO38 | Unassigned | GPIO | FSPIWP, SUBSPIWP |
| 11 | GPIO37 | Unassigned | GPIO | SPIDQS, FSPIQ, SUBSPIQ |
| 12 | GPIO36 | Unassigned | GPIO | SPIIO7, FSPICLK, SUBSPICLK |
| 13 | GPIO35 | Unassigned (Reserved) | GPIO | SPIIO6, FSPID, SUBSPID |
| 14 | GPIO0 | Boot Mode | GPIO / BOOT | Boot Mode Selection |
| 15 | GPIO45 | Unassigned | GPIO | VSPI |
| 16 | GPIO48 | RGB LED (onboard) | GPIO | SPICLK_N, RGB_LED (Addressable) |
| 17 | GPIO47 | Unassigned | GPIO | SPICLK_P |
| 18 | GPIO21 | Chimney Relay 1 | GPIO / RTC | |
| 19 | GPIO14 | Unassigned | GPIO / RTC | ADC2_3, TOUCH14, FSPIWP, FSPIDQS, SUBSPIWP |
| 20 | GPIO13 | Unassigned | GPIO / RTC | ADC2_2, TOUCH13, FSPIQ, FSPIIO7, SUBSPIQ |
| 21 | 5V0 | Power | Power In (USB) | 5V Bus Voltage |

## Key Features & Abbreviations
- **ADC1_X / ADC2_X**: Analog to Digital Converter channels.
- **TOUCH_X**: Capacitive Touch Sensor channels.
- **U0 / U1**: UART controllers (e.g., U0TXD is UART0 Transmit).
- **RTC**: Low-power pins that remain active during deep sleep.
- **FSPI / SUBSPI**: Flash/Sub-SPI interface pins.
- **USB_D+/-**: Native USB data pins (GPIO 19/20).
- **RGB_LED**: GPIO 48 is typically connected to the onboard WS2812/NeoPixel LED.
