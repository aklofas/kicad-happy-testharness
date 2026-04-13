# Findings: hackclub/OnBoard / projects_CACKLE - Card Adaptable Controller Kinetic Link Electronics_src_ESP32-S3 Hub

## FND-00000110: ESP32-S3 hub board with 74HC595 shift register, THVD1420 RS-485 transceiver, 40MHz crystal, SPI/I2C buses, and extensive connector system. Good crystal and decoupling analysis but bus protocols and RS-485 not identified.

- **Status**: confirmed
- **Analyzer**: schematic
- **Source**: repos/OnBoard/projects/CACKLE - Card Adaptable Controller Kinetic Link Electronics/src/ESP32-S3 Hub/ESP32-S3 Hub.kicad_sch
- **Created**: 2026-03-14

### Correct
- Correctly identified 40MHz crystal with 12pF load caps and calculated effective CL of 9pF
- Correctly identified VDD rail decoupling with 10 caps totaling 47.5uF including bulk and bypass
- Correctly identified RC filter on crystal lines (R6=22ohm, C11=12pF)
- Correctly detected bus signal prefixes: CS (8 chip selects), SPI (MISO/MOSI/SCK), I2C (SDA/SCL)
- Correctly identified ferrite bead FB1 at 120ohm@100MHz
- Correctly identified 7 test points

### Incorrect
- IC function not identified for any of the 3 main ICs (ESP32-S3, 74HC595, THVD1420DRLR) - all show func=?
  (ic_pin_analysis)
- IC ref fields are ? for all 22 components in ic_pin_analysis
  (ic_pin_analysis)
- RC filter R7=10k/C13=1uF with fc=15.9Hz detected but this is likely a power-on reset or enable delay circuit, not a signal filter
  (signal_analysis.rc_filters)

### Missed
- THVD1420DRLR is a half-duplex RS-485/RS-422 transceiver with ESD protection - not identified as bus protocol or analyzed
  (signal_analysis)
- 74HC595 is an 8-bit shift register used for chip select expansion via SPI - purpose not analyzed
  (ic_pin_analysis)
- SPI bus topology with 8 chip selects driving multiple sensor boards via FPC connectors not identified as a bus protocol
  (signal_analysis)
- I2C bus (SDA/SCL) not identified as a bus protocol despite detected bus signals
  (signal_analysis)
- No power regulator detected - board may be powered externally via connectors but power path not analyzed
  (signal_analysis.power_regulators)
- ESP32-S3 WiFi/BT capability not noted
  (ic_pin_analysis)
- FPC connectors (Panasonic Y3b 7-pin) connecting to sensor boards not analyzed for interface type
  (ic_pin_analysis)

### Suggestions
- Detect RS-485/RS-422 transceiver ICs (THVD14xx, MAX485, SN65HVD, etc.) as bus protocols
- Identify shift registers (74HC595, 74HC165) and their role in expanding GPIO/chip selects
- SPI bus detection should combine MOSI/MISO/SCK/CS signals into a coherent bus protocol entry
- I2C bus detection should identify SDA/SCL signal pairs
- IC function lookup for common part families (74HCxxx, ESP32-Sx, THVDxxxx)

---
