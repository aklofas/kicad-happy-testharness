# Findings: bumwings-kbd / v001R_pcb_R55_rp2040zero_sd_bumwings_v001R55_rp2040zero_sd

## FND-00002345: RZ1 (RP2040-Zero MCU module) misclassified as type 'resistor' instead of 'ic'; Key matrix correctly detected as 8x14 with 54 switches and 54 diodes

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: schematic_bumwings-kbd_v001_pcb_rp2040zero_bumwings_v001.kicad_sch.json
- **Created**: 2026-03-24

### Correct
- The analyzer accurately identified the split keyboard matrix topology via net analysis: 8 row nets (row_up, row_dn, row_home, row_mod plus 4 unnamed) and 14 column nets (col_Lt, col_Lr, col_Li1/Li2, col_Lm, col_Lp1/Lp2, col_Rt, col_Rr, col_Ri1/Ri2, col_Rm, col_Rp1/Rp2), with 54 switches and 54 diodes on the matrix. The detection_method 'topology' is appropriate.

### Incorrect
- The RP2040-Zero (ref RZ1) is a microcontroller module and should be classified as type 'ic'. The analyzer assigns type 'resistor' because the reference prefix 'RZ' is not in the standard IC prefix list (U, IC, etc.) and the value 'RP2040-Zero' doesn't match IC value heuristics. This also means it is counted in component_types.resistor (1) rather than ic, and appears in statistics with type mismatch. The missing_footprint list correctly flags it for missing footprint.
  (bom)

### Missed
(none)

### Suggestions
(none)

---
