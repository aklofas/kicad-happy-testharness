# Findings: SparkFun_IoT_Node_LoRaWAN / Hardware_SparkFun_IoT_Node_LoRaWAN

## FND-00000205: RP2350A-based IoT node with XBee LR LoRaWAN module, dual USB-C ports, PSRAM, flash, microSD, Qwiic I2C, and LiPo battery support. Good component classification and signal detection with a few regulators and bus interfaces missed.

- **Status**: confirmed
- **Analyzer**: schematic
- **Source**: Hardware_SparkFun_IoT_Node_LoRaWAN.kicad_sch.json
- **Created**: 2026-03-15

### Correct
- RT9080-3.3 (U7) correctly identified as fixed 3.3V LDO regulator via value suffix parsing
- Y1 12MHz crystal with C5=15pF and C2=15pF load caps correctly detected, effective load 10.5pF
- D1 and D3 DT1042-04SO correctly identified as USB ESD protection on USB_D+/USB_D- and XBLR_USB_D+/XBLR_USB_D- lines
- Q1 DMG2305UX correctly identified as P-channel MOSFET power switch controlled by gate on __unnamed_34
- WS2812B_CBI (D4) addressable LED chain correctly detected on LED_IN net
- D2 BAT20J correctly classified as diode (Schottky for reverse polarity protection)
- 9 decoupling rails analyzed including 3.3V, 1.1V, 3.3V_XBLR, VBATT, VDDA
- U1 RP2350A, U2 W25Q128JVPIM, U3 APS6404L-3SQR-ZR, U4 XBLR (XBee LR), U5 CH340C all correctly classified as ICs
- Design observations correctly flag missing I2C pull-ups on SDA/SCL and missing input cap on U7

### Incorrect
(none)

### Missed
- MCP73831 (U8) single-cell LiPo battery charger from VUSB not detected as battery management component
  (signal_analysis.bms_systems)
- MAX17048 (U9) I2C fuel gauge for battery monitoring not detected
  (signal_analysis.bms_systems)
- I2C bus on SDA/SCL connecting U1 (RP2350A) and U9 (MAX17048) with pull-up jumper JP7 not detected as bus interface
  (signal_analysis.bus_interfaces)
- QSPI flash interface (U2 W25Q128JVPIM) and QSPI PSRAM interface (U3 APS6404L-3SQR-ZR) not detected as memory buses
  (signal_analysis.memory_interfaces)
- Dual USB-C interfaces with CH340C (U5) USB-UART bridge for both RP2350 and XBLR module not detected as USB buses
  (signal_analysis.bus_interfaces)
- XBee LR LoRaWAN module (U4) not detected as RF/radio component despite being a LoRaWAN transceiver
  (signal_analysis.rf_chains)

### Suggestions
- Add XBee/XBLR modules to RF chain detection
- Detect CH340C/CH342 as USB-UART bridges and flag USB bus interfaces
- Add MCP73831 to battery charger IC recognition for bms_systems
- Recognize DPDT switches in signal routing paths

---
