# Findings: siderakb/ergo-snm-keyboard / ErgoSNM_Keyboard_rev2_thumb_cluster

## FND-00002190: EC1 rotary encoder switch counted as matrix key, inflating switches_on_matrix to 7 instead of 6

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: ErgoSNM_Keyboard_rev2_thumb_cluster_thumb_cluster.kicad_sch.json
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
- The thumb cluster has KEY1..KEY6 (6 true matrix keys each with a 1N4148 diode) plus EC1 (Alps EC11 rotary encoder with integrated push switch). EC1's S1 pin connects to COL_7, but its S2 pin connects to an unnamed net (a direct MCU input, not a ROW net). The key matrix detector counts EC1 as a matrix switch because S1 touches COL_7, resulting in switches_on_matrix=7 and diodes_on_matrix=6. The true key matrix has only 6 switches. EC1's click function is wired as a direct input, not through the row-column diode matrix. The mismatch (7 switches, 6 diodes) is numerically correct but logically misleading—EC1 is not a matrix key.
  (findings)

### Missed
(none)

### Suggestions
(none)

---
