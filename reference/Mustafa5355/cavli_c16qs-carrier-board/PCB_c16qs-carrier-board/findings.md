# Findings: Mustafa5355/cavli_c16qs-carrier-board / PCB_c16qs-carrier-board

## FND-00002315: AP62250WU buck converter (U3) not detected in power_regulators; test_coverage incorrectly lists UART nets as uncovered despite J_UART1 being identified as a UART debug connector for those exact net...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: schematic_cavli_c16qs-carrier-board_src_c16qs-carrier-board.kicad_sch.json
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
- The test_coverage section reports UART_TX_3V3 and UART_RX_3V3 as 'uncovered_key_nets' (category 'uart'). At the same time, debug_connectors correctly identifies J_UART1 (Conn_01x04) as a UART connector with connected_nets including UART_TX_3V3 and UART_RX_3V3. This is self-contradictory: the nets are physically accessible via J_UART1 but the coverage logic fails to mark them covered when a matching debug connector is present.
  (test_coverage)
- The rc_filters list contains three entries. Entries 2 and 3 both involve R2 (10kΩ) but pair it with different capacitors (C8 and C9 respectively) and report swapped input/output nets (__unnamed_15 vs RST). R2 connects a single node between C8 and C9; the analyzer is traversing both directions and generating redundant filter detections from the same resistor node. One of these entries is a duplicate and both should likely resolve to a single pi-filter or RC chain.
  (signal_analysis)

### Missed
- U3 is an AP62250WU (lib_id Regulator_Switching:AP62250WU, described as '2.5A, 1.3MHz Buck DC/DC Converter'). It has VIN on +5V_IN, SW output to L1, and feedback resistors R3/R4. Despite being detected as a subcircuit and having its lib_id unambiguously identify it as a switching regulator, power_regulators is empty. The MC34063 in car_usb_power_adapter is detected (with topology 'unknown'), showing inconsistent coverage of the Regulator_Switching library.
  (signal_analysis)
- D1, D3, and D4 are SMF15A 200W TVS diodes (lib_id Diode:SMF15A), described as 'Transient Voltage Suppressor'. These should be classified as protection_devices. The protection_devices list is empty. TVS diodes are a standard protection category and the part value/description unambiguously identifies them as transient suppressors rather than rectifiers or signal diodes.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00002316: Drill-only directory flagged as incomplete Gerber set (missing copper/mask layers expected)

- **Status**: promoted
- **Analyzer**: gerber
- **Source**: gerber_cavli_c16qs-carrier-board_Fabrication_Drill.json
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
- The Fabrication_Drill directory contains only drill files (PTH + NPTH), no copper Gerbers. The analyzer reports completeness.complete=false and lists B.Cu, B.Mask, Edge.Cuts, F.Cu, F.Mask as missing_required layers. This is a false negative: when a directory contains exclusively drill files (no .gbr files), it should be treated as a drill-only package rather than an incomplete full Gerber set. The Gerber layers are correctly present in the separate Fabrication_Gerbers directory.
  (completeness)

### Missed
(none)

### Suggestions
(none)

---

## FND-00002317: Courtyard overlaps correctly detected, including large J_SIM1 vs U1 overlap

- **Status**: new
- **Analyzer**: pcb
- **Source**: pcb_cavli_c16qs-carrier-board_src_c16qs-carrier-board.kicad_pcb.json
- **Created**: 2026-03-24

### Correct
- The PCB analyzer detected 8 courtyard overlaps, prominently flagging a 19.5 mm2 overlap between J_SIM1 (JAE SIM card connector) and U1 (C16QS cellular module). Additional overlaps between J_SIM1 and nearby diodes/resistors were also caught. These are real placement issues in a densely packed 40.5x46.25mm board.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
