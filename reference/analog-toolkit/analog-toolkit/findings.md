# Findings: analog-toolkit / analog-toolkit

## FND-00000070: 13 false positive RF matching networks on ADC input conditioning circuits (0-ohm series resistors + 10nF anti-aliasing caps)

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: analog-toolkit.kicad_sch.json
- **Created**: 2026-03-13

### Correct
- U1 AP2204R-3.3 correctly identified as LDO with VBUS input and +3V3 output
- F1 fuse and U2 USBLC6-4 ESD protection correctly identified
- Decoupling analysis correct: +3V3 (4x caps, 5.0uF), VBUS (1x 4.7uF), +3.3VA (1x 100nF)
- I2C bus detected with correct no-pull-up observation; UART TX/RX detected

### Incorrect
- dnp_parts=1 but there are 13 DNP components (R5-R10, R17-R23). Counts BOM line items instead of component instances.
  (statistics.dnp_parts)

### Missed
- 6 RC anti-aliasing filters on ADC inputs (R11-R16 series + C8-C13 shunt to GND). rc_filters array is empty.
  (signal_analysis.rc_filters)
- Ferrite bead FB1 between +3V3 and +3.3VA with C7 100nF forms analog supply filter. Not detected.
  (signal_analysis.lc_filters)

### Suggestions
- RF matching detector too aggressive: triggering on any resistor near a cap connected to an IC. Should require antenna-like components or RF-frequency indicators.
- Fix dnp_parts to count component instances, not BOM line items.
- RC filter detection should handle 0-ohm series resistors (still a valid RC topology).
- Detect ferrite_bead + cap as analog supply filtering pattern.

---
