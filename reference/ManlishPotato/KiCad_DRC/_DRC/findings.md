# Findings: ManlishPotato/KiCad_DRC / _DRC

## FND-00000738: Stepper driver schematic correctly identifies 14 components across 4 types with proper power rails; Decoupling warnings claim C1/C2 caps missing on +5V/+12V, but caps exist on GND/signal nets (not ...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: _DRC.kicad_sch.json
- **Created**: 2026-03-23

### Correct
- 14 components (4R, 2C, 4J, 3IC, 1LED), power rails [+12V, +5V, GND, GNDPWR], net count=18 all match source. Component classification correct for U1=A4988, VR1=LM2596S, U2=LM555.

### Incorrect
- design_observations flags U1, VR1, U2 as lacking decoupling caps. C1 (0.01uF) is on GND and a signal net to U2 (timer cap), C2 (1uF) is on GND and a pot-connected signal net. These are functional caps, not bypass caps. The warning is technically correct that no bypass cap exists directly between +5V/+12V and GND, but the analyzer should differentiate functional caps vs bypass caps.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00000739: B.Cu reported as having 4 track segments but source file has zero B.Cu segment lines

- **Status**: new
- **Analyzer**: pcb
- **Source**: _DRC.kicad_pcb.json
- **Created**: 2026-03-23

### Correct
(none)

### Incorrect
- tracks.layer_distribution shows {'F.Cu': 83, 'B.Cu': 4} and net_lengths for +5V shows 4 B.Cu segments. However grep of the source PCB confirms 0 actual 'segment' primitives on B.Cu — all 14 footprints happen to be placed on B.Cu side. The 4 'B.Cu segments' appear to be pad stubs or via-to-pad connections miscounted as track segments.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00000740: Gerber completeness check correctly reports 'complete' based on gbrjob definition; Drill classification correctly identifies 6 vias (0.8mm), 52 component holes, and 0 mounting holes

- **Status**: new
- **Analyzer**: gerber
- **Source**: _Export.json
- **Created**: 2026-03-23

### Correct
- gbrjob lists only F.Cu and Edge.Cuts as expected layers. Analyzer finds exactly those two files and reports complete=True. This is accurate per-gbrjob, though the underlying PCB has components on B.Cu — this is a design/export decision, not an analyzer error.
- X2 attributes used for classification. Drill sizes (0.8, 1.0, 1.3, 2.0mm), hole counts, and split between PTH and NPTH all look correct. 58 total holes matches 6 vias + 52 component holes.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
