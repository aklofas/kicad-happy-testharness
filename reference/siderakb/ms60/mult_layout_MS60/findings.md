# Findings: siderakb/ms60 / mult_layout_MS60

## FND-00000234: Keyboard (155 components). Decoupling cap C6 double-counted on both +3V3 and +5V rails. Key matrix reports 78 switches on 5x15 matrix (75 positions) with 3 extra switches unexplained.

- **Status**: confirmed
- **Analyzer**: schematic
- **Source**: MS60.kicad_sch.json
- **Created**: 2026-03-16

### Correct
(none)

### Incorrect
- Decoupling cap C6 double-counted - listed on both +3V3 and +5V rails
  (signal_analysis.decoupling)
- Key matrix reports 78 switches on 5x15 matrix (75 positions) - 3 extra switches unexplained
  (signal_analysis.key_matrix)

### Missed
(none)

### Suggestions
- Ensure decoupling caps are only counted on their actual rail
- Validate key matrix switch count against matrix dimensions

---
