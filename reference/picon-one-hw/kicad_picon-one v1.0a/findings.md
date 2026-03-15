# Findings: picon-one-hw / kicad_picon-one v1.0a

## FND-00000134: Multi-function Pico-based board with DS3231M RTC, SC16IS752 I2C-to-UART, TM1640 LED driver, and 14.7456MHz crystal. Excessive I2C false positives (10 buses detected for what should be 2-3). Crystal load cap mismatch (22pF vs 33pF) flagged correctly. Many unnamed nets suggest legacy format connectivity issues.

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: repos/picon-one-hw/kicad/picon-one v1.0a.sch
- **Created**: 2026-03-14

### Correct
- DS3231M RTC correctly identified in power domains
- SC16IS752 I2C-to-dual-UART correctly detected with I2C and UART connections
- Crystal Y1 14.7456MHz with asymmetric load caps (22pF/33pF) correctly detected, CL_eff=16.2pF calculated
- SPI bus detected with MISO/MOSI/SCK signals
- Multiple UART channels (TXW/RXW, TXG/RXG, RXP, RXR, TXR) correctly detected
- Decoupling coverage warning: +5V has only 0.1uF bypass, no bulk - legitimate concern
- Battery connection (BT1) detected

### Incorrect
- 10 I2C buses detected but most are false positives from unnamed nets with SCL/SDA pin names - should be 2-3 actual I2C buses
  (design_analysis.bus_analysis.i2c)
- Many power rails use unnamed nets (__unnamed_56, __unnamed_90, __unnamed_114) - these should be resolved to actual rail names
  (design_analysis.power_domains)
- MCU1 (likely Raspberry Pi Pico module) not detected in power domains or as an IC
  (design_analysis.power_domains)
- Crystal frequency field is null despite 14.7456MHz in value string
  (signal_analysis.crystal_circuits)
- SPI bus pin mapping has MISO mapped to CS net - incorrect signal identification
  (design_analysis.bus_analysis.spi)

### Missed
- Raspberry Pi Pico module (MCU1) not detected as a component or processor
  (statistics.component_types)
- TM1640 LED driver function not identified - drives 7-segment display grid/segment lines
  (signal_analysis)
- DIP switch (DIP1) configuration not analyzed
  (signal_analysis)
- No power regulator detected - board likely powered from Pico USB/VSYS
  (signal_analysis.power_regulators)
- 12V input connectors (12V1, 12V2) not traced through power path
  (signal_analysis)

### Suggestions
- Filter I2C false positives - require named nets or multi-device buses, not single-device unnamed nets
- Parse crystal frequency from value string
- Detect Raspberry Pi Pico module footprint as processor module
- Fix SPI pin mapping - distinguish MISO/MOSI/SCK/CS properly

---
