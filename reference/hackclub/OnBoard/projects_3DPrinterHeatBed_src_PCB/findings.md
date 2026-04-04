# Findings: OnBoard / projects_3DPrinterHeatBed_src_PCB

## FND-00000089: Simple heated bed PCB with single heater element between +24V and GND. Analyzer output is accurate for this minimal design.

- **Status**: confirmed
- **Analyzer**: schematic
- **Source**: repos/OnBoard/projects/3DPrinterHeatBed/src/PCB.kicad_sch
- **Created**: 2026-03-14

### Correct
- Heater (Device:Heater with R prefix) correctly classified as resistor type
- 4 mounting holes correctly identified and excluded from BOM
- Power rails +24V and GND correctly detected
- PWR_FLAG warnings correctly issued for both power rails

### Incorrect
(none)

### Missed
(none)

### Suggestions
- Could note that lib_id Device:Heater indicates a heating element rather than a standard resistor, though resistor classification is technically correct

---
