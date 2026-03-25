# Findings: Mechanical-Keyboard / A10L9

## FND-00000881: Eagle-import key switches misclassified by single-letter reference: 27 of 82 KEYSWITCH-PLAIN-MX-1U components get wrong types (crystal, varistor, fuse, connector, ic, transistor, etc.); False posit...

- **Status**: new
- **Analyzer**: schematic
- **Source**: A10L9.kicad_sch.json
- **Created**: 2026-03-23

### Correct
- statistics shows 88 diodes, 195 total components. MCU (ATMEGA32U4-QFN44) correctly typed as IC. Decoupling analysis correctly finds 5x 0.1uF caps on VCC. D+ and D- nets present in nets list. Bus analysis correctly shows no SPI/I2C (Eagle import lacks named bus nets).

### Incorrect
- The Eagle-imported schematic uses bare letter references (Y, V, F8, J, A, U, X, etc.) for key switches. The classifier maps Y→crystal, V→varistor, F*→fuse, J→connector, A/U→ic, Q→transistor, etc. by reference prefix heuristics, ignoring the lib_id 'KEYSWITCH-PLAIN-MX-1U'. 55 correctly classified as switch, 27 misclassified. Downstream effects: false varistor in protection_devices, false crystal in crystal_circuits.
  (signal_analysis)
- signal_analysis.crystal_circuits contains one entry with reference='Y', value='KEYSWITCH-PLAIN-MX-1U' because the ref heuristic matches 'Y' to crystal/oscillator. This is a key switch, not a crystal.
  (signal_analysis)
- signal_analysis.protection_devices contains one entry with ref='V', type='varistor' because ref 'V' triggers varistor classification. The component is a key switch.
  (signal_analysis)

### Missed
- The keyboard has row nets R0-R5 and column nets C0-C17. The key matrix detector only matches 'row'/'col' prefix naming, not the 'R'/'C' single-letter prefix style used here. signal_analysis.key_matrices is empty. The Matrix.kicad_sch subsheet (sister design) correctly detects the matrix via 'row0-row5'/'col0-col13' nets; A10L9 uses the same matrix but named R0-R5/C0-C17.
  (signal_analysis)
- The design has a USB-C connector (lib_id='A10L9-eagle-import:USB-C'), D+ and D- nets, and a ZEN056V130A16YM TVS (U1) for protection. The USB compliance analyzer was not triggered, likely because the Eagle-imported lib_id does not match KiCad standard library patterns for USB connectors.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00000882: PCB correctly analyzed: 195 footprints, 2-layer 347x115mm board, fully routed, DFM board-size warning

- **Status**: new
- **Analyzer**: pcb
- **Source**: A10L9.kicad_pcb.json
- **Created**: 2026-03-23

### Correct
- statistics: 195 footprints, 1063 track segments, 35 vias, routing_complete=true, 0 unrouted nets. DFM correctly flags oversized board (347x115mm > 100x100mm JLCPCB threshold). Thermal pad correctly identified for MCU (TAB, 5.08x5.08mm, GND net, 1 thermal via). Edge clearance warning for U$1 (-2.67mm) is accurate for a USB connector near board edge.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
