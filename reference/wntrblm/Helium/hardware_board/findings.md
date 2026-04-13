# Findings: wntrblm/Helium / hardware_board

## FND-00000606: PWR_FLAG symbols not parsed — false pwr_flag_warnings on +12V and -12V

- **Status**: new
- **Analyzer**: schematic
- **Source**: hardware_board_power.kicad_sch.json
- **Created**: 2026-03-23

### Correct
(none)

### Incorrect
- The power subsheet contains two power:PWR_FLAG instances (#FLG0101, #FLG0102) connected to +12V and -12V, but the analyzer omits them from the component list entirely. Consequently pwr_flag_warnings fires for both +12V and -12V rails in a sheet that explicitly has PWR_FLAGs. Reproduces across all subsheets (mults, precision-adder, hubble-lens).
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00000607: Precision rectifier topology misclassified as comparator_or_open_loop

- **Status**: new
- **Analyzer**: schematic
- **Source**: hardware_board_mults.kicad_sch.json
- **Created**: 2026-03-23

### Correct
(none)

### Incorrect
- U1/U2/U4 unit 1 in the mults sheet each drive a diode bridge feedback network (diode from output to inv-input, second diode in reverse) — a classic precision half-wave rectifier. The analyzer classifies them as 'comparator_or_open_loop' because the output net and inv-input net differ, but no feedback resistor is detected. This is a missed opamp topology: precision rectifier.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00000608: Board outline (gr_poly on Edge.Cuts) not detected — board_width/height null, edge_count 0

- **Status**: new
- **Analyzer**: pcb
- **Source**: hardware_faceplate_faceplate.kicad_pcb.json
- **Created**: 2026-03-23

### Correct
(none)

### Incorrect
- The faceplate PCB defines its outline as a gr_poly on Edge.Cuts (20x128.5mm Eurorack panel). The analyzer reports edge_count=0, bounding_box=null, board_width_mm=null, board_height_mm=null. The gr_poly shape type is not being parsed for board outline extraction. A spurious 'No filled polygon data' copper warning is also emitted for a faceplate that intentionally has no copper.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00000609: Board statistics, DFM, and silkscreen analysis correct for a 2-layer Eurorack module

- **Status**: new
- **Analyzer**: pcb
- **Source**: hardware_board_board.kicad_pcb.json
- **Created**: 2026-03-23

### Correct
- 67 footprints (47 SMD, 17 THT), 2-layer, 20x108mm board detected correctly. DFM correctly flags the narrow board exceeding 100mm height. Silkscreen warnings for unlabeled connectors and polarity reminders are appropriate.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00000610: Component counts, BOM, and decoupling analysis correct for a ±12V Eurorack mult/adder

- **Status**: new
- **Analyzer**: schematic
- **Source**: hardware_board_board.kicad_sch.json
- **Created**: 2026-03-23

### Correct
- 64 components (17 connectors, 20 resistors, 8 LEDs, 4 ICs, 11 caps, 2 diodes, 2 ferrite beads) correctly identified. ±12V decoupling (10.4µF each rail, 5 caps each) correctly extracted. Opamp buffer units correctly classified for the majority of units.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00000611: Breakout/expander schematic stats and missing MPN detection correct

- **Status**: new
- **Analyzer**: schematic
- **Source**: hardware_hubble-lens_hubble-lens.kicad_sch.json
- **Created**: 2026-03-23

### Correct
- 27 components (20 connectors, 3 ICs, 4 mounting holes) with 6 missing MPNs (BB1-3, U1-3) correctly flagged. Multiple power rails (+12V, -12V, +3.3V, +12VDOWNSTREAM, GND) correctly detected. Decoupling warnings for MUX508 ICs without bypass caps are valid.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
