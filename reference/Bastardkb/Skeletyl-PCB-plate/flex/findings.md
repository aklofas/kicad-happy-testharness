# Findings: Skeletyl-PCB-plate / flex_flex

## FND-00001407: Key matrix correctly detected as 4×5 grid with 15 actual keys; Addressable LED chain detection reports 3 chains (one duplicate) instead of 2; Component counts (69 total, 15 switches, 15 diodes, 30 ...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: flex.kicad_sch
- **Created**: 2026-03-24

### Correct
- The key matrix detector identifies 4 row nets and 5 column nets, and correctly reports estimated_keys=15 (not the naïve 4×5=20), matching the actual 15 switches and 15 diodes on the matrix. This matches the Skeletyl 3×5 layout (15-key per half) via net-name detection. The detection_method='net_name' is appropriate here since nets are labeled row2–row5, col2–col6.
- BOM breakdown: 15 SK6812MINI LEDs per footprint variant (two variants × 15 = 30 total LEDs), 15 SOD-123 diodes, 15 MX switches, 2 capacitors, 2 resistors, 5 connectors. Total 69 matches the components list. The 4 extra footprints in the PCB (73 vs 69) are expected — they represent fiducials or additional mechanical elements not in the schematic.

### Incorrect
- The analyzer finds three addressable LED chains: two of length 15 and one of length 1 (D6 alone). The two 15-element chains both start at D5 and share only D5 in their component lists — they represent two parallel sub-chains branching from the same data input. D6 (also from the same input net) is reported as a degenerate single-element chain. Total unique LEDs across all chains = 30 which matches statistics.component_types.led=30, but the chain count and topology are misleading. This keyboard PCB has two parallel chains of 15 LEDs each (left/right halves), not 2 complete+1 degenerate.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001408: 0.6 mm board thickness captured correctly for this thin PCB plate design

- **Status**: new
- **Analyzer**: pcb
- **Source**: flex.kicad_pcb
- **Created**: 2026-03-24

### Correct
- The stackup specifies 0.6 mm (0.51 mm core + 2×0.035 mm copper + 2×0.01 mm mask), which is intentional for this flex keyboard plate adapter. The analyzer faithfully captures board_thickness_mm=0.6. DFM correctly flags the 104.8×90.6 mm board as exceeding JLCPCB's 100×100 mm pricing boundary and the 0.1 mm annular ring as requiring an advanced process.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
