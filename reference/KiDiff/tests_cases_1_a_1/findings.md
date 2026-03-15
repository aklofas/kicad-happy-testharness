# Findings: KiDiff / tests_cases_1_a_1

## FND-00000191: ESP32 8-channel MOSFET output board (77 components). Correct: all components, nets, AZ1117-3.3 LDO, CP2104 USB-UART, auto-reset circuit, MOSFET switches, BOM. Incorrect: flyback diodes D3-D10 not detected (drain-to-VCC topology missed), regulator input cap C4 falsely flagged as missing. Missed: D1/D2 power OR-ing, R17-R24 gate pulldowns.

- **Status**: confirmed
- **Analyzer**: schematic
- **Source**: tests_cases_1_a_1.kicad_sch.json
- **Created**: 2026-03-15

### Correct
- All 77 components with accurate pin-to-net assignment
- AZ1117-3.3 correctly detected as LDO
- Q1/Q2 auto-reset circuit correctly traced

### Incorrect
- has_flyback_diode=false for Q3-Q10 despite D3-D10 Schottky diodes from drain to VCC
  (signal_analysis.transistor_circuits)
- Regulator input cap falsely flagged as missing (C4 1uF is on the input net)
  (signal_analysis.design_observations)

### Missed
- D1/D2 Schottky power OR-ing not detected
  (signal_analysis.protection_devices)

### Suggestions
- Check flyback diodes from drain to supply rail not just drain-to-source
- Fix regulator_caps to detect existing caps on input net

---
