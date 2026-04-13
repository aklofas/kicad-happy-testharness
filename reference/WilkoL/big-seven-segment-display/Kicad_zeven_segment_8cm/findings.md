# Findings: WilkoL/big-seven-segment-display / Kicad_zeven_segment_8cm

## FND-00001991: Component counts and types correct: 42 total, 28 J5630 segments, 2 ICs, 5 resistors, 2 caps, 2 connectors, 3 mounting holes; 6V5 power input rail classified as 'signal' instead of 'power', causing ...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: zeven_segment_8cm.sch
- **Created**: 2026-03-24

### Correct
- The analyzer correctly counts 42 components (28 J5630 7-segment LED display segments classified as diode, 2 ICs, 5 resistors, 2 caps, 2 connectors, 3 mounting holes). The STP16CP05 LED shift register (U1) and APE8865N-33-HF-3 LDO (U2) are correctly identified. The LDO output rail (+3.3V) and topology (LDO) are correct.
- The APE8865N-33-HF-3 SOT-23 LDO is correctly detected as a linear regulator with topology='LDO', input_rail='6V5', output_rail='+3.3V', estimated_vout=3.3V via fixed_suffix detection. The design observation also correctly flags missing input decoupling.

### Incorrect
- The 6V5 net is the input voltage supply to the APE8865N-33-HF-3 LDO regulator. Because 6V5 is unnamed in KiCad's standard power library and uses a numeric voltage name, the analyzer classifies it as 'signal' rather than 'power'. This causes C1 (100nF on the 6V5 rail) to be omitted from decoupling_analysis. Only C2 (on +3.3V) appears. The regulator observation correctly flags 'missing_caps: {input: 6V5}' which partially compensates, but the decoupling_analysis is incomplete.
  (signal_analysis)
- The STP16CP05 LED shift register has R1 (1k) in series with its SDI input, and R2–R5 (100k each) as pull resistors on SPI signal lines at J1/J2. The analyzer detects three 'voltage dividers': R1/R5, R3/R5, and R2/R4. These are SPI termination/level-conditioning resistors, not DC bias dividers. The mid-points all connect to signal pins (SDI, J1/J2 connector) rather than high-impedance sensing nodes, confirming the false positive. The R2/R4 pair (50% ratio) connecting J1 pins is particularly weak as a divider candidate.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001992: PCB correctly reports 43 footprints, 2-layer board, full routing, and dual copper pour zones (GND on B.Cu, 6V5 on F.Cu); Edge clearance warnings correctly flagged for J1 and J2 connectors designed ...

- **Status**: new
- **Analyzer**: pcb
- **Source**: zeven_segment_8cm.kicad_pcb
- **Created**: 2026-03-24

### Correct
- The 43 footprint count (42 front + 1 back logo) is correct. The board dimensions 50mm x 100mm are correct. Both copper pours are detected: GND zone on B.Cu (filled) and /6V5 zone on F.Cu (filled). Routing is complete with 24 vias. The back-side component is correctly identified as the decorative logo footprint.
- J1 shows -6.25mm clearance and J2 shows -0.1mm clearance. Horizontal connectors (PinHeader_1x06 Horizontal and PinSocket_1x06 Horizontal) are intentionally mounted at the board edge so negative clearance is expected and correct to flag. H3 mounting hole at 0.15mm is also correctly flagged as tight.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
