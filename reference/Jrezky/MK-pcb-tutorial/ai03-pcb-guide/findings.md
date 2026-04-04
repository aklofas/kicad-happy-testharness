# Findings: MK-pcb-tutorial / ai03-pcb-guide

## FND-00000853: Reset button SW1 counted as a key matrix switch (switches_on_matrix=5, should be 4); Crystal oscillator circuit (16MHz) with 22pF load caps and effective CL=14pF correctly detected; USB full-speed ...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: ai03-pcb-guide.sch.json
- **Created**: 2026-03-23

### Correct
- Y1/C3/C4 crystal circuit and load capacitance calculation is correct. Decoupling on +5V with 4 caps also correctly identified.

### Incorrect
- The key matrix is 2x2 (ROW0/ROW1, COL0/COL1) with 4 MX switches. SW1 is a tactile reset switch connected to GND and Net-(R3-Pad2), not to any row/col matrix nets. The analyzer reports switches_on_matrix=5 by counting all 5 switch-type components regardless of matrix connectivity. Only MX1-MX4 belong to the matrix.
  (signal_analysis)

### Missed
- The design has an ATmega32U4 USB controller with D+/D- global labels, USB1 connector, and R1/R2 (22-ohm) USB series resistors. The bus_analysis section reports no USB interfaces and differential_pairs is empty. These are textbook USB FS termination resistors that should be recognized.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00000854: KEYSW keyboard switches misclassified as 'relay' type; switches_on_matrix=0 when 31 switches are present; 5x7 key matrix topology detected correctly (5 rows, 7 cols, 31 diodes) via net-name heuristic

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: keyboard-layout-pcb_keyboard-layout.sch.json
- **Created**: 2026-03-23

### Correct
- Row/col net naming (row0-row4, col0-col6) is properly detected. estimated_keys=31 matches the 31 diodes present.

### Incorrect
- All 31 K_ components (lib_id keyboard_parts:KEYSW) are typed as 'relay' in statistics and component output. None are recognized as 'switch'. Additionally, switches_on_matrix=0 while the matrix has 31 keys — the analyzer detects the 31 diodes via net-name heuristic but completely misses the co-located switch components.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00000855: diodes_on_matrix=41 overcounts actual 32 diodes; estimated_keys=41 exceeds matrix capacity of 20 (5x4); SK6812mini LEDs (U7-chain, U27-chain) show data_in_net='VCC' instead of the actual GPIO data ...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: helix-master_PCB_beta_helix.sch.json
- **Created**: 2026-03-23

### Correct
- All 32 LEDs are distributed across 5 chains (6+6+6+7+7). Chain lengths and component membership are accurate. Protocol identified correctly as WS2812-compatible.

### Incorrect
- The schematic has 32 diode components. The 5x4 matrix yields a maximum of 20 key positions per half. However the analyzer reports diodes_on_matrix=41 (9 more than actual diode count) and estimated_keys=41. This appears to be a double-counting artifact where the net-name traversal counts diodes on both sides of the matrix signal path. switches_on_matrix=26 is plausible but the estimated_keys figure is clearly wrong.
  (signal_analysis)
- Two of five LED chains report data_in_net='VCC'. VCC is a power rail, not a data line. The first LED in each chain should receive its DIN from a GPIO pin of the ProMicro (likely the 'LED' net seen in single_pin_nets). This is a net-traversal error where the chain origin is misidentified.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00000856: PCB layout analysis correct: 2-layer, 24 footprints, DFM standard, courtyard overlap U1/C1 detected; USB1 edge_clearance reported as -3.85mm (negative) — connector intentionally overhangs board edge

- **Status**: promoted
- **Analyzer**: pcb
- **Source**: ai03-pcb-guide.kicad_pcb.json
- **Created**: 2026-03-23

### Correct
- Board dimensions (77.8x38.1mm), component counts, routing complete, Power net class (0.381mm trace width), decoupling placement for U1 at ~10mm, and DFM tier all look accurate.

### Incorrect
- The Molex USB connector (USB1) is designed to mount at the board edge with an overhang. The -3.85mm edge clearance warning is technically a true measurement but will be a systematic false positive for any edge-mount USB connector. This pattern recurs across keyboard designs and needs context-aware suppression.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00000857: DFM violation for annular ring (0.1mm, advanced tier) and board size >100mm correctly flagged; missing_switch_labels silkscreen warning fires for all 33 keyboard switches — this is a false positive...

- **Status**: promoted
- **Analyzer**: pcb
- **Source**: helix-master_PCB_beta_helix.kicad_pcb.json
- **Created**: 2026-03-23

### Correct
- Both violations are real constraints for JLCPCB. The 132x94mm board does cost more and the 0.1mm annular ring requires advanced fab.

### Incorrect
- The analyzer flags every SW* component as needing a function label on silkscreen. For a keyboard PCB, key switches are intentionally unlabeled (key legends are on keycaps, not PCB silkscreen). The warning should be suppressed for components recognized as keyboard matrix switches.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00000858: Gerber completeness check correct: 7 layers found, F.Paste missing (expected for THT keyboard), 2 drill files

- **Status**: new
- **Analyzer**: gerber
- **Source**: helix-master_PCB_beta_gerber_.json
- **Created**: 2026-03-23

### Correct
- Layer set is appropriate for a THT/SMD mixed keyboard. F.Paste is flagged as missing_recommended but the SMD components are LEDs and the ProMicro module — missing paste is a minor concern. Layer alignment is verified as aligned.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
