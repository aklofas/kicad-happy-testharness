# Findings: Kicad-Hardware-Design / HARDWARE_Kicad-Hardware-Design

## FND-00000785: L7805 regulator with bridge rectifier and filter caps correctly identified; Bridge rectifier topology not identified as a distinct detector finding; power_rails shows only GND and PWR_FLAG — missin...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: HARDWARE_Kicad-Hardware-Design.kicad_sch.json
- **Created**: 2026-03-23

### Correct
- Subcircuit detected: L7805 (U1) with C1/C2/C3 caps, D1-D4 diodes (bridge), R1 resistor, D5 LED, J1/J2 connectors. Component counts (12 total: 1 IC, 4 diodes, 1 resistor, 2 connectors, 3 caps, 1 LED) are correct.

### Incorrect
- The schematic has no named power symbols for the rectified DC bus or the 5V output; they're unnamed nets. The analyzer correctly reports only named power rails, but this means the 5V supply is invisible in the power_rails summary. This is a design limitation of the schematic (no PWR_FLAG on the output), not strictly an analyzer bug, but it means the regulator output net is unnamed.
  (signal_analysis)

### Missed
- D1-D4 form a full-wave bridge rectifier — a very common and recognizable pattern. The analyzer correctly identified them as diodes but did not call out the H-bridge/bridge-rectifier arrangement in any detector field (no 'bridge_rectifier' or similar subcircuit type).
  (signal_analysis)

### Suggestions
(none)

---

## FND-00000786: R1 edge clearance reported as -15.43mm — component appears to be outside the board outline; copper_layers_used=1 (B.Cu only) but all 16 footprints are on F.Cu — misleading; Decoupling cap C2 correc...

- **Status**: promoted
- **Analyzer**: pcb
- **Source**: HARDWARE_Kicad-Hardware-Design.kicad_pcb.json
- **Created**: 2026-03-23

### Correct
- The decoupling_placement correctly finds C2 as the closest cap to U1, sharing GND and the rectified DC net. C3 (output cap) is also correctly linked via the output net.

### Incorrect
- The PCB shows R1 at X=116.0, Y=74.66 with courtyard max_y=96.43. Board outline max_y=81.0. The courtyard extends ~15mm below the board edge, which is geometrically impossible if the board outline is correct. This may be a footprint issue (very tall courtyard for R_Axial_DIN0411 with P20.32mm) rather than the component truly being outside the board. The negative clearance number is correct numerically but should be flagged as 'courtyard extends beyond board' rather than 'component outside board'.
  (signal_analysis)
- The PCB routes all traces on B.Cu (60 segments), which is valid for a single-sided board where THT components sit on the top but trace copper is on the bottom. However, the report says copper_layers_used=1 with layer='B.Cu', yet footprints are placed on 'F.Cu'. This is internally consistent but could confuse: a '2-layer' board is defined in the gerber (F.Cu and B.Cu both present), but all routing is on B.Cu. The front copper layer has only pads (flashes), no traces.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00000787: Alignment flagged as false (19.7mm width variance) — likely a false positive for THT board; Complete 2-layer gerber set with correct drill classification (25 PTH component holes, 4 NPTH mounting ho...

- **Status**: promoted
- **Analyzer**: gerber
- **Source**: GERBER.json
- **Created**: 2026-03-23

### Correct
- All 9 expected layers present, 0 missing. PTH drills correctly identified as component holes (0.8-1.3mm). NPTH correctly identified as mounting holes (3.5mm x4). Hole count 29 total matches expectation for 12 components.

### Incorrect
- The gerber alignment check compares copper extent to board outline. For a THT-only board where all components are through-hole, copper traces only occupy the component area (not the full board outline). B.Cu extent (81x23mm) is smaller than Edge.Cuts (95x33.5mm) because traces cluster around components. This is normal and expected, not a misalignment. The false-positive rate for this check on THT boards is high.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---
