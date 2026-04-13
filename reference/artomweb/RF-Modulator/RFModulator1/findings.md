# Findings: artomweb/RF-Modulator / RFModulator1

## FND-00001106: copper_layers_used reports 3 including Edge.Cuts, which is not a copper layer; track layer_distribution shows '' (empty string) for 11 segments instead of 'B.Cu'; Courtyard overlap detection correc...

- **Status**: promoted
- **Analyzer**: pcb
- **Source**: RFModulator1.kicad_pcb.json
- **Created**: 2026-03-23

### Correct
- J3 (VF330 coaxial, large SMD) overlaps R2, R3, and D1 — this is a known tight layout around an RF connector. The detection of these overlaps is correct and useful.

### Incorrect
- statistics.copper_layers_used=3 and copper_layer_names includes 'Edge.Cuts'. Edge.Cuts is a mechanical outline layer, not a copper layer. The board is actually a 2-layer board (F.Cu + B.Cu). This inflates copper layer count.
  (signal_analysis)
- tracks.layer_distribution has key '' with 11 segments and 'F.Cu' with 14. Empty string layer name indicates the analyzer failed to resolve the layer name for B.Cu segments. Similarly net_lengths for '+15V', 'GND', and 'Net-(Q2-S)' show layer '' instead of 'B.Cu'.
  (signal_analysis)
- J1 and J2 are PJRAN1X1U04X coaxial connectors with courtyard extending past the edge. Negative edge clearance (-7.25mm, -7.0mm) is expected for this connector type — they mount to the board edge by design. The warning is technically correct but highly misleading for panel-mount connectors.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001107: Potentiometers P1 and P2 are classified as 'connector' type instead of 'potentiometer' or 'resistor'; Component extraction, BOM, and net connectivity are all accurate for 18 components; No RF/analo...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: RFModulator1.kicad_sch.json
- **Created**: 2026-03-23

### Correct
- All 18 components are correctly identified: 7 caps, 3 resistors, 1 NJFET (Q2), 6 connectors/coaxials, 1 diode, 2 potentiometers. Nets are correctly traced including the JFET source-follower topology (Q2 drain to +15V, gate to GND, source feedback via R1).

### Incorrect
- P1 and P2 use lib_id 'Device:R_Potentiometer' with keywords 'resistor variable'. The analyzer assigns type='connector' rather than 'resistor'. This causes the component_types count to show 6 connectors instead of 4 connectors + 2 potentiometers, and they appear in the BOM under type='connector'.
  (signal_analysis)

### Missed
- The design is an RF modulator with a JFET (Q2) source follower, two variable capacitors (C6, C7 are trimmers), and a varactor diode (D1/1N4148 used as varactor). No frequency estimation, no detection of the varactor/trimmer tuning network, no signal chain analysis from J1/J2 input through JFET to J3 output.
  (signal_analysis)

### Suggestions
(none)

---
