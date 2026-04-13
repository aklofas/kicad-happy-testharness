# Findings: heitorPB/Kicad-AMS1117 / AMS1117

## FND-00000780: power_regulators detector missed AP1117-50 linear regulator (U1); Decoupling analysis correctly identifies 2-cap bulk+bypass on both +12V and +5V rails

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: AMS1117.sch.json
- **Created**: 2026-03-23

### Correct
- decoupling_analysis correctly pairs C1 (220µF bulk) + C2 (100nF bypass) on +12V, and C3 (10µF bulk) + C4 (100nF bypass) on +5V. has_bulk=true, has_bypass=true for both rails. Self-resonant frequency values computed correctly.

### Incorrect
- U1 is an AP1117-50 (AMS1117-class LDO), +12V in → +5V out, with decoupling caps on both rails. power_regulators=[] is empty. The subcircuit description for U1 is also empty and neighbor_components=[] despite C1/C2 on +12V and C3/C4 on +5V clearly being associated. This is a missed detection for a textbook LDO circuit.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00000781: board_outline bounding_box is null — board has no edge cuts defined; Via annular ring DFM violation correctly detected (0.1mm < 0.125mm standard)

- **Status**: promoted
- **Analyzer**: pcb
- **Source**: AMS1117.kicad_pcb.json
- **Created**: 2026-03-23

### Correct
- All 12 vias are 0.6mm diameter / 0.4mm drill → 0.1mm annular ring, below the 0.125mm standard threshold. DFM violation correctly classified as requiring 'advanced' process.

### Incorrect
- board_outline shows edge_count=0, bounding_box=null, yet board_width_mm and board_height_mm are also null. The board has no Edge.Cuts geometry. This is a real design issue (board with no outline) that the analyzer captures correctly. However, the DFM tier reports 'advanced' with only one violation — without a board outline, area-based calculations (zone density per cm²) are unreliable.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---
