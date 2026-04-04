# Findings: QSFP_Breakout / QSFP_Breakout

## FND-00001125: U1 (QSFP_Conn) classified as 'ic' type instead of 'connector'; 8 differential pairs (TX1-4, RX1-4) correctly detected with ESD protection noted; TPS562201 switching regulator correctly detected wit...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: QSFP_Breakout.kicad_sch.json
- **Created**: 2026-03-23

### Correct
- All 8 QSFP differential pairs (TX1_P/N, TX2_P/N, TX3_P/N, TX4_P/N, RX1_P/N, RX2_P/N, RX3_P/N, RX4_P/N) are correctly identified with has_esd=True referencing U1 (SRV05-4 equivalent). Pair naming matches the U.FL connector net names exactly.
- U2 (TPS562201) identified as switching topology with input=+12V, output=+3V3, R1=33k2/R2=10k feedback divider, estimated Vout=2.592V (close to 3.3V with Vref=0.6V). C9 DNP compensation cap on FB net correctly noted in mid_point_connections.

### Incorrect
- U1 has lib_id='QSFP:QSFP_Conn' and footprint='QSFP:QSFP_Conn_w_Cage', clearly a connector. It is typed as 'ic' in both the component entry and component_types statistics (3 ICs). The correct breakdown should be: connector=20 (19 U.FL + 1 QSFP), ic=2 (TPS562201 + PCA9554A). The misclassification propagates to differential pair detection which correctly attributes pairs to U1 but labels it as an IC.
  (signal_analysis)
- The warnings report nets like 'ModPrsL', 'RX3_N', 'TX4_P', 'IntL' having both 'input' and 'output' label shapes. In QSFP breakout designs, the same signal net has both input-direction labels (from the QSFP connector side) and output-direction labels (to the U.FL connector side). This bidirectional use of directional labels is intentional in breakout PCBs. The warnings are not actionable design issues.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001126: 4-layer stackup, board size, GND zone stitching, and routing all correctly reported; 2 courtyard overlaps between R5/J2 and R4/J2 may be false positives for edge-mount connectors

- **Status**: promoted
- **Analyzer**: pcb
- **Source**: QSFP_Breakout.kicad_pcb.json
- **Created**: 2026-03-23

### Correct
- 4-layer board (F.Cu/In1.Cu/In2.Cu/B.Cu), 70x47.5mm, 54 footprints, 46 nets, fully routed. 234 GND vias with 7.2/cm² density. Stackup correctly parsed with prepreg/core thicknesses. All footprints on F.Cu (front-only). DFM: 0 violations, min track 0.2329mm.

### Incorrect
- R5 and R4 overlap with J2 (IO_EXP PinSocket_2x05 connector) by 3.37mm² and 1.87mm² respectively. Also J2 and J3 have negative edge_clearance_mm=-4.38mm, suggesting they are edge-mount or deliberately placed near the board edge. The courtyard overlap may be a real DFM concern, but could also be a footprint library courtyard definition issue for the 2x5 pin socket.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---
