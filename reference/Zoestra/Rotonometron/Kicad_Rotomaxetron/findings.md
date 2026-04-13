# Findings: Zoestra/Rotonometron / Kicad_Rotomaxetron

## FND-00001217: RP1 (RP2040+ dev board) classified as 'resistor' due to 'RP' reference prefix heuristic

- **Status**: new
- **Analyzer**: schematic
- **Source**: Rotomaxetron.kicad_sch
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
- lib_id is 'Custom:RP2040+', value is 'RP2040+'. The analyzer apparently mapped the 'RP' prefix to resistor (resistor pack convention). Should be 'ic' or 'mcu'. Also PWR_FLAG warnings fire on GND/+5V for this handwired board — likely false positives for a board using a dev board as power source.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001218: Key matrix with 44 switches not detected; also Antenna_Dipole misclassified as 'ic'

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: Kicad_Rotonometron_PCB_Rotonometron_PCB.kicad_sch
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
(none)

### Missed
- Board has 44 switches routed via PCA9506BS I2C I/O expanders (not a direct row/col net pattern), so key_matrices=[] is understandable — but worth noting. Separately, 'Antenna_Dipole' (ref AE1) is typed as 'ic' instead of 'connector' or 'other'. The addressable LED chain (31x SK6812) is correctly detected.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00001219: Component classification, power rail detection, and statistics look accurate

- **Status**: new
- **Analyzer**: schematic
- **Source**: Kicad_Rotonometron_PCB_rev2_Rotonometron_V2_Rotonometron_V2.kicad_sch
- **Created**: 2026-03-24

### Correct
- 111 components correctly parsed with proper type breakdown (switches, LEDs, resistor_network, ICs). Power rails +5V/GND detected. Missing MPN list is complete. The resistor_network type for RA* refs is correct.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001220: Handwired board correctly shows 0 tracks/nets/copper layers despite 61 footprints

- **Status**: new
- **Analyzer**: pcb
- **Source**: Rotomaxetron.kicad_pcb
- **Created**: 2026-03-24

### Correct
- Rotomaxetron is explicitly a handwired keyboard (title: 'RotoMaxetron Handwired'). PCB file is used only for footprint placement/reference, not routing. analyzer correctly reports copper_layers_used=0, track_segments=0. Board outline at 217x168mm is also correctly computed.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001221: board_width_mm/board_height_mm are null despite 56 Edge.Cuts entries present

- **Status**: new
- **Analyzer**: pcb
- **Source**: Kicad_Rotonometron_PCB_Rotonometron_PCB.kicad_pcb
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
- The Edge.Cuts geometry is embedded inside footprint fp_rect entries rather than as top-level gr_line/gr_arc objects. The analyzer only parses top-level board outline graphics, so it reports 0 edges and null dimensions. This is a known limitation — the analyzer cannot extract board dimensions when the outline lives inside footprint courtyard/edge rectangles. The 4-layer routed board (3160 segments, 147 footprints, net_count=184) is otherwise correctly analyzed.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001222: net_count=0 is correct — all 72 track segments are on net 0 (unassigned), incomplete design

- **Status**: new
- **Analyzer**: pcb
- **Source**: Kicad_Rotonometron_PCB_rev2_Rotonometron_V2_RotoSplit_RotoSplit.kicad_pcb
- **Created**: 2026-03-24

### Correct
- Source file confirms all segments use '(net 0)', meaning this is a partially-placed board where routes haven't been assigned to named nets yet. routing_complete=true is technically correct (no ratsnest unrouted count). Board dimensions 168x154mm are correctly computed from top-level Edge.Cuts.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001223: gerber_files=0 and all required layers missing despite drill files correctly parsed — gerber files not found/read

- **Status**: new
- **Analyzer**: gerber
- **Source**: Kicad_Rotonometron_PCB_rev2_Rotonometron_V2_rotonometron gerber
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
- The directory contains drill files (.drl) which are correctly parsed (770 total holes, PTH/NPTH classified). However gerber_files=0 and found_layers=[] with all 5 required layers missing. The gerber .gbr/.gtl/.gbl files are either not present in this directory or have non-standard extensions not recognized by the analyzer. This triggers a false 'incomplete=true' but the drill data itself is fully correct.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001224: Both PCB gerber directories produce identical drill analysis — correctly represents drill-only exports

- **Status**: new
- **Analyzer**: gerber
- **Source**: Kicad_Rotonometron_PCB_rotonometron gerber
- **Created**: 2026-03-24

### Correct
- Both gerber directories (PCB and PCB_rev2) contain only drill files, no copper/mask/silkscreen gerbers. The drill classification using X2 attributes is accurate: 223 vias at 0.4mm, component holes, and mounting holes all correctly identified. The layer_count=4 sourced from X2 FileFunction attribute is correct.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
