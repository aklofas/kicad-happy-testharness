# Findings: oasis / pcb_main_pcb

## FND-00000240: Robot board (57 components). Regulator feedback Vout mismatch: 2.495V calculated vs 3.3V net label. LC filters and MOSFET circuits correctly detected.

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: pcb.kicad_sch.json
- **Created**: 2026-03-16

### Correct
- 2 LC filters correctly detected
- 2 MOSFET circuits correctly detected

### Incorrect
- Regulator feedback Vout mismatch: 2.495V calculated vs 3.3V net label
  (signal_analysis.power_regulators)

### Missed
(none)

### Suggestions
- Cross-check calculated Vout against net label for feedback-based regulators

---
