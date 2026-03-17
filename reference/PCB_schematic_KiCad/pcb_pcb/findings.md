# Findings: PCB_schematic_KiCad / pcb_pcb

## FND-00000242: STM32 board (104 components). Crystal Y1 present but not detected. Multi-driver VCC conflict (2 regulators driving same net). 3 regulators detected. 7 components missing value.

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: pcb.kicad_sch.json
- **Created**: 2026-03-16

### Correct
- 3 regulators detected

### Incorrect
- Multi-driver VCC conflict: 2 regulators driving same net not flagged
  (signal_analysis.power_regulators)

### Missed
- Crystal Y1 present in schematic but not detected
  (signal_analysis.crystal_circuits)
- 7 components missing value field
  (components)

### Suggestions
- Detect crystals even when value field is missing
- Flag multi-driver conflicts on power rails

---
