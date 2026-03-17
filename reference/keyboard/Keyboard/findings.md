# Findings: keyboard / Keyboard

## FND-00000190: Mechanical keyboard (322 components from sub-sheets). Correct: 80 LEDs, 80 caps, 81 diodes, 81 switches all correctly counted; decoupling properly associated with +5V; missing footprints flagged. Incorrect: all 22 global labels flagged as single_use (C1-C15 and R1-R6 appear on multiple sheets). Missed: keyboard switch matrix detection, SK6812 LED daisy-chain.

- **Status**: confirmed
- **Analyzer**: schematic
- **Source**: Keyboard.kicad_sch.json
- **Created**: 2026-03-15

### Correct
- 322 components correctly counted from sub-sheets
- Decoupling for 80 SK6812RGBW LEDs correct

### Incorrect
- All 22 global labels flagged as single_use despite appearing on multiple sheets
  (hierarchical_labels.single_use_global_labels)

### Missed
(none)

### Suggestions
- Fix single_use_global_labels to count across all hierarchical sheets

---
