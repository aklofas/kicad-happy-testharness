# Findings: souseiki-fammy-kicad / fammy

## FND-00000243: Famicom clone (52 components). 5 RC filters detected with suspicious capacitor reuse (C2 in 3 filters, C3 in 2). 1 BJT and 10 decoupling caps correct.

- **Status**: confirmed
- **Analyzer**: schematic
- **Source**: fammy.kicad_sch.json
- **Created**: 2026-03-16

### Correct
- 1 BJT correctly detected

### Incorrect
- RC filter capacitor reuse: C2 appears in 3 filters, C3 in 2 - same capacitor counted in multiple filter instances
  (signal_analysis.rc_filters)

### Missed
(none)

### Suggestions
- Deduplicate capacitors shared across multiple RC filter detections

---
