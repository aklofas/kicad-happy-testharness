# Findings: Twisted-Fields/acorn-robot-electronics / previous_revisions_V1_acorn_motherboard

## FND-00000273: V1 Acorn robot motherboard (KiCad 5, 208 components). AO3401A P-ch MOSFET misclassified as N-channel. Two isolated DC/DC converters and ACS725 current sensor missed.

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: previous_revisions_V1_acorn_motherboard.sch.json
- **Created**: 2026-03-16

### Correct
- 7 voltage dividers correctly detected: 3 precision range-select sensing dividers and 4 RS-485 termination networks
- 8 CDSOT23-SM712 TVS protection devices on RS-485 lines correctly detected
- I2C bus with 4 devices (ADS1115 x2, MCP23017, HDC1080) correctly detected
- Q1 2N7002 with flyback diode D8 correctly detected
- LC filter L2+C99 on 48V input correctly identified

### Incorrect
- Q12 AO3401A reported as is_pchannel=false — AO3401A is a P-channel MOSFET
  (signal_analysis.transistor_circuits)

### Missed
- PDQ30-Q48-S5-D (U4) isolated DC/DC converter (48V to 5V) not detected as power regulator
  (signal_analysis.power_regulators)
- SPBW06F-12 (PS1) isolated converter (48V to 15V) classified as 'connector' preventing regulator detection
  (signal_analysis.power_regulators)
- ACS725LCTR-10AU (U14) Hall-effect current sensor on +48V path not detected in current_sense
  (signal_analysis.current_sense)

### Suggestions
- Add AO3401A to known P-channel MOSFET list or improve P-ch detection heuristics
- Parse DC/DC converter part values for voltage info (Q48-S5 = 48V in, 5V out)
- Add ACS7xx family to current_sense detection patterns

---
