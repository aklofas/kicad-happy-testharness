# Findings: KLOTZ / PCB_Klotz

## FND-00000612: LEDs (L1, L2, L3) misclassified as 'inductor' type instead of 'led'; False positive I2C bus detection on LED signal nets; assembly_complexity reports all 55 components as SMD with tht_count=0, cont...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: PCB_Klotz.kicad_sch.json
- **Created**: 2026-03-23

### Correct
- The key_matrices detector correctly identifies the 4x5 matrix with row0-row3 and col0-col4 nets, 17 key switches and 17 flyback diodes. The encoder (SW18) and special switches are correctly excluded from the matrix count.
- The design uses a battery-powered nice!nano with no explicit PWR_FLAG symbols on GND and VCC. The pwr_flag_warnings correctly flags both rails as ERC issues.
- design_observations correctly notes U1's RST pin on the RESET net, connected to RSW1 (reset switch), with has_pullup=false. The nice!nano has internal pull-up, so this is an accurate structural observation.

### Incorrect
- Components L1/L2/L3 use lib_id 'Device:LED' with keywords 'LED diode', but the analyzer assigns type='inductor' and category='inductor' to all three, based on the 'L' reference prefix. The BOM also groups them under value 'LED' with type 'inductor'. This is a reference-prefix heuristic misfiring — 'L' prefix is normally inductors, but these are clearly LEDs. The type should be 'led' or at minimum 'diode'.
  (signal_analysis)
- The bus_analysis reports I2C on net 'LED1' (SCL line) and '__unnamed_22' (SDA line) because U1 (nice!nano) has pin names '3/D0/SCL' and '2/D1/SDA'. However, those GPIO pins are used here as LED PWM outputs (LED1/LED2/LED3 nets) and encoder inputs — not I2C. The I2C detection is triggering purely on pin name substrings without checking whether a real I2C device (with pull-ups and matching SCL/SDA partners) is present.
  (signal_analysis)
- The schematic assembly_complexity section shows smd_count=55, tht_count=0. The PCB analyzer correctly identifies smd_count=7, tht_count=43. The schematic analyzer is deriving assembly type from schematic footprint strings using custom KLOTZ library names (e.g. 'Kailh_socket_PG1350_optional_reversible', 'LED_3mm_reversible', 'Diode_SOD123') that it cannot resolve and defaults to treating as SMD.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00000613: Switchplate board outline reported as edge_count=0 with null bounding_box despite 100+ gr_curve Edge.Cuts elements; Switchplate DFM reports 'standard' tier with no metrics or violations despite the...

- **Status**: new
- **Analyzer**: pcb
- **Source**: switchplate_Klotz_02_Plate.kicad_pcb.json
- **Created**: 2026-03-23

### Correct
(none)

### Incorrect
- The switchplate PCB uses exclusively gr_curve (cubic bezier) elements for the complex keyboard cutout outline on Edge.Cuts — no gr_line or gr_arc elements. The PCB analyzer only collects 'line' and 'arc' type edges, completely missing gr_curve, resulting in edge_count=0 and board_outline.bounding_box=null. The gerber analyzer correctly computes board dimensions (120.5x85.48mm) from the actual gerber file, confirming a real outline exists.
  (signal_analysis)
- Because the board_outline bounding_box is null (due to the gr_curve parsing failure), the DFM analyzer cannot compute board dimensions, so dfm_tier is left as 'standard' and metrics are empty. The main PCB correctly detects this same physical size as exceeding the 100x100mm threshold and issues a board_size violation. The switchplate should show the same board_size DFM warning.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00000614: DFM correctly identifies 0.05mm annular ring (challenging tier) and oversized board; 46 nets, 56 footprints, 106 vias, full routing correctly reported for main keyboard PCB

- **Status**: new
- **Analyzer**: pcb
- **Source**: PCB_Klotz.kicad_pcb.json
- **Created**: 2026-03-23

### Correct
- The main keyboard PCB has 0.3mm via drill with 0.25mm tracks giving a 0.05mm annular ring, correctly flagged as below the advanced process minimum. The board_size violation for 120x85mm is also correct.
- Net count (46), footprint count (56), via count (106), 2-layer copper, and routing_complete=true all match what is visible in the PCB file content.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00000615: Main keyboard gerber set complete: 9 layers, 2 drill files, 373 total holes correctly parsed

- **Status**: new
- **Analyzer**: gerber
- **Source**: PCB_gerbers.json
- **Created**: 2026-03-23

### Correct
- All required layers present (F.Cu, B.Cu, F/B.Mask, F/B.Paste, F/B.SilkS, Edge.Cuts). 106 via holes (0.3mm PTH) and 199 component holes correctly classified. 104 NPTH holes include 51x3.0mm and 17x3.429mm switch cutouts (Kailh socket NPTH stabilizers) and 34x1.702mm NPTH.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00000616: Switchplate gerber reports has_pth_drill=true despite PTH drill file containing zero holes; Switchplate gerber dimensions, layer structure, and NPTH drill holes (8 holes: 5x2.2mm + 3x3.2mm) correct...

- **Status**: promoted
- **Analyzer**: gerber
- **Source**: switchplate_gerbers.json
- **Created**: 2026-03-23

### Correct
- Board dimensions 120.5x85.48mm match the physical board. The 8 NPTH mounting holes (5 M2.2 for stabilizers/spacers and 3 M3.2 mounting holes) are correctly classified. Empty F.Cu/B.Cu/F.Paste/B.Paste are correctly identified as zero-aperture files, appropriate for a non-electrical plate.

### Incorrect
- The completeness section shows has_pth_drill=true because a PTH .drl file is present, but it contains 0 holes (only an empty header). This is a false positive — a switchplate with no electrical connections legitimately has no PTH holes. The flag should reflect whether any PTH holes actually exist, not merely whether the file is present.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---
