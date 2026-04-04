# Findings: KiCad_JLC_template / pcb_JLC_DemoBoard

## FND-00000736: Simple LED driver circuit (BT1, R1, D1) correctly parsed with 3 nets, correct types; Battery polarity issue not flagged: BT1 pin1 ('+') connects to GND, pin2 ('-') connects to VCC

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: pcb_JLC_DemoBoard.sch.json
- **Created**: 2026-03-23

### Correct
- 3 components, 3 nets (GND, VCC, unnamed signal), correct power rail identification, component types (battery, resistor, led) all correct.

### Incorrect
(none)

### Missed
- In the net output, BT1 pin '1' (named '+') is on the GND net and pin '2' (named '-') is on VCC. This is reversed polarity relative to standard conventions. No ERC warning generated. May be a symbol convention artifact in KiCad 5, but warrants a design observation.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00000737: PCB correctly analyzed: 3 SMD components, circular board (14.3×14.4mm), GND zones on both layers; Edge clearance warnings incorrectly fire for BT1 (-16.66mm) and R1 (-6.16mm) which are inside circu...

- **Status**: promoted
- **Analyzer**: pcb
- **Source**: pcb_JLC_DemoBoard.kicad_pcb.json
- **Created**: 2026-03-23

### Correct
- Footprint count, component types, zone fill ratios, via stitching, board dimensions, and net routing all look accurate. 6 stitching vias on GND correctly identified.

### Incorrect
- Board outline is a circle. Edge clearance computation uses bounding box (14.3×14.4mm rectangle) rather than actual circular outline geometry. Components well within the circle appear to violate clearance to the bounding box corners. This is a known limitation when the board is circular.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---
