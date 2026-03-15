# Findings: OnBoard / projects_superflat_src_superflat

## FND-00000094: Low-profile wireless keyboard with BQ24075 battery charger and XC6206 LDO. Key matrix and power chain correctly identified. BOM matches perfectly.

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: repos/OnBoard/projects/superflat/src/superflat.kicad_sch
- **Created**: 2026-03-14

### Correct
- BOM quantity sum (94) matches total_components (94) exactly
- Key matrix correctly detected: 5 rows x 6 cols, 30 switches, 30 diodes
- BQ24075RGT battery charger correctly identified with input +5V and output +VSW
- XC6206 LDO correctly identified: input +VSW, output +3.3V
- Battery voltage divider R12(806k)/R11(2M) for VSENSE correctly detected
- BSD3C051V diode protection and 750mA fuse correctly identified
- 2N7002 MOSFET transistor circuit detected (SYSOFF control)
- Decoupling analysis covers 5 rails including Earth and +BATT

### Incorrect
(none)

### Missed
- No wireless/Bluetooth module detection despite being a wireless keyboard
  (design_analysis.bus_analysis)

### Suggestions
- Consider wireless module detection for keyboard designs

---
