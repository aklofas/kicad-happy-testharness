# Findings: ESP32-S3-DevKit-LiPo / HARDWARE_ESP32-S3-DevKit-LiPo_Rev_B_ESP32-S3-DevKit-LiPo_Rev_B

## FND-00000183: OLIMEX ESP32-S3 dev board (58 components). Correct: all components extracted, SY8089 switching regulator, CH340X, BL4054B charger, fiducials. Incorrect: T1/T2 BC817-40 NPN BJTs classified as transformer (T prefix), pUEXT1 CONN_01X10 classified as other, SY8089 input_rail=GND. Missed: battery sensing voltage divider R6/R7, feedback divider R10/R11, auto-programming circuit.

- **Status**: confirmed
- **Analyzer**: schematic
- **Source**: HARDWARE_ESP32-S3-DevKit-LiPo_Rev_B_ESP32-S3-DevKit-LiPo_Rev_B.sch.json
- **Related**: KH-087
- **Created**: 2026-03-15

### Correct
- 58 components correctly extracted
- SY8089 correctly detected as switching regulator

### Incorrect
- T1/T2 BC817-40 NPN BJTs (lib_id Q_NPN_BEC) classified as transformer instead of transistor
  (bom.type)
- pUEXT1 (lib_id CONN_01X10) classified as other instead of connector
  (bom.type)
- SY8089 input_rail=GND incorrect
  (signal_analysis.power_regulators)

### Missed
- Voltage divider R6(470k)/R7(150k) for battery sensing not detected
  (signal_analysis.voltage_dividers)
- Feedback divider R10/R11 for SY8089 not detected
  (signal_analysis.voltage_dividers)

### Suggestions
- Fix T-prefix: check lib_id for Q_NPN/Q_PNP before defaulting to transformer
- Check lib_id for CONN keyword for connector classification

---
