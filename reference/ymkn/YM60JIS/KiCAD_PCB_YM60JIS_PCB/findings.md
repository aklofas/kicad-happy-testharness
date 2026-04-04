# Findings: YM60JIS / KiCAD_PCB_YM60JIS_PCB

## FND-00001773: 165 total components detected matching source (67 SW + 1 BTN + 67 D + 7 R + 17 C + 4 U + 1 J + 1 Y); 5x14 key matrix with 67 keys and 67 diodes correctly detected; RP2040 + W25Q16 memory interface ...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: YM60JIS_PCB.kicad_sch.json
- **Created**: 2026-03-24

### Correct
- Source schematic has SW1-SW67 (67 key switches), BTN1 (1 tact switch), D1-D67 (67 diodes), R1-R7 (7 resistors), C1-C17 (17 capacitors), U1-U4 (4 ICs), J1 (1 USB-C connector), Y1 (1 crystal) = 165. Analyzer matches exactly.
- The key matrix detector correctly finds 5 rows (ROW0-ROW4) and 14 columns (COL0-COL13), estimated_keys=67, switches_on_matrix=67, diodes_on_matrix=67. This matches the JIS 60% layout with 67 keys.
- U4 (W25Q16JVUXIQ) flash connected to U3 (RP2040) via 6 shared signal nets is correctly detected as a memory interface. The total_pins=8 matches the W25Q16's package.
- U1 is correctly identified as a fixed 3.3V LDO (topology=LDO, input=+5V, output=+3V3, estimated_vout=3.3, vref_source=fixed_suffix). The vref is inferred from the part number suffix '332' meaning 3.32V.

### Incorrect
(none)

### Missed
- The RP2040 connects to the W25Q16 flash via QSPI signals: QSPI_SCLK, QSPI_SD0, QSPI_SD1, QSPI_SD2, QSPI_SD3, QSPI_SS. These are global labels in the schematic. The bus analyzer reports spi=[] because it likely matches against SPI-named nets (MOSI, MISO, SCK, etc.) but not QSPI-prefixed names. The memory_interfaces section correctly identifies the connection via shared nets, but the dedicated spi bus analysis is empty.
  (design_analysis)

### Suggestions
(none)

---

## FND-00001774: 173 footprints on fully routed 2-layer keyboard PCB; DFM board_size violation correctly flagged for 285x94mm exceeding 100x100mm; 50 courtyard overlaps correctly detected for keyboard layout

- **Status**: new
- **Analyzer**: pcb
- **Source**: YM60JIS_PCB.kicad_pcb.json
- **Created**: 2026-03-24

### Correct
- Analyzer correctly reports 173 footprints (165 SMD + 4 THT + 4 REF**), 2 copper layers, 1064 track segments, 160 vias, and routing_complete=true. The 285x94mm board is correct for a JIS 60% keyboard.
- The DFM analyzer correctly identifies that the 285x94mm keyboard PCB exceeds the JLCPCB standard tier 100x100mm limit, flagging it as a pricing-tier issue. This is accurate — oversized PCBs incur extra cost.
- A mechanical keyboard PCB intentionally places diodes directly under switch footprints, causing courtyard overlaps. The 50 detected overlaps (e.g., D50/SW50, J1/SW1) are real but expected design practice for dense keyboard layouts, not errors.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001775: Keyboard plate PCB correctly identified: 69 footprints, 0 tracks, no nets

- **Status**: new
- **Analyzer**: pcb
- **Source**: KiCAD_Plate_YM60JIS_Plate.kicad_pcb.json
- **Created**: 2026-03-24

### Correct
- The plate PCB has 67 switch cutouts (SW1-SW67, all THT) plus 1 REF** and 1 unnamed, totaling 69 footprints. It has no copper traces (track_segments=0) or nets (net_count=0), which is correct for a mechanical plate used only for switch mounting.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
