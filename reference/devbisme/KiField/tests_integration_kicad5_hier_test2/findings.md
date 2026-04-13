# Findings: devbisme/KiField / tests_integration_kicad5_hier_test2

## FND-00001649: Correct component count and I2C detection for AD5593R; I2C bus correctly detected on AD5593R SDA/SCL pins

- **Status**: new
- **Analyzer**: schematic
- **Source**: tests_integration_kicad7_random_circuit.kicad_sch.json
- **Created**: 2026-03-24

### Correct
- The kicad7 random_circuit schematic has 4 real components (U1=AD5593R, U2=Z80CPU, C1, C2). The analyzer correctly reports total_components=4, unique_parts=3, and detects the I2C interface (SDA/SCL) on the AD5593R. Power rails +5V and GND are correctly identified.
- The AD5593R (U1) has SDA and SCL pins connected to named nets. The analyzer correctly identifies two I2C bus entries, one for SDA and one for SCL, with U1 as the device on each.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001650: Correct component and BOM counts for multi-unit component (RN1); Op-amp circuits correctly detected in AD8676xR (dual op-amp)

- **Status**: new
- **Analyzer**: schematic
- **Source**: tests_integration_kicad6_random_circuit.kicad_sch.json
- **Created**: 2026-03-24

### Correct
- The schematic contains Q1, Q2 (2 NPN transistors), RN1 (4-unit resistor network), and U1 (dual op-amp AD8676xR with 3 units). total_components=4 (unique refs), unique_parts=3 (unique BOM entries by value), and the components list has 9 entries (one per unit). This is correct multi-unit handling.
- The AD8676xR is a dual op-amp. The analyzer detects 3 op-amp circuit entries (one for the power unit and two for the signal units), correctly identifying comparator_or_open_loop configuration for both signal units based on the absence of feedback resistors.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001651: Correct component count (18) including DNP resistors in integration.sch; DNP resistors correctly identified; I2C bus for CAT24C32 EEPROM not detected despite I2C pull-up resistors present

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: tests_integration_misc_integration.sch.json
- **Created**: 2026-03-24

### Correct
- The integration.sch contains 18 real components (H1-H4, J3, J6, J9, Q1, Q2, R6, R7, R8, R9, R11, R23, R24, R29, U2). The analyzer correctly counts all 18 including DNP parts (R7, R9, R11) and reports dnp_parts=3.
- Three resistors (R7, R9, R11) have value 'DNP' and are marked dnp=true in the source schematic. The analyzer correctly reports dnp_parts=3 and flags them in the BOM with dnp=true.

### Incorrect
(none)

### Missed
- The CAT24C32 is an I2C EEPROM connected via nets ID_SD_EEPROM (SDA) and ID_SC_EEPROM (SCL), with 3.9K pull-up resistors R6 and R8 to P3V3. The analyzer does not detect an I2C bus here because the net names use non-standard RPi HAT naming (ID_SD/ID_SC instead of SDA/SCL) and the KiCad 5 legacy component has no pin connectivity data. This is an inherent limitation for non-standard net naming in KiCad 5 format.
  (design_analysis)

### Suggestions
(none)

---

## FND-00001652: Correct component count (29) for NeoESP.sch; Neopixel addressable LED chain correctly detected (D2=Neopixel_THT); RV1 (potentiometer) misclassified as 'resistor' type

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: tests_integration_misc_NeoESP.sch.json
- **Created**: 2026-03-24

### Correct
- The NeoESP.sch contains exactly 29 unique component references: A1, C1-C4, D1, D2, J1-J4, K1, L1, Q1, R1-R11, RV1, U1-U3. The analyzer reports total_components=29, which matches.
- D2 is a Neopixel_THT (WS2812-type) LED. The analyzer correctly detects an addressable LED chain of length 1 with protocol 'single-wire (WS2812)' and estimates 60mA current.

### Incorrect
- RV1 (value '10k POT', lib_id 'POT') is a trimmer potentiometer but is classified as type 'resistor'. While potentiometers are resistive, they should ideally be classified as a distinct type (e.g., 'potentiometer') or at minimum reflected in component_types as a separate category. The current classification conflates passive resistors with variable resistors.
  (statistics)

### Missed
(none)

### Suggestions
- Fix: RV1 (potentiometer) misclassified as 'resistor' type

---

## FND-00001653: All 45 components correctly counted in avishorp.sch

- **Status**: new
- **Analyzer**: schematic
- **Source**: tests_integration_misc_avishorp.sch.json
- **Created**: 2026-03-24

### Correct
- The avishorp.sch has 45 unique component references (R1-R17: 17, Q1-Q3: 3, D1: 1, C1-C9: 9, J1-J7: 7, U1-U8: 8). The analyzer reports total_components=45 and the component_types breakdown sums to 45 correctly.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001654: Hierarchical FPGA schematic correctly parsed across 4 sheets; 84 no-connect markers correctly counted for FPGA I/O pins

- **Status**: new
- **Analyzer**: schematic
- **Source**: tests_integration_misc_FPGA.sch.json
- **Created**: 2026-03-24

### Correct
- FPGA.sch references three sub-sheets (FPGA_PWR.sch, FPGA_CFG.sch, FPGA_IO.sch). The analyzer correctly parses all 4 sheets and reports 54 total components, with accurate component type breakdown (4 ICs, 32 capacitors, 1 diode, 7 resistors, 5 jumpers, 2 resistor networks, 3 switches).
- The FPGA schematic has 84 no-connect markers on unused I/O pins, which is typical for FPGA designs. The analyzer correctly reports total_no_connects=84.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001655: BOM values with embedded quotes preserved verbatim from source

- **Status**: new
- **Analyzer**: schematic
- **Source**: tests_integration_kicad6_hierarchical_schematic.kicad_sch.json
- **Created**: 2026-03-24

### Correct
- The kicad6 hierarchical schematic has per-instance value overrides stored with literal quote characters in the KiCad file (e.g., '"2"', '"10"', '"11"'). The analyzer correctly preserves these verbatim. This is not a bug — it is an artifact of how the test data was originally created with KiField tool overrides that embed quote characters.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001656: KiCad 7 hierarchical schematic correctly resolved to 11 components

- **Status**: new
- **Analyzer**: schematic
- **Source**: tests_integration_kicad7_hierarchical_schematic.kicad_sch.json
- **Created**: 2026-03-24

### Correct
- The kicad7 hierarchical schematic references two leaf sheets, each instantiated twice. The analyzer correctly aggregates all instances and reports 11 total components (6 resistors, 3 inductors, 2 capacitors).

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001657: Hierarchical KiCad 5 schematic correctly traverses sub-sheet to find single crystal

- **Status**: new
- **Analyzer**: schematic
- **Source**: hier_test.sch.json
- **Created**: 2026-03-24

### Correct
- hier_test.sch references leaf.sch which contains a single crystal (Y2). The analyzer correctly parses 2 sheets and reports 1 total component of type 'crystal'.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001658: Deep 3-level KiCad 5 hierarchy correctly parsed (4 sheets, 5 components)

- **Status**: new
- **Analyzer**: schematic
- **Source**: hier_test2.sch.json
- **Created**: 2026-03-24

### Correct
- hier_test2.sch references sheet_dir/leaf.sch, sheet_dir/file5C5DA9F0.sch (which references subsheet_dir/file5C5DAE86.sch). All 4 sheets are parsed, yielding 5 components (C1, D1, D2, U1, U2).

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001659: Non-ASCII Unicode component value (2.0 KΩ) correctly parsed

- **Status**: new
- **Analyzer**: schematic
- **Source**: tests_integration_misc_resistor_nonascii.sch.json
- **Created**: 2026-03-24

### Correct
- The resistor R1 has value '2.0 KΩ' containing a Unicode Ohm sign (U+03A9). The analyzer correctly parses and stores this as '2.0 K\u03a9', demonstrating proper UTF-8 handling for non-ASCII component values.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001660: Rgb7Hat multi-sheet schematic correctly parsed (includes RPi_GPIO sub-sheet)

- **Status**: new
- **Analyzer**: schematic
- **Source**: tests_integration_misc_Rgb7Hat.sch.json
- **Created**: 2026-03-24

### Correct
- Rgb7Hat.sch references RPi_GPIO.sch as a sub-sheet. The analyzer parses both sheets and correctly reports 25 total components including fiducials, connectors, ICs, capacitors, resistors, transistors, test points, and a fuse.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001661: NPTH mounting holes (H1-H4) misclassified as 'smd' type; Correct total footprint count (18) including mounting holes; Correct copper layer usage: 3 of 4 defined copper layers (F.Cu, In2.Cu, B.Cu); ...

- **Status**: promoted
- **Analyzer**: pcb
- **Source**: tests_integration_misc_integration.kicad_pcb.json
- **Created**: 2026-03-24

### Correct
- The integration PCB has exactly 18 footprints: J3, J6, J9, U2, Q1, Q2, R6, R7, R8, R9, R11, R23, R24, R29, H1, H2, H3, H4. The analyzer reports footprint_count=18, which is correct.
- The board defines 4 copper layers (F.Cu, In1.Cu, In2.Cu, B.Cu) but only 3 carry actual content (tracks or zones). In1.Cu appears only in the layer definition with no tracks or zones. The analyzer correctly reports copper_layers_used=3.
- The integration PCB has three courtyard overlaps: J6 vs Q2 (1.152mm²), J6 vs R24 (0.16mm²), and Q1 vs Q2 (0.157mm²). These are real overlaps in the densely packed board, correctly identified by the placement analysis.
- J3 is a 40-pin socket on the back copper layer that extends significantly beyond the board edge (edge_clearance_mm=-41.63mm). The analyzer correctly identifies this as an edge clearance warning. The extreme negative value reflects that the connector footprint's courtyard was designed to extend off-board.
- The integration PCB has GND pour zones on F.Cu and In2.Cu. The analyzer correctly identifies both as filled zones with fill_ratio of 0.594 and 0.629 respectively, and shows GND domain connecting 6 components.
- The board has 62 track segments and 0 unrouted connections. The analyzer correctly reports routing_complete=true, unrouted_net_count=0, and track_segments=62. Track widths range from 0.15mm to 1.0mm.

### Incorrect
- The four 3mm mounting holes (H1-H4) use pad type 'np_thru_hole' in the PCB file, making them non-plated through holes (NPTH). The analyzer classifies them as 'smd' instead, inflating smd_count to 15 (should be 11) and not accounting for the 4 NPTH footprints. tht_count=3 (J3, J6, J9) is correct.
  (statistics)

### Missed
(none)

### Suggestions
- Fix: NPTH mounting holes (H1-H4) misclassified as 'smd' type

---

## FND-00001662: Empty stub PCB file correctly parsed with zero footprints and zero nets

- **Status**: new
- **Analyzer**: pcb
- **Source**: tests_integration_kicad7_random_circuit.kicad_pcb.json
- **Created**: 2026-03-24

### Correct
- random_circuit.kicad_pcb is a minimal stub file containing only '(kicad_pcb (version 20221018) (generator pcbnew))'. The analyzer correctly reports 0 footprints, 0 tracks, 0 nets, and routing_complete=true (vacuously true for an empty board).

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001663: KiCad 5 stub PCB ('dummy file') correctly parsed as empty board

- **Status**: new
- **Analyzer**: pcb
- **Source**: hier_test2.kicad_pcb.json
- **Created**: 2026-03-24

### Correct
- hier_test2.kicad_pcb contains only '(kicad_pcb (version 4) (host kicad "dummy file"))'. The analyzer correctly handles this as an empty board with 0 footprints, 0 tracks, file_version=4, and no errors.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001664: cap_grouping.sch correctly identifies 6 capacitors with MPN data

- **Status**: new
- **Analyzer**: schematic
- **Source**: tests_integration_misc_cap_grouping.sch.json
- **Created**: 2026-03-24

### Correct
- The cap_grouping.sch is a test file for KiField grouping logic with 6 capacitors (C1-C6) in two groups by value (0.6 and 0.3). All 6 have MPNs assigned (CAP123 and CAP456). The analyzer reports total_components=6, no missing_mpn, and correctly groups them in the BOM.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001665: Memory.sch correctly parsed: 1 IC + 7 capacitors with zero wires (bus-style)

- **Status**: new
- **Analyzer**: schematic
- **Source**: tests_integration_misc_Memory.sch.json
- **Created**: 2026-03-24

### Correct
- Memory.sch contains U5 (a memory IC) and 7 decoupling capacitors (C8-C14), connected via power buses with no wire segments. The analyzer correctly reports total_components=8, total_wires=0, and total_no_connects=1.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
