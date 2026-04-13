# Findings: Bastardkb/dilemma-cirque / dilemma-cirque

## FND-00002327: Assembly complexity reports all 9 components as SMD with 0 THT, but J1 is a through-hole connector; SPI and I2C bus interfaces not detected in bus_analysis despite clear net names MISO/MOSI/SCK/SS/...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: schematic_dilemma-cirque_dilemma-cirque_dilemma-cirque.kicad_sch.json
- **Created**: 2026-03-24

### Correct
- The analyzer correctly identifies 4 ferrite beads (FB1-FB4), 4 mounting holes (H1-H4), and 1 Cirque trackpad connector (J1) for a total of 9 components. The ferrite bead topology connecting mounting holes to GND via ferrite beads is captured in the netlist. Power rails GND and VCC are correctly extracted.

### Incorrect
- The schematic assembly_complexity section reports smd_count=9, tht_count=0. However, J1 (CirqueDB, lib_id Connector:Conn_01x12_Female) is a through-hole connector, confirmed by the PCB output where J1 has type=through_hole. The schematic analyzer is misclassifying the connector as SMD. PCB correctly reports smd_count=4, tht_count=1.
  (assembly_complexity)

### Missed
- The design has nets named MISO, MOSI, SCK, SS (SPI) and SDA, SCL (I2C) on a Cirque trackpad connector. The test_coverage section correctly identifies these as 'spi' and 'i2c' category nets. However, bus_analysis.spi and bus_analysis.i2c are both empty arrays. The analyzer inconsistently recognizes protocol net names for test coverage but not for bus_analysis — it likely requires IC components with typed pins rather than plain connector pins to trigger bus detection.
  (design_analysis)

### Suggestions
(none)

---

## FND-00002328: PCB correctly identifies board has no Edge.Cuts outline and reports null board dimensions

- **Status**: new
- **Analyzer**: pcb
- **Source**: pcb_dilemma-cirque_dilemma-cirque_dilemma-cirque.kicad_pcb.json
- **Created**: 2026-03-24

### Correct
- The board_outline section reports edge_count=0, edges=[], bounding_box=null, and statistics board_width_mm and board_height_mm are both null. This is consistent with the PCB having no Edge.Cuts layer content — correct behavior for an incomplete or sub-board design.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
