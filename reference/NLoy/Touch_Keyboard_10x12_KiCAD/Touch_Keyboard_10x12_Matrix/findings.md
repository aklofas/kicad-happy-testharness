# Findings: Touch_Keyboard_10x12_KiCAD / Touch_Keyboard_10x12_Matrix

## FND-00001615: T1/T2/T3 (TOOLINGHOLE) misclassified as transformer; should be mounting_hole; M61 (MX_SW_solder keyboard switch) misclassified as 'other' instead of 'switch'; kicad_version reported as 'unknown' fo...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: Touch_Keyboard_10x12_Matrix.kicad_sch.json
- **Created**: 2026-03-24

### Correct
- The analyzer reports key_matrices with rows=12, columns=10, estimated_keys=118, switches_on_matrix=118. The 11th column net COLK connects only rotary encoders SW1, SW2, and a U3 GPIO — correctly excluded from the key matrix. The repo is named 'Touch_Keyboard_10x12_KiCAD' (10 columns x 12 rows), matching the detection.

### Incorrect
- Components T1, T2, T3 use lib_id 'Touch_Keyboard_Symbols:MountingHole' and keywords 'mounting hole', but are classified as type 'transformer' because their reference prefix 'T' triggers the transformer classifier instead of mounting_hole. The statistics report 'transformer': 3 and 'mounting_hole': 15, when it should be 'transformer': 0 and 'mounting_hole': 18.
  (statistics)
- Component M61 uses lib_id 'Touch_Keyboard_Symbols:MX_SW_solder' and keywords 'switch normally-open pushbutton push-button', identical to the 119 MX-prefixed keyboard switches that are correctly classified as switch. Because the reference prefix 'M' is not in the switch prefix list (which handles 'MX'), M61 falls through to 'other'. The statistics report 'switch': 120 (missing M61) and 'other': 1, but M61 is a keyboard switch identical to the MX-prefix variants. The BOM groups M61 with the 1u switch group (qty=109) correctly, showing the inconsistency.
  (statistics)
- The schematic file header is '(kicad_sch (version 20230121) (generator eeschema)' — it lacks a 'generator_version' field, which older KiCad 7.x exports omit. The file_version 20230121 definitively maps to KiCad 7.x. The analyzer outputs kicad_version='unknown' instead of inferring '7' from the numeric file version. Compare with UBW32 (file_version 20231120, generator_version '8.0') which correctly outputs kicad_version='8.0'.
  (kicad_version)
- The design has 119 SK6812MINI-E addressable LEDs (DIN/DOUT chain protocol) grouped into sections via named nets (LEDS, LEDS0-1, LEDS1-2, LEDS2-3, LEDS3-4, LEDS4-5). The analyzer reports 119 separate chains each with chain_length=1 and data_in_net=''. Inspection of the net list shows all Net-(LED*-DOUT) and Net-(LED*-DIN) nets have zero component-pin entries — the analyzer fails to map the SK6812's DIN/DOUT pin UUIDs to the LED component references, breaking chain following. The PCB correctly shows LED0 pad 2 on 'Net-(LED0-DOUT)' and pad 4 on 'LEDS', confirming the physical connections exist but are missing from the schematic pin-net map.
  (signal_analysis)

### Missed
(none)

### Suggestions
- Fix: T1/T2/T3 (TOOLINGHOLE) misclassified as transformer; should be mounting_hole
- Fix: M61 (MX_SW_solder keyboard switch) misclassified as 'other' instead of 'switch'

---

## FND-00001616: F.SilkS extent (512.6 x 186.8 mm) dramatically exceeds Edge.Cuts (428.6 x 121.4 mm) but no alignment issue flagged

- **Status**: promoted
- **Analyzer**: gerber
- **Source**: Gerber_Files.json
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
(none)

### Missed
- The F.SilkS layer extends 84 mm wider and 65 mm taller than the board outline (Edge.Cuts). This ~20% width and ~54% height overhang is far beyond any fabrication tolerance. It likely represents fab notes or silkscreen text printed outside the board area. The analyzer reports alignment.aligned=True and alignment.issues=[]. The F.Paste layer (width=0, height=0) is correctly reported as empty. All other copper and mask layers are within ~10 mm of Edge.Cuts. The silkscreen anomaly should generate an alignment warning.
  (alignment)

### Suggestions
(none)

---

## FND-00001617: PCB correctly reports 589 footprints, 2-layer board, 428.625 x 121.444 mm, 810 vias, fully routed

- **Status**: new
- **Analyzer**: pcb
- **Source**: Touch_Keyboard_10x12_Matrix.kicad_pcb.json
- **Created**: 2026-03-24

### Correct
- The PCB statistics match what is visible in the design: 118 MX key switches (MX group) plus 1 M61 switch, 119 SK6812MINI-E LEDs (LED group), 128 diodes (D group), 143 capacitors (C group), 10 ICs (U group), 20 resistors (R group), and various mounting holes/connectors. Routing is complete (unrouted_net_count=0). Zone count of 2302 reflects the large number of copper fill zones used for signal routing on this keyboard PCB.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
