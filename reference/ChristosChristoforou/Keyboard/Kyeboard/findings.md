# Findings: Keyboard / Kyeboard

## FND-00000635: Button+/Button- and LED+/LED- incorrectly classified as differential pairs; U2 LM317 incorrectly flagged as missing input decoupling cap (C2 is present on __unnamed_50); Key matrix not detected des...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: Kyeboard.sch.json
- **Created**: 2026-03-23

### Correct
- U1 detected with input_rail=Vbus_5V and U2 with input_rail=__unnamed_50 (U1 output), forming a two-stage adjustable linear regulator chain for LED power. Topology classified as LDO which, while not perfectly accurate (LM317 is adjustable linear, ~1.25V dropout), is functionally reasonable.
- The top-level sheet reports 27 components while the PCB has 241 footprints. The 214-component gap comes from 72 instances of Button.sch (each instance has SW+D+LED) that are only parsed once in the KiCad 5 hierarchical model. The analyzer correctly parses what is in the schematic files; the instance multiplication is a known limitation of KiCad 5 legacy format.

### Incorrect
- The design_analysis.differential_pairs section flags 'Button+/Button-' and 'LED+/LED-' as differential pairs. Button+/- are the two terminals of a single Cherry MX switch (hierarchical labels into the key matrix sub-sheet), and LED+/- are LED power supply rails. Neither is a differential signal in any meaningful sense. This is a false-positive pattern-match on +/- naming.
  (signal_analysis)
- The design_observations entry for U2 reports 'missing_caps.input = __unnamed_50'. However, C2 (1u tantalum) has pin 1 on the __unnamed_50 net (U2's input). The analyzer misses it likely because C2's pin 2 goes to 'GND' (a separate power symbol from 'GNDREF'), and the decoupling detector may not equate GND with GNDREF as ground. This produces a false-positive missing-cap warning for U2's input.
  (signal_analysis)

### Missed
- The schematic uses hierarchical nets named C_0 through C_16 (17 columns) and R_0 through R_4 (5 rows) for an 85-key matrix. The key_matrices detector returns an empty list. The switch/diode pairs are in hierarchically-repeated Button.sch sub-sheets (72 instances), so the individual SW/D components aren't directly visible in the top sheet, but the row/column net labels are present and could be used for detection.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00000636: Keyboard_Matrix.sch analyzed standalone reports only 3 components instead of 216 (72 key cells)

- **Status**: new
- **Analyzer**: schematic
- **Source**: Keyboard_Matrix.sch.json
- **Created**: 2026-03-23

### Correct
(none)

### Incorrect
- When analyzed as a standalone root sheet, Keyboard_Matrix.sch reports 3 components (SW3, D2, D1 — one Button.sch instance). The sheet actually contains 72 hierarchical instances of Button.sch (each = 1 switch + 1 Schottky diode + 1 LED). The analyzer does not expand multi-instance hierarchical sheets in KiCad 5 legacy format, causing a massive under-count of 213 components. This is a structural limitation but materially misleads any assertion on component count for this sub-sheet.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00000637: kicad_version reported as 'unknown' for a KiCad 5 board (file_version 20171130); Board stats correctly extracted: 241 footprints, 4 copper layers, 725 vias, fully routed; Courtyard overlap between ...

- **Status**: promoted
- **Analyzer**: pcb
- **Source**: Kyeboard.kicad_pcb.json
- **Created**: 2026-03-23

### Correct
- footprint_count=241, copper_layers=4 (F.Cu/In1.Cu/In2.Cu/B.Cu), via_count=725, routing_complete=true, unrouted=0, board size 375.1x120.49mm all correct.
- J1 (1x13 pin socket at x=134.4mm) and J4 (1x24 pin socket at x=171.2mm) have courtyards that overlap in the x=[111.0,136.2] region. The 87.192mm² overlap value is geometrically correct. These are likely adjacent MCU breakout connectors placed in the same row.
- Board dimensions 375.1x120.49mm correctly identified as exceeding the 100x100mm standard pricing tier threshold at JLCPCB.

### Incorrect
- The file_version is 20171130 which corresponds to KiCad 5.0.x. The analyzer correctly parses the file but reports kicad_version='unknown' rather than '5'. This affects any downstream logic that branches on version.
  (signal_analysis)

### Missed
- The PCB contains 74 SW* (Cherry MX switch) footprints and 72 BAT60A diodes in a regular grid pattern forming an 80-key keyboard matrix. The placement analysis doesn't characterize this as a key matrix layout, which would be useful context for understanding the board's primary function.
  (signal_analysis)

### Suggestions
(none)

---
