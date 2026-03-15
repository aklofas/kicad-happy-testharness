# Findings: OnBoard / projects_mobile_power_station_charger_src_battery-bus

## FND-00000098: Battery charger/power station with LT3790 buck-boost, ESP32-C3, USB-C PD. Major component classification failure: 105 of 136 components classified as other due to non-standard reference designator prefixes (Cch_, Rch_, Cc_, Ruc, etc).

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: repos/OnBoard/projects/mobile_power_station_charger/src/battery-bus.kicad_sch
- **Created**: 2026-03-14

### Correct
- AMS1117-3.3 LDO correctly identified
- LMR36520FADDAR switching regulator detected
- USB differential pair (D+/D-) detected
- ESP32-C3 missing decoupling correctly flagged in design_observations

### Incorrect
- 105 of 136 components (77%) classified as other — components with non-standard prefixes like Cch_, Rch_, Cc_, Ruc, Lch, Qch_, Dch are not recognized as capacitors/resistors/inductors/transistors/diodes
  (statistics.component_types)
- Only 4 capacitors counted in statistics despite ~35 capacitor-type BOM entries with Cc_/Cch_ prefixes
  (statistics.component_types)
- BOM sum (126) does not match total_components (136) — 10 missing, mounting_hole(3) only partially explains gap
  (statistics)
- LT3790 buck-boost converter not detected as power regulator — classified as other
  (signal_analysis.power_regulators)

### Missed
- No voltage dividers detected despite many 200K/100K/33K resistors likely forming feedback networks
  (signal_analysis.voltage_dividers)
- No current sense detection despite Rch_Ibat (0.013 ohm) and Rch_Iin (0.003 ohm) sense resistors
  (signal_analysis.current_sense)
- No charger circuit detection for LT3790 buck-boost charger
  (signal_analysis)
- USB-C PD controller (CYPD3177) not recognized
  (design_analysis)
- ACS712 current sensor IC not detected
  (signal_analysis.current_sense)
- MCP4725 DAC not recognized as analog output device
  (design_analysis)

### Suggestions
- Component classifier should parse reference prefixes more flexibly — strip trailing underscores/numbers and match first letter (C=capacitor, R=resistor, L=inductor, Q=transistor, D=diode)
- Non-standard prefixes like Cch_, Rch_ are user conventions for hierarchical sheets and should still be classified by first letter

---
