# Findings: ubertooth / ubertooth-one

## FND-00000073: Legacy net resolver assigns pins to wrong nets: CC2591 RF_P/AVDD pins on GND, LPC1758 GPIO/XTAL pins on 3V3D. 71/143 nets are single-pin orphans (50%).

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: hardware_ubertooth-one_ubertooth-one.sch.json
- **Related**: KH-015, KH-016
- **Created**: 2026-03-13

### Correct
- 89 components correctly extracted from 170 $Comp blocks (81 power symbols excluded). All types, values, footprints correct.
- All types correct: 35 caps, 19 resistors, 14 connectors, 6 LEDs, 5 ICs, 5 ferrite beads, 3 inductors, 1 transistor, 1 crystal
- 6 rails correctly identified: 1V8, 3V3, 3V3D, GND, VBUS, VDDA
- L3 correctly flagged as DNP (value=DNP)

### Incorrect
- GND net contains wrong pins: J1.VBUS, U1.AVDD_PA1, U1.RF_P, U4.P1[30]/VBUS, U3.AVDD_RF1, U3.RF_N. Power and RF signal pins incorrectly assigned to GND.
  (nets)
- 3V3D net contains 5 wrong LPC1758 GPIO pins (P0[11], P0[6], P1[4], P0[18], P1[20]) and U4.XTAL1 (should connect to crystal X1).
  (nets)
- 71 of 143 nets (50%) are single-pin orphans (__unnamed_*). Wire-to-pin connectivity resolution fails on half the connections.
  (nets)
- All MPNs empty despite source having extensive MPN data in Field2 (F5) entries. CC2400-RTB1, CC2591RGVR, TPS71219DRCT, ABMM2-16.000MHZ-E2-T all present in source but not extracted.
  (bom)
- 9 CONN_1 test pad components (P5-P13) have pins=[] - parser fails to extract pins from single-pin connectors.
  (components)

### Missed
(none)

### Suggestions
- Fix KH-016: wire-to-pin connectivity resolver assigns pins to wrong power nets instead of tracing wires correctly.
- Add custom field mapping for legacy .sch: F4->manufacturer, F5->MPN, F6->description.
- Fix CONN_1 single-pin connector extraction.
- Fix KH-015: add signal_analysis to legacy parser path.

---
