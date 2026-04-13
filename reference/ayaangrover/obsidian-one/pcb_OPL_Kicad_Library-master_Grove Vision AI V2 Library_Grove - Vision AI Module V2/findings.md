# Findings: ayaangrover/obsidian-one / pcb_OPL_Kicad_Library-master_Grove Vision AI V2 Library_Grove - Vision AI Module V2

## FND-00000229: Grove Vision AI V2 module (112 components). Regulators (2 DCDC + 1 LDO), feedback networks, protection devices, voltage dividers, crystal all correctly detected. Issue: gate_driver_ics for Q4 lists unrelated ICs (U1 processor, U3 LDO) — should only include ICs with outputs connected to gate net. Q4 gate reportedly on VCC_3V3 rail warrants verification.

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: pcb_OPL_Kicad_Library-master_Grove Vision AI V2 Library_Grove - Vision AI Module V2.kicad_sch.json
- **Created**: 2026-03-16

### Correct
- 2 feedback networks correctly identified: U6/U4 SY80004DQD DCDC converters with R33/R34 and R16/R26 dividers (ratio 0.180, Vout≈3.3V)
- U3 WR0331-18FF4R LDO (3.3V→1.8V) correctly detected with fixed output from part suffix
- 4 ESD protection diodes (D5-D8, DF2S6.8FS) correctly identified protecting SPI bus pins
- X1 24MHz crystal with C14/C15 (12pF) load caps correctly detected, effective load 9pF
- 2 RC filters on reset circuit (R7/C3 1.59kHz, R7/C16 72.34Hz) correctly identified

### Incorrect
- Q4 gate_driver_ics contains unrelated ICs (U1 processor, U3 LDO, U5 memory) — should only list ICs with output pins connected to gate net
  (signal_analysis.transistor_circuits)

### Missed
(none)

### Suggestions
- Refine gate_driver_ic detection to only include ICs whose output pins are directly connected to the transistor gate net

---
