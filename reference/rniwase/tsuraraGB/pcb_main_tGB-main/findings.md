# Findings: tsuraraGB / pcb_main_tGB-main

## FND-00000237: Game Boy clone (70 components). U4 regulator Vout estimated 1.659V but net labeled 3.3V (Vref assumption wrong). RC filter R11/C19 has output==ground anomaly. 2 regulators and 1 crystal correctly detected.

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: tGB-main.kicad_sch.json
- **Created**: 2026-03-16

### Correct
- 2 regulators correctly detected
- 1 crystal correctly detected

### Incorrect
- U4 regulator Vout estimated 1.659V but net labeled 3.3V - Vref assumption wrong in feedback divider calculation
  (signal_analysis.power_regulators)
- RC filter R11/C19 has output==ground anomaly
  (signal_analysis.rc_filters)

### Missed
(none)

### Suggestions
- Verify Vref assumptions against actual regulator datasheet
- Flag RC filters where output net equals ground

---
