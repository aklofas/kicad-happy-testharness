# Findings: cnlohr/cnhardware / addlepatedarray_synthtest

## FND-00000162: Synthesizer test board with TCXO oscillator. Y1 CFPS-72 TCXO misclassified as crystal instead of oscillator.

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: addlepatedarray_synthtest_synthtest.kicad_sch.json
- **Created**: 2026-03-15

### Correct
(none)

### Incorrect
- Y1 with lib_id 'Oscillator:CFPS-72' (active TCXO, value 'TG-5006CG-12H 26.0000M3') classified as crystal instead of oscillator
  (signal_analysis.crystal_circuits)

### Missed
(none)

### Suggestions
- Lib_id 'Oscillator:*' should classify as oscillator, not crystal
- TCXO frequency parsing should extract 26MHz from 'TG-5006CG-12H 26.0000M3'

---
