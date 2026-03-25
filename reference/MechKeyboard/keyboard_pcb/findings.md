# Findings: MechKeyboard / keyboard_pcb

## FND-00000944: I2C pull-up resistors R1/R2 not detected — has_pullup false despite R1(SDA-3V3) and R2(SCL-3V3) present; Key matrix correctly detected: 6 rows, 21 columns, 105 keys/switches/diodes; USB data lines ...

- **Status**: new
- **Analyzer**: schematic
- **Source**: keyboard_pcb.kicad_sch.json
- **Created**: 2026-03-23

### Correct
- The KiCad 6 .kicad_sch parser correctly reports the full matrix topology with all ROW1-ROW6 and COL1-COL21 nets, and accurate counts of 105 each.
- Both D+ and D- nets found on J1 and J2. The label_shape_warnings correctly flag D+, D-, and 5V as having no driver pins (they are net labels connected to passive pins, not PWR symbols). USB compliance section correctly notes ESD IC is absent (informational).

### Incorrect
- R1 connects pin2→3V3 and pin1→SDA; R2 connects pin2→3V3 and pin1→SCL. These are 4.7k pull-ups (confirmed by silkscreen). The i2c_bus observations report has_pullup=false, pullup_resistor=null for both SDA and SCL. This is a false negative — the pullup topology is there but not recognized, likely because 3V3 is classified as 'signal' not 'power' (no power symbol, comes from Teensy connector).
  (signal_analysis)
- The 3V3 and 5V nets are used as power rails (Teensy VIN=5V, Teensy 3V3 output) but classified as generic 'signal'. This causes downstream failures: I2C pullup detection fails because 3V3 is not recognized as a power rail for the pullup topology check. Root cause: no power symbols on these nets — they originate from connector pins, so the detector misses them.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00000945: Key matrix estimated_keys/switches_on_matrix/diodes_on_matrix all report 210 instead of 105

- **Status**: new
- **Analyzer**: schematic
- **Source**: keyboard_pcb.sch.json
- **Created**: 2026-03-23

### Correct
(none)

### Incorrect
- The legacy .sch schematic has 105 diodes and 105 switches (confirmed by statistics.component_types). The key_matrices detector reports rows=6, cols=21, estimated_keys=210, switches_on_matrix=210, diodes_on_matrix=210. The 6×21=126 max theoretical keys, but there are only 105 actual keys. The count inflation (210=2×105) suggests each switch/diode is being counted twice in the legacy parser.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00000946: Same key matrix double-counting bug: reports 210 keys/switches/diodes when actual is 105 each

- **Status**: new
- **Analyzer**: schematic
- **Source**: matrix.sch.json
- **Created**: 2026-03-23

### Correct
(none)

### Incorrect
- matrix.sch is a pure switch/diode matrix schematic with 105 switches and 105 diodes per statistics. The key_matrices section reports switches_on_matrix=210, diodes_on_matrix=210, estimated_keys=210 — exactly double. This is the same bug as keyboard_pcb.sch. The legacy .sch parser appears to double-count components when building the matrix.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00000947: Component counts correct: 105 diodes, 105 switches, 4 connectors, 2 resistors, 1 U1, 28 mounting holes; Courtyard overlaps reported between diodes and mounting holes (Hxx) at 0.0mm2 — false positiv...

- **Status**: new
- **Analyzer**: pcb
- **Source**: keyboard_pcb.kicad_pcb.json
- **Created**: 2026-03-23

### Correct
- component_groups accurately reflects the BOM. The Ref** entries (graphical text, 0 pads) are included in the footprint count but are harmless placeholders.
- connectivity shows total_nets_with_pads=145, routed_nets=139, unrouted_count=0. The 6-net gap corresponds exactly to the 6 unconnected-(U1-PadXX) nets for unused Teensy 4.0 pins. Net math is consistent.
- dfm_tier=advanced. Two violations: track spacing 0.127mm at advanced threshold, and board 436×124mm exceeding JLCPCB 100×100mm pricing tier. Both are accurate observations for this full-size keyboard PCB.

### Incorrect
- 10 courtyard overlap violations are reported between D41/D43/D47/D49/D52/D53/D56/D100 and H14-H23, but all have overlap_mm2=0.0. Zero-area 'overlaps' are not real violations; they are touching or near-touching boundaries being falsely flagged. These should be filtered or suppressed.
  (signal_analysis)

### Missed
- There are 2 GND zones but both show layer=None. The zones cover both F.Cu and B.Cu (confirmed by ground_domain zone_layers=['B.Cu','F.Cu']), but the zone objects themselves lose the layer information during parsing. This is a minor data quality issue but means zone-per-layer analysis would be incorrect.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00000948: All 9 layers found, no missing required or recommended layers, board dimensions consistent with PCB; Drill classification correctly identifies component holes, NPTH mounting holes, and 0 vias; B.Pa...

- **Status**: new
- **Analyzer**: gerber
- **Source**: Gerbers_Release-Candidate.json
- **Created**: 2026-03-23

### Correct
- completeness shows all standard 2-layer layers present (F.Cu, B.Cu, F.Mask, B.Mask, F.Paste, B.Paste, F.SilkS, B.SilkS, Edge.Cuts). Board dimensions 436.25×123.83mm match PCB analysis (436.245×123.825mm).
- 688 component holes + 159 mounting holes = 847 total holes. The 210 NPTH 1.7mm holes are likely stabilizer/switch plate holes (matching 105 2-pin switches×2=210 NPTH), and 210 PTH 1.5mm are switch socket holes. Zero vias is consistent with PCB analysis.
- The B.Paste layer extent is 0×0mm in alignment data, consistent with an all-THT design with no bottom-side SMD parts. F.Paste is also zero, consistent with the PCB having no SMD at all (smd_count=0).

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
