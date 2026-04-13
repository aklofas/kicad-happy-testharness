# Findings: mlab-modules/RFIQINT01 / hw_sch_pcb_RFIQINT01B

## FND-00001108: LM1117-3.3 (U3) correctly identified as LDO regulator generating +3V3 from VCC; MAX9321 differential line receivers (U1, U2) correctly identified as ICs with 8-pin SOIC footprints; Differential pai...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: RFIQINT01B.kicad_sch
- **Created**: 2026-03-23

### Correct
- The regulator topology, output rail, power budget (20mA for 2x MAX9321), inrush analysis, and sleep current audit for U3 are all accurately detected and reasonable.
- The BOM correctly groups U1 and U2 as MAX9321 with proper footprint and datasheet. All 48 components extracted, 32 nets matched between schematic and PCB outputs (32 net_count in schematic stats matches PCB).

### Incorrect
(none)

### Missed
- The design has 8 ADC differential pairs and 4 CLK differential pairs (N/P suffix nets). No differential pair detection or annotation is present in the output. This is a significant missed analysis for an RF IQ interface board.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00001109: Layer completeness, alignment, drill classification, and component count all correct; NPTH holes (1.6mm, count=12) classified under component_holes instead of mounting_holes

- **Status**: promoted
- **Analyzer**: gerber
- **Source**: hw_cam_profi
- **Created**: 2026-03-23

### Correct
- 9 gerber files present, all expected layers found, 48 unique components extracted matching schematic count, 126 vias (0.4mm drill) correctly classified, 6 NPTH mounting holes correctly identified. F.Paste is empty (back-side SMD only) which is correct.

### Incorrect
- The 12 NPTH 1.6mm holes appear in drill_classification.component_holes.tools as type='NPTH', but mounting_holes count is 0. 1.6mm NPTH holes are likely connector locating pins (SATA connectors use 1.6mm locating pegs), not mounting holes, so this may be debatable — but the mounting_holes bucket is empty when there are 12 NPTH holes which is worth flagging.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001110: PCB statistics, footprint count, and routing completeness correctly extracted

- **Status**: new
- **Analyzer**: pcb
- **Source**: RFIQINT01B.kicad_pcb
- **Created**: 2026-03-23

### Correct
- 48 footprints, 12 THT + 36 SMD, 650 segments, 126 vias, 2 zones, fully routed — all consistent with the gerber output (195 total holes: 126 vias + 69 component holes matches PCB via_count).

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
