# Findings: LibreSolar/bms-c1 / kicad_bms-c1

## FND-00000211: Libre Solar BMS C1, 16-cell battery management system with BQ76952. Overall excellent analysis: BMS system, current sense, transistor circuits, and cell input RC filters all correctly identified. Switching regulator Vout estimate is incorrect due to wrong Vref assumption.

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: kicad_bms-c1.kicad_sch.json
- **Created**: 2026-03-15

### Correct
- BQ76952 BMS system correctly detected with 16 cells, 17 cell voltage pins, 17 balance resistors, charge/discharge FETs (Q2-Q5 IPT012N08N5, Q12 ZXMP10A17GTA), and NTC sensors (RT1, RT2)
- Current sense shunt R45 (300uOhm) correctly detected between BAT- and PACK- with BQ76952 as sense IC
- Feedback voltage divider R28 (82k) / R31 (35.7k) correctly identified as feedback for U3 LMR38010 FB pin with is_feedback=true
- 16 cell input RC filters correctly detected (R2-R17 with C1-C16 pairs, 20 ohm + 220nF parallel caps, ~18 kHz cutoff) for BQ76952 cell voltage measurement inputs
- Shunt sense RC filters R19/C28 and R20/C28 (100 ohm + 100nF, ~15.9 kHz) correctly detected for SRP/SRN current sense inputs
- 12 MOSFET transistor circuits correctly analyzed including Q2-Q5 (IPT012N08N5 charge/discharge), Q12 (ZXMP10A17GTA P-channel), Q1 (DMN10H220LE) with gate resistors identified
- ESD protection diodes D3/D4 (ESD5B5.0ST1G) on USB data lines and D8 (PESD2CANFD) on CAN bus correctly detected
- I2C bus with pull-ups R32/R33 on I2C_SDA/I2C_SCL correctly detected connecting U4 (BQ76952) and U5
- RT1 and RT2 (10k NTC thermistors) correctly classified as thermistor type in component_types

### Incorrect
- U3 LMR38010 estimated_vout=1.978V is wrong. The analyzer assumed Vref=0.6V (heuristic) but LMR38010 actual Vref is 1.0V per datasheet. Correct Vout = 1.0 / 0.303 = 3.30V, matching the +3V3 output rail
  (signal_analysis.power_regulators)
- Design observation vout_net_mismatch reports 40.1% difference between estimated 1.978V and +3V3 rail, but this mismatch is caused by the wrong Vref assumption, not a real circuit error
  (signal_analysis.design_observations)

### Missed
(none)

### Suggestions
- Add LMR38010/LMR38020 to the Vref lookup table with Vref=1.0V to avoid heuristic fallback

---
