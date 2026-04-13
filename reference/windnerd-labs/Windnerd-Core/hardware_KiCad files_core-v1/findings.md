# Findings: windnerd-labs/Windnerd-Core / hardware_KiCad files_core-v1

## FND-00001971: LDO regulator XC6206P332MR correctly identified with topology and rails; I2C bus correctly detected with pull-up resistors on both SDA and SCL; ESD protection device SP0502BAHT correctly identified...

- **Status**: new
- **Analyzer**: schematic
- **Source**: core-v1.kicad_sch
- **Created**: 2026-03-24

### Correct
- U1 (XC6206P332MR) is correctly classified as an LDO, with input rail VCC and output rail +3.3V. The output voltage is not estimated from the lib_id suffix in this case, which is correct since the part name encodes 3.3V but the analyzer does not always parse custom part number suffixes.
- The TMAG5273A1QDBVR magnetic sensor (U3) and STM32G031F8Px (U2) share the SDA and SCL nets. The analyzer correctly identifies both I2C lines with 2K pull-ups (R6 on SDA, R5 on SCL) to +3.3V and both devices on each line.
- D1 (SP0502BAHT) is correctly classified as an esd_ic type protection device guarding the TX2 net. The D2 (1N5819WS) Schottky diode is correctly typed as 'diode' in the BOM.
- Statistics counts 4 connectors: J1 (XH2.54-3P SMD, in_bom=true), J2 (Conn_01x13_Pin, in_bom=false), J3 (Conn_01x05_Pin, in_bom=true), J4 (Conn_01x01_Pin, in_bom=false). The BOM only shows J1 and J3 because J2 and J4 have in_bom=false, which is correct — they are mechanical/debug connectors excluded from BOM.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001972: Courtyard overlaps correctly detected on a very narrow board; Routing completeness correctly reported with unconnected INT_N pin noted

- **Status**: new
- **Analyzer**: pcb
- **Source**: core-v1.kicad_pcb
- **Created**: 2026-03-24

### Correct
- The board is 87.98×17.14 mm (narrow form factor), and the analyzer correctly identifies 3 courtyard overlaps: U2 vs J4 (1.21 mm²), J2 vs R1 (0.967 mm²), and C3 vs J4 (0.531 mm²). It also flags J2 as extending well beyond the board edge (edge_clearance -15.07 mm), indicating J2 is the edge connector hanging over the board boundary by design.
- The board has 26 nets; 25 have tracks (routed_nets=25) and 1 ('unconnected-(U3-INT_N-Pad5)') is an intentional KiCad no-connect net for the TMAG5273 INT_N pin. routing_complete=true and unrouted_count=0 are both accurate since the no-connect pin is intentionally left without tracks.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
