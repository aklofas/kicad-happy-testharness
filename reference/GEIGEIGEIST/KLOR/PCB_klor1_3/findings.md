# Findings: GEIGEIGEIST/KLOR / PCB_klor1_3

## FND-00000671: Component count inconsistency: statistics=88, simulation_readiness=100, assembly_complexity=109 — three different values; J1 (MJ-4PP-9, TRRS audio connector) misclassified as a UART debug connector...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: PCB_klor1_3_klor1_3.kicad_sch.json
- **Created**: 2026-03-23

### Correct
- 22 key switches with 22 diodes identified. Bus topology correctly detects col (width=12 covering col0..col5 = 6 signals) and row (width=8 covering row0..row3 = 4 signals) patterns from net names.
- SDA and SCL nets are detected as I2C with U1 (ProMicro) as the device, and pull_ups=[] (has_pull_up=false) is correct — there are no pull-up resistors in this design as pull-ups are on the ProMicro module itself.

### Incorrect
- The schematic has 88 total_components in statistics, but assembly_complexity.total_components=109 and simulation_readiness.total_components=100. The 88 in statistics matches the unique component refs; the other values likely include power symbols or virtual components being counted differently. This internal inconsistency is confusing and the discrepancy of 21 components (88 vs 109) is significant.
  (signal_analysis)
- J1 is a 4-pole phone jack (TRRS) used for split keyboard half-to-half communication (serial over TRRS). The analyzer detects TX/RX/VCC/GND nets and classifies it as a 'uart' debug interface with interface='uart'. This is misleading — it's not a debug connector, it's the keyboard interconnect. RX/TX nets being 'uncovered' in test_coverage is then also questionable.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00000672: Large keyboard PCB correctly extracted: 89 footprints, 159.7x118mm board, 329 vias, 1664 segments, 81 nets

- **Status**: new
- **Analyzer**: pcb
- **Source**: PCB_klor1_3_klor1_3.kicad_pcb.json
- **Created**: 2026-03-23

### Correct
- Split keyboard half with SK6812MINI+MX combo footprints correctly identified as through_hole type with 21 pads each (4 LED pads + 4 switch pads + mounting), 22 diodes, 9 mounting holes. PCB and schematic component counts align at 89 vs 88+1(OLED).

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00000673: KLOR gerber set complete (9 layers, 2 drill files PTH+NPTH), alignment correct, layer count=2; KLOR drill classification: 378 vias reported but PCB shows only 329 vias; extra 49 likely from 0.4mm N...

- **Status**: promoted
- **Analyzer**: gerber
- **Source**: PCB_klor1_3_gerbers.json
- **Created**: 2026-03-23

### Correct
- All required layers present (F.Cu, B.Cu, F.Mask, B.Mask, F.Paste, B.Paste, F.SilkS, B.SilkS, Edge.Cuts), alignment correctly reported as true. 670 total holes including 329 vias and large NPTH holes for keyboard switch alignment pins (1.7mm and 1.9mm NPTH) correctly categorized.

### Incorrect
- PCB analysis shows via_count=329, but gerber drill_classification shows vias.count=378 (using diameter_heuristic). The 44 holes at 0.399mm and 5 holes at 0.201mm are likely NPTH alignment or LED holes, not vias. Since no X2 attributes are present (classification_method='diameter_heuristic'), the threshold boundary is causing misclassification.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---
