# Findings: MatthewATaylor/Modular-Synth-Hardware / Delay

## FND-00000255: Modular synth delay module (PT2399-based, 186 components). False parallel capacitor groupings in PT2399 RC networks inflate capacitance values. Op-amp integrator misclassified as compensator. GND-base transistors accumulate false driver lists.

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: Delay_Delay.kicad_sch.json
- **Created**: 2026-03-16

### Correct
- Op-amp circuits for TL072/TL074 correctly identified with inverting/non-inverting configurations
- PT2399 delay ICs correctly classified as ICs

### Incorrect
- 21 of 45 RC filter entries contain false parallel capacitor groupings — caps on different PT2399 nodes (pins 13/14 and separate filter stages) incorrectly combined, producing wrong capacitance and cutoff values
  (signal_analysis.rc_filters)

### Missed
(none)

### Suggestions
- RC filter parallel-cap detection should verify both caps share the same two terminal nodes, not just one shared node

---
