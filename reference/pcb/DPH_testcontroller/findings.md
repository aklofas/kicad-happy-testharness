# Findings: pcb / DPH_testcontroller

## FND-00000224: kiibohd DPH test controller (45 components, legacy KiCad 5). Zero signal detections but design contains 2x LM324 quad op-amps (8 active filter stages with 4066 analog switches) that were completely missed. BOM extraction is accurate.

- **Status**: confirmed
- **Analyzer**: schematic
- **Source**: DPH_testcontroller.sch.json
- **Created**: 2026-03-16

### Correct
- BOM component counts accurate: 16 diodes, 9 capacitors, 10 resistors, 4 ICs, 4 connectors, 1 switch

### Incorrect
(none)

### Missed
- 2x LM324AN quad op-amps (U1, U3) with all 8 channels active not detected in opamp_circuits. Each stage has sense signal input with feedback configuration for keyboard matrix signal conditioning.
  (signal_analysis.opamp_circuits)
- 8 RC filter stages (36K + 500pF, fc≈88Hz) on op-amp outputs not detected. Each LM324 output feeds through CD4066 analog switch to R-C low-pass filter.
  (signal_analysis.rc_filters)

### Suggestions
- Improve op-amp detection for LM324/TL074/OPA family ICs with non-power pins connected to signal nets
- Detect RC filter stages connected to op-amp outputs (not just standalone R-C pairs)

---
