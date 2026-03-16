# Findings: RVPC / SOFTWARE_rvpc_tools_esp32s2-cookbook_hardware_exposed_power_rails_exposed_power_rails

## FND-00000230: OLIMEX RVPC ESP32-S2 power rails board (37 components). All 6 HX6306P332MR LDO regulators correctly identified with accurate 3.3V output estimates. Crystal Y1 40MHz with correct load caps. RC filter R6/C2 correct. False positive: decoupling analysis reports missing output caps on regulators but caps are connected via global labels to shared rails that DO have proper decoupling.

- **Status**: confirmed
- **Analyzer**: schematic
- **Source**: SOFTWARE_rvpc_tools_esp32s2-cookbook_hardware_exposed_power_rails_exposed_power_rails.kicad_sch.json
- **Created**: 2026-03-16

### Correct
- 6 LDO regulators (U1-U4, U6, U7, all HX6306P332MR) correctly identified with LDO topology and 3.3V estimated output
- Y1 40MHz crystal with C9/C10 (10pF) correctly detected, effective load 8pF within ESP32-S2 spec
- R6(5.1k)/C2(1uF) RC filter (31.21Hz cutoff) correctly detected on GPIO0 reset path
- BOM accurate: 14 capacitors, 10 resistors, 7 ICs, 3 connectors, 1 diode, 1 LED, 1 crystal

### Incorrect
- Decoupling analysis reports missing output capacitors on all 6 regulators, but caps are present via global label connectivity (VBUS, VDD3P3, etc. rails each have 2-4uF). Analyzer doesn't trace global label connections for decoupling verification.
  (signal_analysis.design_observations)

### Missed
(none)

### Suggestions
- Enhance decoupling analysis to trace global labels and include shared-rail capacitors in per-IC decoupling assessment

---
