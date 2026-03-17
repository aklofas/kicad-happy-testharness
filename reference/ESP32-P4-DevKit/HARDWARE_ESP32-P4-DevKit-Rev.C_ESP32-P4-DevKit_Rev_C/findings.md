# Findings: ESP32-P4-DevKit / HARDWARE_ESP32-P4-DevKit-Rev.C_ESP32-P4-DevKit_Rev_C

## FND-00000113: Dev board with two TPS62A02 regulators and Ethernet PHY correctly identified; differential pairs properly detected with ESD protection; crystal circuit undetected; RMII signals misclassified as UART; voltage divider R16/R14 is SD card detect not a divider

- **Status**: confirmed
- **Analyzer**: schematic
- **Source**: repos/ESP32-P4-DevKit/HARDWARE/ESP32-P4-DevKit-Rev.C/ESP32-P4-DevKit_Rev_C.kicad_sch
- **Created**: 2026-03-14

### Correct
- TPS62A02 switching regulator for 3.3V correctly identified with feedback divider R39/R40 (30.1k/6.49k), ratio 0.177, estimated Vout 3.38V
- Second TPS62A02 for separate power domain correctly detected
- RC filter on ESP_EN pin (R36 10k / C39 100nF, fc=159Hz) correctly identified as reset delay
- LC filter (L4 1uH / C62 47uF, resonant 23.2kHz) correctly detected at DCDC output
- Feedback network R39/R40 correctly duplicated in feedback_networks section
- Decoupling analysis shows good coverage: +3.3V has 77.8uF total across 18 caps with mixed values for broadband impedance
- Power rails correctly identified including +1V8, +2.5V, +3.3V, +5V, +5VP, VDD_SD
- Ethernet PHY IP101GRR (U2) correctly detected in ethernet_interfaces
- Ethernet differential pairs TD+/TD- and RD+/RD- correctly identified with ESD protection noted
- PoE power differential pair PW+/PW- detected between LAN_CON1 and POE_PWR1
- ESDS314DBVR ESD protection on Ethernet lines correctly identified
- I2C bus correctly identified with pull-ups (R22/R23 2.2k to +3.3V) on GPIO7/8
- Second I2C bus on GPIO32/33 correctly flagged as missing pull-ups
- W25Q128 SPI flash (U3, 16MB) detected as subcircuit
- Reverse polarity protection D1 (1N5822) correctly identified between +5VP and +5V

### Incorrect
- Voltage divider R16/R14 (22R/4.7k) classified as signal voltage divider with ratio 0.995 but this is actually just a series resistor (R16=22R) on SD card detect line with pull-down R14 - the 22R is too small to be a divider top resistor, it is a current limiting resistor
  (signal_analysis.voltage_dividers)
- Crystal oscillator components (R12 10M feedback resistor with C1/C2 22pF load caps) misidentified as RC low-pass filter at 723Hz instead of crystal circuit
  (signal_analysis.rc_filters)
- RMII Ethernet signals (GPIO35/RMII_TXD1, RMII_RXDV, RMII_RXD0, etc.) misclassified as UART instead of Ethernet/RMII bus
  (design_analysis.bus_analysis.uart)

### Missed
- No crystal circuit detected for ESP32-P4 40MHz crystal with 22pF load caps and 10M feedback resistor
  (signal_analysis.crystal_circuits)
- MIPI-DSI connector (MIPI-DSI1) and MIPI-CSI connector (MIPI-CSI1) present but differential pairs not detected
  (design_analysis.differential_pairs)
- Buttons BOOT1 and RST1 classified as type other instead of switch
  (statistics.component_types)
- POE_PWR1 connector present suggesting Power-over-Ethernet capability but no PoE subcircuit detected
  (subcircuits)
- SD card interface (MICRO_SD1) not detected as memory interface with card detect signal
  (signal_analysis.memory_interfaces)

### Suggestions
- Crystal circuit detector should recognize the pattern: high-value resistor (1M-10M) bridging two nets that also have small caps (10-33pF) to ground
- Voltage divider detector should reject dividers where ratio > 0.95 as these are likely series resistor + pull-down configurations, not intentional voltage dividers
- YTS-A016-X button footprints should be classified as switch type, not other
- SD card interfaces should be detected when MICRO_SD footprint is present with data/clock/detect lines

---
