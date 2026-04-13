# Findings: Bastardkb/Dilemma / 3x5_2_dilemma

## FND-00000470: Key matrix row_nets and col_nets fields are swapped; PSW1 (SW_DPDT) power switch misclassified as 'connector' instead of 'switch'; Voltage divider on 'hand' net correctly detected (R7 5.1k / R1 5.1...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: 3x5_2_dilemma.kicad_sch.json
- **Created**: 2026-03-23

### Correct
- The hand-detection circuit uses R7 (5.1k, pin 1 to +5VL) and R1 (5.1k, pin 2 to GND) to create a 0.5 ratio voltage divider on the 'hand' net, connected to U2 pin F4 (GPIO). The analyzer correctly identifies this in signal_analysis.voltage_dividers with top_net='+5VL', mid_net='hand', bottom_net='GND', ratio=0.5, and mid_point_connections listing U2 pin 20 (F4).
- The analyzer correctly identifies I2C bus activity: scl_l net pulled up via R4 (4.7k to +5VL) and sda_l net pulled up via R3 (4.7k to +5VL), both driven from U2 (eliteC). The pull-up analysis correctly reports ohms=4700.0 and to_rail='+5VL' for both lines.
- The analyzer correctly identifies a full-duplex SPI bus (bus_id='L') driven from U2 with signals on mosi_l, miso_l nets. The chip select count of 1 and bus mode 'full_duplex' are consistent with the trackball connector J7 as the SPI peripheral.
- The analyzer correctly reports estimated_keys=17, switches_on_matrix=17, diodes_on_matrix=17. The 3x5_2 single-half design has 3 finger columns (5 keys each) + 2 thumb columns (1 key each) = 17 total. The matrix topology detection via diode-switch pairing is accurate. The only error is that the row_nets and col_nets labels are swapped (covered separately).

### Incorrect
- The analyzer reports row_nets=['col1_l','col2_l','col3_l','col4_l','col5_l'] and col_nets=['row1_l','row2_l','row3_l','row4_l']. Inspection of the nets shows col1_l through col5_l carry diode K (cathode) pins — these are the column scan lines in keyboard terminology. The row1_l through row4_l nets carry switch pin 1 connections — these are the row scan lines. The field labels are inverted in the output JSON. As a consequence the matrix dimensions are also reported as 5 rows x 4 cols when the correct physical topology is 5 cols x 4 rows (matching the '3x5' in the repo name: 3 finger columns + 2 thumb keys = 5 cols, 4 rows per half).
  (signal_analysis)
- PSW1 has value='SW_DPDT_x2', lib_id='jiran-ble:SW_DPDT', footprint 'Switch_MSK-12C01-07'. It is a double-pole double-throw power switch used to switch the battery rail (bat_sw_l net) to the MCU. The analyzer assigns type='connector' (and subcircuit neighbor type='connector') because the symbol comes from a custom library ('jiran-ble:') that is not recognized as a switch. It should be type='switch'. This also means the switch count (19 total) is reported correctly but the 'switch' category count in component_types is 19 — PSW1 is among the missing 19 switches but it is listed separately as a 'connector' in statistics, so the raw count is still off by one from what the bill-of-materials implies.
  (signal_analysis)
- The file header contains '(version 20211123)' which corresponds to KiCad 6.0 (released November 2021). The analyzer outputs kicad_version='unknown' instead of '6.0'. By contrast, file_version=20250114 is correctly mapped to kicad_version='9.0' in the 3x5_3_procyon and 4x6_4 outputs. This version gap affects the 3x5_2 (20211123 = KiCad 6) and 3x5_3 (20230121 = KiCad 7) schematics.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00000471: Key matrix detected as 38x10 instead of correct 10 cols x 4 rows (combined both halves); SK6805-EC15 addressable RGB LEDs misclassified as 'diode' type; Addressable LED chains for all 36 SK6805-EC1...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: 3x5_3_dilemma.kicad_sch.json
- **Created**: 2026-03-23

### Correct
- The RP2040 (U1) power domain analysis correctly identifies three rails: +3.3V (I/O supply), +1V1 (internal VREG output), and VBUS_DET (USB detection). The XC6210B332MR-G LDO (U3) is correctly shown supplying +3.3V from +5V. This matches the RP2040 hardware design guide architecture where VREG outputs 1.1V core supply.
- Y1 and Y5001 (Crystal_GND24) are each correctly paired with two 15pF load capacitors (C3/C4 for Y1, C5005/C5008 for Y5001). The effective load capacitance is correctly computed as 10.5pF (series combination 15*15/(15+15) + ~3pF stray). Frequency is null because the Crystal_GND24 symbol does not expose frequency as a parseable property — this is a correct absence rather than an error.
- All four USBLC6-2P6 ESD arrays are detected (U4 on D+/D-, U5003 on D+_L/D-_L, U5005 on SERIAL, U5006 on SERIAL_L) and both Polyfuse parts (F1, F5001) are detected as protection devices. The detection method and protected nets are accurate.

### Incorrect
- The 3x5_3 is a dual-half split keyboard. The true key matrix has 5 column nets per half (M_COL1..M_COL5 and M_COL1_L..M_COL5_L = 10 total) and 4 row nets per half (M_ROW1..M_ROW4 and M_ROW1_L..M_ROW4_L = 8 total), giving 40 key positions. Instead the analyzer reports row_nets with 38 entries (4 named M_COL4/5 nets, 2 encoder_diode nets, and 32 unnamed anode-intermediate nets) and col_nets with 10 entries (8 M_ROW nets plus '~{RESET_L}' and '~{RESET}'). Three causes: (1) the D_CC dual-cathode diode topology means each column net has only 2 diode K pins instead of 4 per standard single-diode matrix, so M_COL1/2/3 are not recognized as column lines; (2) the 32 unnamed nets connecting D_CC anodes (A1/A2) to switch pins are incorrectly included as 'row' lines; (3) two RESET lines are incorrectly included as matrix column lines. The estimated_keys=40 count happens to be correct despite the wrong topology.
  (signal_analysis)
- The 3x5_3 schematic contains 36 SK6805-EC15 addressable RGB LEDs (lib_id='sk6805-ec15:SK6805-EC15'). The analyzer classifies them as type='diode' because the custom library prefix 'sk6805-ec15:' is not recognized, causing the component to fall through to diode detection. These are single-wire protocol (WS2812-compatible) addressable LEDs with pins DIN/DOUT/VDD/GND — functionally identical to the SK6812MINI parts in the same schematic, which are correctly classified as type='led' (lib_id='LED:SK6812MINI'). The 36 SK6805-EC15 parts inflate the diode count from the correct 22 matrix+protection diodes to 58 total.
  (signal_analysis)
- File header version '20230121' maps to KiCad 7.0 (released January 2023). The analyzer outputs kicad_version='unknown'. The version mapping gap covers at least file_version 20211123 (KiCad 6) and 20230121 (KiCad 7); KiCad 9 (20250114) is correctly mapped.
  (signal_analysis)

### Missed
- The 3x5_3 contains 36 SK6805-EC15 addressable RGB LEDs arranged in two chains of 18 (one per keyboard half), driven from separate GPIO pins. Despite each SK6805-EC15 having DIN and DOUT pins and forming a clear daisy-chain topology, the addressable_led_chains detector finds only the two SK6812MINI chains (18 each). All 36 SK6805-EC15 refs (e.g. D19, D5017 through D5030) appear in no detected chain. The root cause is the type='diode' misclassification: the chain detector only traverses components classified as type='led'. The missing chains have data_in pins on nets connected to RP2040 GPIO, distinct from the SK6812MINI chain signals.
  (signal_analysis)
- The SERIAL net connects U1:GPIO1 (RP2040 TX) through USBLC6-2P6 ESD protection (U5005) to AudioJack4 connector J102. The SERIAL_L mirror connects U5002:GPIO1 through U5006 to J5003. This is a UART-over-TRRS half-duplex serial link for QMK/ZMK split-keyboard communication. The design_analysis.bus_analysis.uart array is empty. The UART detector does not match this topology because the RP2040 symbol uses generic pin names 'GPIO1' rather than 'TX'/'RX', so the pin-name heuristic fails. The same issue applies identically to 4x6_4.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00000472: Key matrix detected as 38x12 instead of correct 10 cols x 4 rows; same D_CC and RESET issues as 3x5_3; 36 SK6805-EC15 addressable LEDs misclassified as 'diode' and their chains missed

- **Status**: new
- **Analyzer**: schematic
- **Source**: 3x5_3_procyon_dilemma.kicad_sch.json
- **Created**: 2026-03-23

### Correct
(none)

### Incorrect
- 3x5_3_procyon is a variant of 3x5_3 with the same dual-half RP2040 layout and D_CC dual-cathode matrix diodes. The analyzer reports 38 row_nets x 12 col_nets (including '~{RESET_L}', '~{RESET}', and two unnamed intermediary nets in col_nets alongside the 8 M_ROW nets). The root cause is identical to 3x5_3: D_CC topology breaks the column-net detection causing M_COL1/2/3 to be missed and 32+ unnamed anode-intermediate nets to be included as rows. estimated_keys=40 is still correct.
  (signal_analysis)
- Same issue as 3x5_3: all 36 SK6805-EC15 (lib_id='sk6805-ec15:SK6805-EC15') are typed 'diode' and none appear in the addressable_led_chains output. Only the 18 SK6812MINI per half (36 total, detected in two chains of 18 each) are correctly identified. The 3x5_3_procyon uses the identical LED arrangement as 3x5_3.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00000473: Key matrix reported as 14x12 instead of correct 12 cols x 5 rows (combined both halves); 48 SK6805-EC15 addressable LEDs misclassified as 'diode'; their two LED chains of 24 each are missed; Test p...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: 4x6_4_dilemma.kicad_sch.json
- **Created**: 2026-03-23

### Correct
- 12 test points (J5016-J5027 region, Conn_01x01_Socket) are correctly classified as type='test_point' and appear in test_coverage with covered_nets listing M_COL1, M_COL1_L, M_COL2, M_COL2_L, M_COL3, etc. This is accurate: the test pads are placed on key matrix column lines.
- Four I2C bus entries are correctly detected: SDA/SCL for U1 (right half RP2040) with R103/R104 (4.7k to +3.3V), and SDA_L/SCL_L for U5002 (left half RP2040) with R5013/R5014 (4.7k to +3V3_L). All pull-up values, rail associations, and devices are accurate.

### Incorrect
- The 4x6_4 is a 4-row x 6-col per half split keyboard (combined: 10 row nets x 12 col nets = 60 key positions). The analyzer reports row_nets with 14 entries (12 M_COL nets + 2 unnamed) and col_nets with 12 entries (10 M_ROW nets + '~{RESET_L}' + '~{RESET}'). Two issues: (1) the RESET lines are incorrectly included as key matrix column lines; (2) the row_nets/col_nets field labels are swapped relative to keyboard convention. The estimated_keys=60 count is correct. switches_on_matrix=60 is correct (56 key switches + 4 encoder switches, excluding the 2 SW_SPST reset switches which are correctly excluded here, unlike 3x5_3).
  (signal_analysis)
- The 4x6_4 contains 48 SK6805-EC15 (lib_id='sk6805-ec15:SK6805-EC15') classified as type='diode'. None of the 48 refs appear in the addressable_led_chains output. Only the 56 SK6812MINI (type='led', lib_id='LED:SK6812MINI') are detected, forming two chains of 28 each. The SK6805-EC15 form a separate 24-per-half daisy chain with DIN/DOUT pins connected through named nets — the missed chains have an estimated current draw of approximately 24 * 60mA = 1440mA per half at full brightness, a significant omission from the power budget.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---
