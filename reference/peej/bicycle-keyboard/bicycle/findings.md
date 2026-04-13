# Findings: peej/bicycle-keyboard / bicycle

## FND-00001988: Component counts, power rails, and BOM entries correctly parsed from KiCad 5 legacy schematic; RESET1 (Conn_01x01, value 'Reset') misclassified as 'switch' instead of 'connector'; TX0 (Conn_01x01, ...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: bicycle.sch.json
- **Created**: 2026-03-24

### Correct
- The analyzer correctly identifies 64 total components (excluding 5 power symbols: 2 VCC + 3 GND), 29 diodes (D1–D29), 1 Arduino Pro Micro IC (U1), 1 TRRS connector (J1), and the two power rails GND and VCC. The KiCad 5 legacy format is handled properly.
- The analyzer correctly identifies the 5x6 keyboard matrix with Row0–Row4 and Col0–Col5 net names, and uses the net_name detection method. The row and column net listings are accurate.
- The design_observations section correctly flags that U1 ARDUINO_PRO_MICRO has no bypass capacitors on the VCC rail. This is a genuine observation; the module relies on internal decoupling. The analyzer appropriately reports rails_without_caps=['VCC'] and rails_with_caps=[].

### Incorrect
- RESET1 is a single-pin connector instantiated from the Conn_01x01 library. Because its value field is 'Reset', the component type heuristic matches a 'reset switch' keyword and classifies it as 'switch'. The correct type is 'connector'. This inflates statistics.component_types.switch from the correct 29 to 30, and adds RESET1 to the switch list in components and BOM.
  (statistics)
- TX0 is a single-pin connector from the Conn_01x01 library (used as an exposed test pad for the TX UART line). Its value field 'TX0' apparently matches a transformer keyword heuristic ('TX' prefix or suffix). The correct type is 'connector'. It appears in statistics.component_types.transformer (count 1) incorrectly.
  (statistics)
- The source schematic contains exactly 29 SWITCH_PUSH components (MX0:0-5, MX1:0-5, MX2:0-5, MX3:0-5, MX4:1-5 — note MX4:0 is absent, making Row4 have only 5 keys) and exactly 29 diodes. The key matrix detector using net_name method reports estimated_keys=33, switches_on_matrix=33, and diodes_on_matrix=33 for a 5-row x 6-col matrix, overcounting by 4. The 5x6 matrix topology is correctly identified but the actual populated key count is wrong.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001989: PCB statistics correct: 87 footprints (64 schematic + 23 mounting holes), 2 copper layers, routing complete; SMD diodes (SOD123 axial footprint) correctly classified as SMD type; MX switches correc...

- **Status**: new
- **Analyzer**: pcb
- **Source**: bicycle.kicad_pcb.json
- **Created**: 2026-03-24

### Correct
- The 87 footprint count matches: 64 schematic components + 17 M2 mounting holes + 6 M8 mounting holes = 87. The board correctly reports 2 copper layers (F.Cu + B.Cu), 54 nets, 0 unrouted connections, 148.75mm x 119.0mm board size, and a distinctive non-rectangular bicycle-frame outline captured with 44 edge segments.
- All 29 diodes using the keyboard_parts:D_SOD123_axial footprint are correctly typed as 'smd'. All 29 MX key switches using Keyboard:MX_DoubleSided are correctly typed as 'through_hole'. The Arduino Pro Micro and single-pin connector test pads are also correctly typed as through_hole.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001990: has_pth_drill=false is wrong; bicycle.drl is the PTH drill file by KiCad naming convention; Gerber layer set correct: 7 files covering F.Cu, B.Cu, F.Mask, B.Mask, F.SilkS, B.SilkS, Edge.Cuts; F.Pas...

- **Status**: promoted
- **Analyzer**: gerber
- **Source**: gerber.json
- **Created**: 2026-03-24

### Correct
- The 2-layer keyboard PCB correctly reports all expected layers present. F.Paste is flagged as missing_recommended, which is appropriate since this is primarily a through-hole and SMD-without-paste design. Board dimensions 148.75mm x 119.0mm match the PCB output exactly.

### Incorrect
- KiCad exports two Excellon drill files: the default file (bicycle.drl) contains PTH holes and the file ending in -NPTH.drl contains NPTH holes. The analyzer typed bicycle.drl as 'unknown' because it lacks an explicit header tag, setting has_pth_drill=false. In practice bicycle.drl contains the through-hole component holes (0.6096mm diode pads, 0.7112mm MX switch pins, 1.0922mm Arduino header, etc.) and the 1.4986mm holes (116 count), which are plated. The correct result is has_pth_drill=true.
  (completeness)

### Missed
(none)

### Suggestions
(none)

---
