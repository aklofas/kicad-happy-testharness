# Findings: esp-rs/esp-rust-board / hardware_esp-rust-board

## FND-00000114: Good detection of ESP32-C3 dev board with USB-C, I2C sensors, LiPo charging, and switching regulator. I2C bus missing pull-ups flagged but may have internal pull-ups in ESP32-C3 module. Crystal value 32.768Hz should be 32.768kHz.

- **Status**: confirmed
- **Analyzer**: schematic
- **Source**: repos/esp-rust-board/hardware/esp-rust-board/esp-rust-board.kicad_sch
- **Created**: 2026-03-14

### Correct
- SY8088 switching regulator correctly identified with inductor L1, input +5V
- MCP73831 LiPo charger correctly placed in VBUS/+BATT power domains
- USB ESD protection (LESD5D5.0CT1G on D+/D-) correctly detected
- I2C bus detected with SHTC3 and ICM-42670-P sensors on SCL/SDA
- P-channel MOSFET Q1 (DMG3415U) power path switch correctly identified between VBUS/+BATT/+5V
- Reset circuit with pull-up and filter cap correctly detected on CHIP_PU net
- Power domains correctly map 6 ICs across +3V3, +5V, VBUS, +BATT rails
- UART TX/RX detected between ESP32-C3 (U3) and board connector (U4)

### Incorrect
- Crystal Y1 value shown as 32.768Hz - should be 32.768kHz (frequency field is null, value string not parsed)
  (signal_analysis.crystal_circuits)
- I2C bus shows has_pull_up=false but ESP32-C3 has internal pull-ups and board may use them intentionally
  (design_analysis.bus_analysis.i2c)
- Switching regulator output_rail is null - should be +3V3 (SY8088 feeds the 3.3V domain)
  (signal_analysis.power_regulators)
- Subcircuit neighbors are identical for all 6 ICs - neighbor detection appears broken, listing same caps for every IC regardless of actual connectivity
  (subcircuits)

### Missed
- WS2812B addressable RGB LED (D9) not identified as a smart LED requiring data signal - classified as generic LED
  (signal_analysis)
- LiPo charging circuit (MCP73831) charge current setting resistor not analyzed
  (signal_analysis)

### Suggestions
- Parse crystal frequency from value string (32.768kHz, 32.768Hz patterns)
- Fix subcircuit neighbor detection - currently returns same list for all ICs
- Detect WS2812B / addressable LED data chains
- Analyze LiPo charger program resistor for charge current calculation

---
