# Findings: theBrutzler/IndiaNavi_PCB / Navi_2_0

## FND-00000665: DISPLAY1 (EPD e-ink module) misclassified as type 'diode'; Dual MT3420C buck regulators correctly detected with feedback divider values and output voltages; I2C bus analysis correct: pull-ups detec...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: Navi_2_0.kicad_sch.json
- **Created**: 2026-03-23

### Correct
- signal_analysis.power_regulators correctly identifies U1 (+BATT≈4.14V from +5V) and U2 (+3V3≈3.18V from +BATT), both with correct inductors and feedback resistors. The small error in estimated 3.18V vs 3.3V reflects the heuristic Vref assumption.
- design_analysis.bus_analysis.i2c correctly identifies 4 I2C lines, detects 4.7k pull-ups to +3V3 on named nets, and correctly flags missing pull-ups on the unnamed nets used by U7 and U5 (GPS module).
- pwr_flag_warnings correctly flags +BATT and +3V3 as having power_in pins with no power_out or PWR_FLAG. These are internally generated rails from regulators, but the schematic lacks explicit PWR_FLAG symbols, so ERC would flag them.

### Incorrect
- DISPLAY1 uses lib_id=Graphic:SYM_Arrow45_Large (an arrow graphic symbol used as a placeholder) with footprint=Navi_2_0:EPD_MODUL 5.65. The analyzer classifies it as 'diode' due to the arrow symbol's shape, but it should be classified as 'display' or 'connector'. It appears in the BOM with type='diode', which is wrong.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00000666: Unusual front/back placement correctly detected: front_side=3, back_side=107; 4-layer board correctly identified with DFM tier=standard and board size violation flagged

- **Status**: new
- **Analyzer**: pcb
- **Source**: Navi_2_0.kicad_pcb.json
- **Created**: 2026-03-23

### Correct
- Only 3 footprints on front (DISPLAY1, SW2, SM3) and 107 on back. This accurately reflects the actual design — the EPD display connector, slide switches, and mounting hole are front-side; all electronics are on the back.
- copper_layers_used=4 with F.Cu, In1.Cu, In2.Cu, B.Cu is correct. DFM correctly flags board_size 111.7×136.95mm exceeding 100×100mm standard tier. Zone stitching on all 4 power/ground nets correctly analyzed.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00000667: Missing F.Paste and B.Paste layers not flagged despite 96 SMD components; 4-layer gerber set complete with inner layers In1.Cu and In2.Cu present

- **Status**: promoted
- **Analyzer**: gerber
- **Source**: GERBERS_V3.json
- **Created**: 2026-03-23

### Correct
- completeness.complete=true, all 9 expected layers (including In1.Cu and In2.Cu) found. Layer count=4 correct. Board dimensions 111.75×137.0mm match PCB output (111.7×136.95mm within rounding).

### Incorrect
- The gerber set has no F.Paste or B.Paste files. completeness.missing=[] because the .gbrjob file doesn't list paste layers as expected. However, the board has 96 SMD components requiring solder paste, so the absence of paste layers should be flagged as a DFM concern. The analyzer relies solely on the job file manifest and misses this.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---
