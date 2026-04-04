# Findings: gh60 / keyboard

## FND-00002080: Key matrix reports diodes_on_matrix=0 despite 65 diodes present on the matrix sub-sheet; SPI bus not detected despite explicit SCK/MOSI/MISO labels present on IC1 (ATmega32U4) ISP header; I2C false...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: schematic_gh60_keyboard.sch.json.json
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
- The matrix.sch sub-sheet contains 65 1N4148 diodes (one per key) wired in a standard key-matrix anti-ghosting configuration alongside 84 switches and 65 diodes all on row/col nets. The keyboard.sch.json key_matrices entry reports diodes_on_matrix=0 even though these diodes are part of the same hierarchical design and share the col/row nets. The detection_method is 'net_name', suggesting the detector only examines the sheet where the matrix nets were found rather than tracing cross-sheet diode connections.
  (signal_analysis)
- The bus_analysis.i2c section reports a bus on net 'col5' (line='SCL') with device IC1. The net name 'col5' is a keyboard matrix column net — it is not an I2C bus. The ATmega32U4 shares I2C and GPIO on the same physical pins, and here PD0/SCL is used as a keyboard column scan output, not as I2C. This is a false-positive I2C detection based on pin-name matching without considering the functional context of the net.
  (signal_analysis)

### Missed
- The top-level keyboard.sch contains local labels SCK, MOSI, MISO connecting IC1 (ATmega32U4) to an ISP programming header (6-pin connector). The bus_analysis.spi list is empty. The ATmega32U4 exposes these SPI pins for in-circuit programming. The analyzer detected two SPI-named labels on the sheet but did not synthesize them into a spi bus entry, likely because the chip's pin names do not match the SPI heuristic pattern when accessed through the legacy .sch parser.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00002081: Correctly analyzed fully-routed GH60 keyboard PCB with 338 footprints, 3305 track segments, and 7 copper zones

- **Status**: promoted
- **Analyzer**: pcb
- **Source**: pcb_gh60_keyboard.kicad_pcb.json.json
- **Created**: 2026-03-24

### Correct
- The GH60 is a 60% mechanical keyboard PCB. The analyzer correctly reports: 338 footprints (241 front / 97 back), 231 THT (mechanical key switches) and 101 SMD components, 2 copper layers, 3305 track segments, 179 vias, 7 copper fill zones, 285mm x 94.6mm board outline, and routing_complete=true. These are consistent with a production-ready keyboard PCB.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
