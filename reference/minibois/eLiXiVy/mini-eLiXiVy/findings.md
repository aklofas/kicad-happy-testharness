# Findings: minibois/eLiXiVy / mini-eLiXiVy

## FND-00002338: Logo/graphic symbols misclassified as power rails; False positive SPI bus detected from AVR-ISP-6 ICSP programming connector; Rotary encoder quadrature signals (RE+/RE-) falsely flagged as differen...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: schematic_eLiXiVy_mini-eLiXiVy.sch.json.json
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
- power_rails lists 'Logo_Open_Hardware_Small', 'OSHW-Text-Logo', and 'mini-eLiXiVy-Logo' as power rails. These are decorative logo symbols with no pins (pins: [], point_count: 1) placed on the schematic for aesthetics. Their KiCad 5 component names happen to match the net names used in isolated power symbol placements, but they are not electrical power rails and should not appear in the power_rails list.
  (statistics)
- bus_analysis.spi contains a spurious entry with bus_id 'pin_J2' where J2 is an AVR-ISP-6 ICSP header. The analyzer matched pin names SCK/MOSI/MISO from this programming connector and incorrectly assigned the RESET net as MOSI and an unnamed net as MISO. This is a false positive — the ICSP connector should not be reported as a separate SPI bus instance; the actual SPI bus (bus_id '0') is correctly identified with U1 on SCK/MOSI/MISO.
  (signal_paths)
- differential_pairs contains an entry for RE+ and RE- with RE0 listed as shared_ic. RE0 is a Device:Rotary_Encoder_Switch — its A/B outputs (labeled RE+/RE-) are single-ended quadrature signals from a mechanical encoder, not differential pairs in any RF or signal-integrity sense. This is a false positive: mechanical encoder outputs should not be classified as differential_pairs.
  (signal_paths)

### Missed
(none)

### Suggestions
(none)

---

## FND-00002339: DFM violation correctly reported for oversized keyboard PCB

- **Status**: new
- **Analyzer**: pcb
- **Source**: pcb_eLiXiVy_mini-eLiXiVy.kicad_pcb.json.json
- **Created**: 2026-03-24

### Correct
- The PCB is 302.2x93.5mm — a full 65% keyboard layout. The analyzer correctly flags this as a DFM board_size violation against the 100x100mm JLCPCB standard tier threshold, with an appropriate message about higher fabrication pricing. The violation_count is 1 and is accurate.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
