# Findings: esphome-pressure / pcb_esphome-pressure

## FND-00000116: Pressure sensor board with ESP32-C3, BD9G101G buck converter, and XGZP6899D I2C pressure sensor. Good I2C and regulator detection but 7 false positive RF matching networks from the power supply LC filter components.

- **Status**: confirmed
- **Analyzer**: schematic
- **Source**: repos/esphome-pressure/pcb/esphome-pressure.kicad_sch
- **Created**: 2026-03-14

### Correct
- I2C bus correctly detected with XGZP6899D pressure sensor (U2) and ESP32-C3 (U4) with 5.1k pull-ups
- BD9G101G switching regulator correctly identified with inductor L1 and bootstrap cap
- Feedback voltage divider R12/R2 (3k9/680) correctly detected with estimated Vout=4.04V
- AMS1117-3.3 LDO correctly identified with +5V input and +3V3 output
- UART TX/RX detected on ESP32-C3
- SS210 diodes correctly classified as diodes (bridge rectifier for 24VAC input)

### Incorrect
- 7 false positive RF matching networks detected - these are power supply LC filter components (L1 6.8uH, C7 10uF, C4 0.1uF) misidentified as antenna matching circuits
  (signal_analysis.rf_matching)
- BD9G101G input rail shown as __unnamed_11 - should trace through diode bridge to 24VAC input
  (signal_analysis.power_regulators)
- AMS1117-3.3 missing input cap warning for +5V rail is incorrect - C7/C9 (10uF) are on the +5V rail from BD9G101G output
  (signal_analysis.design_observations)
- BD9G101G estimated Vout=4.04V using 0.6V Vref heuristic - BD9G101G actual Vref is 0.75V giving Vout=5.04V which matches the +5V rail
  (signal_analysis.power_regulators)

### Missed
- Full-wave bridge rectifier (7x SS210 diodes) for 24VAC input not detected as a rectifier circuit
  (signal_analysis)
- Fuse F1 (140mA/340mA) on input not connected to protection_devices analysis
  (signal_analysis.protection_devices)
- USB-C connector (J4) present but no USB data analysis or ESD protection check
  (signal_analysis.design_observations)

### Suggestions
- RF matching detector should require plausible RF component values (not 10uF caps or 6.8uH inductors)
- Add bridge rectifier detection (multiple diodes forming full/half bridge)
- Look up actual Vref for known regulator parts instead of using 0.6V heuristic
- Track fuses in protection_devices

---
