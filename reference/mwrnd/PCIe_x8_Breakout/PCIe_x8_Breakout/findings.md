# Findings: PCIe_x8_Breakout / PCIe_x8_Breakout

## FND-00001072: 35 U.FL coaxial connectors incorrectly classified as 'uart' debug connectors; PCIe x8 edge connector (J1) misclassified as 'jtag' debug connector; Component counts, test point detection, power rail...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: PCIe_x8_Breakout.kicad_sch.json
- **Created**: 2026-03-23

### Correct
- 42 components, 36 connectors, 5 test points (TP1 on GND, TP6-TP9 on PRSNT nets) all correctly parsed. 5 missing_mpn for test points correctly flagged. pwr_flag_warnings on +12V and +3.3VA correct (PCIe connector-only driven rails without PWR_FLAG).

### Incorrect
- All 35 U.FL connectors (J2-J36 carrying PCIe Rx/Tx lanes) are flagged as 'uart' debug interfaces in test_coverage.debug_connectors. These are coaxial RF connectors carrying PCIe differential pairs, not UART. The 2-pin coaxial footprint with GND+signal matches a heuristic that is incorrectly triggering for UART. Only J7 (Conn_02x08 with JTAG signals) is correctly identified.
  (signal_analysis)
- J1 (PCI_Express_x8 with 96+ pins including TCK/TMS/TDI/TDO/TRST sideband signals) is classified as a JTAG debug connector because it happens to carry PCIe JTAG sideband. The primary function is PCIe, not JTAG. This is a false positive.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001073: PCB statistics, layer stack, net list, routing all correct; Board outline with 3 edges is correct for an open-slot PCIe add-in card

- **Status**: new
- **Analyzer**: pcb
- **Source**: PCIe_x8_Breakout.kicad_pcb.json
- **Created**: 2026-03-23

### Correct
- 4-layer board (F.Cu, In1.Cu, In2.Cu, B.Cu), 42 footprints (35 SMD, 6 THT), 56 nets, 1812 track segments, 160 vias, all routed. GND zone spans all 4 layers with 157 stitching vias at 7.5/cm2 density. Power track widths 0.3mm for +12V and +3.3V correctly reported.
- The board outline has only 3 explicit lines (top, right, bottom). The missing left edge is the PCIe card edge connector tab — it is intentionally open/slotted. The bounding box correctly computes 39.3 x 51.3mm. This is expected PCIe add-in card geometry.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
