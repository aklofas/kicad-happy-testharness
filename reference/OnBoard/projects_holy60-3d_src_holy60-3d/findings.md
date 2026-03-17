# Findings: OnBoard / projects_holy60-3d_src_holy60-3d

## FND-00000101: Holy60-3D is a 61-key keyboard switch matrix with no MCU on this board (connector-only). Matrix not detected despite clear Row/Column net names. 19 mounting holes classified but no connectors found.

- **Status**: confirmed
- **Analyzer**: schematic
- **Source**: repos/OnBoard/projects/holy60-3d/src/holy60-3d.kicad_sch
- **Created**: 2026-03-14

### Correct
- Correctly identified 61 switches and 61 diodes
- Correctly identified 19 mounting holes
- Component counts are accurate: 141 total, 9 unique parts

### Incorrect
- 84 components classified as other when they should be 61 switches + some diodes or other types - only some switches/diodes were categorized
  (statistics.component_types)

### Missed
- Key matrix not detected despite explicit Row 0-4 and Column 0-13 net names with 61 switches and 61 diodes in classic keyboard matrix topology
  (signal_analysis.key_matrices)
- No connectors detected - board must have connector(s) to connect to a controller board since there is no MCU
  (statistics.component_types)
- No subcircuit analysis despite clear switch matrix pattern
  (subcircuits)
- No IC pin analysis at all - board has no ICs which is valid, but matrix connector should be analyzed
  (ic_pin_analysis)

### Suggestions
- Key matrix detector should work with net names containing spaces like Row 0 and Column 2
- Boards without MCUs but with switch matrices should still be identified as keyboard matrix PCBs
- Component classification needs to handle all switches consistently

---
