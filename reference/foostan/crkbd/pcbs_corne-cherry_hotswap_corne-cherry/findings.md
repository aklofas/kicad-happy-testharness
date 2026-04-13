# Findings: foostan/crkbd / pcbs_corne-cherry_hotswap_corne-cherry

## FND-00000236: Split keyboard (18 components). All components have broken references (LED?, U?, D? placeholders), making all detection unreliable. 2 addressable LED chains and 5 ESD ICs detected but with annotation issues.

- **Status**: confirmed
- **Analyzer**: schematic
- **Source**: corne-cherry.kicad_sch.json
- **Created**: 2026-03-16

### Correct
(none)

### Incorrect
- All component references are placeholders (LED?, U?, D?) - broken annotation makes all detections unreliable
  (components)

### Missed
(none)

### Suggestions
- Flag schematics with placeholder references as potentially unreliable

---
