# Findings: kicad / cb-flex_cb-flex

## FND-00000195: panStamp flexible battery board with panStamp NRG2 module, SIM800L GSM/GPRS, level shifter, sensor interface, and PSU across 3 sheets. Good detection of voltage dividers, RC filter, power regulators, and RF matching, but regulator output pin mapping has issues and I2C bus detection flags missing pullups.

- **Status**: confirmed
- **Analyzer**: schematic
- **Source**: cb-flex_cb-flex.sch.json
- **Created**: 2026-03-15

### Correct
- Voltage divider R14/R15 (976k/309k) correctly detected with ratio 0.24 on VDD rail, likely for battery voltage monitoring
- Voltage divider R16/R17 (100k/43k) on VAA rail correctly detected with ratio 0.30
- RC filter R8/C24 (10k/100n, fc=159Hz) correctly identified as low-pass on TRIG/EN_SENSOR path
- MIC29302 (U8) correctly identified as LDO regulator with feedback net
- AP7365-30 (U9) correctly identified as LDO with estimated_vout=3.0V from fixed_suffix
- ANT2 RF matching L_match with L2/C9 detected; L2 value '0' and C9 'N.P.' correctly suggest unpopulated matching network
- Q2 NMOS and Q1 NMOS correctly identified as switching transistors on sensor enable paths
- LC filter L1/C1 (10u/10u) correctly detected at resonant 15.9kHz on power rail
- Decoupling on VCC rail correctly includes C6 (100n), C5 (1u), C4 (100n) totaling 1.2uF across 3 caps
- Thermistor TH1 correctly classified as component type 'thermistor'

### Incorrect
- U9 (AP7365-30) output_rail is 'GND' which is incorrect; output pin should connect to VCC rail, not ground
  (signal_analysis.power_regulators)
- U8 (MIC29302) missing caps observation claims both input and output caps missing, but C10/C14/C16/C18 are likely on those rails in the PSU sub-sheet
  (signal_analysis.design_observations)

### Missed
(none)

### Suggestions
- Fix LDO output rail mapping - AP7365 output pin should not map to GND
- Cross-reference regulator cap detection with decoupling analysis to avoid false 'missing caps' observations

---
