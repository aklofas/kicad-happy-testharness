# Findings: keeb-x3 / keeb-x3

## FND-00002228: Key matrix correctly detected with 6 rows × 18 columns and 105 keys; QSPI bus to W25Q128 flash not detected in bus_analysis despite clear QSPI-* net names; kicad_version reports 'unknown' for a KiC...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: schematic_keeb-x3_keeb-x3.kicad_sch.json.json
- **Created**: 2026-03-24

### Correct
- The analyzer correctly identified the keyboard matrix via net-name detection, finding Row_0..Row_5 and Col_0..Col_17 nets, with 105 switches and 105 diodes on the matrix. The RP2040-based design also has its crystal, decoupling, and W25Q128 flash memory interface correctly identified in signal_analysis.

### Incorrect
- The file has file_version 20230121 which corresponds to KiCad 7. The analyzer correctly reads this version number but outputs kicad_version as 'unknown' rather than mapping the date-format version to the KiCad release. This affects display quality and any version-gated logic downstream.
  (kicad_version)

### Missed
- The design uses 6 QSPI nets (QSPI-SS, QSPI-SCLK, QSPI-SD0..SD3) connecting RP2040 to the W25Q128JVS flash. The memory_interfaces detector found the W25Q128 with 6 shared signal nets, but bus_analysis.spi is empty — the QSPI prefix is not matched by the SPI bus detector. The bus_topology.detected_bus_signals only reports Col_* and Row_* matrix signals, completely ignoring the QSPI bus.
  (design_analysis)

### Suggestions
(none)

---

## FND-00002229: Board outline not parsed: gr_poly with arc sub-elements on Edge.Cuts yields 0 edges and null bounding box

- **Status**: promoted
- **Analyzer**: pcb
- **Source**: pcb_keeb-x3_keeb-x3.kicad_pcb.json.json
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
- The keeb-x3 PCB defines its board outline as a single gr_poly element containing four arc segments (with rounded corners) on the Edge.Cuts layer. The analyzer reports edge_count=0, empty edges array, and null bounding_box. The source file clearly contains `(gr_poly ... (layer "Edge.Cuts"))` with arc-based pts. The analyzer appears to only parse gr_line/gr_arc/gr_rect primitives, not gr_poly with arc children, causing it to silently miss the entire board boundary.
  (board_outline)

### Missed
(none)

### Suggestions
(none)

---
