# Findings: INTI-CMNB/KiDiff / tests_cases_1_b_1

## FND-00000192: Variant b of ESP32 MOSFET board — coordinate-only differences from variant a. Output is logically identical confirming position-independent parsing. Same issues as variant a (flyback diode false negative, regulator cap false positive).

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: tests_cases_1_b_1.kicad_sch.json
- **Created**: 2026-03-15

### Correct
- All outputs identical to variant a despite coordinate changes

### Incorrect
- Same flyback diode false negative as variant a
  (signal_analysis.transistor_circuits)
- Same regulator cap false positive as variant a
  (signal_analysis.design_observations)

### Missed
(none)

### Suggestions
- Use a/b pair for regression testing: any functional diff indicates position-dependent bug

---
