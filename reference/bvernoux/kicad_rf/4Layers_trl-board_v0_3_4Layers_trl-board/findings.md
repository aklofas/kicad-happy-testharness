# Findings: bvernoux/kicad_rf / 4Layers_trl-board_v0_3_4Layers_trl-board

## FND-00002365: Legacy 'Top'/'Bottom' layer names not recognized as copper layers — 4-layer board reported as 2-layer; front_side=0 and back_side=0 reported for board with 18 footprints all placed on 'Top' layer

- **Status**: promoted
- **Analyzer**: pcb
- **Source**: pcb_kicad_rf_4Layers_trl-board_v0_3_4Layers_trl-board.kicad_pcb.json
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
- The TRL calibration board uses KiCad 5 legacy layer names 'Top' and 'Bottom' instead of 'F.Cu'/'B.Cu'. The PCB analyzer reports copper_layers_used=2 with only ['In1.Cu', 'In2.Cu'] in copper_layer_names, missing the outer signal layers entirely. The board is actually 4-layer (Top, In1.Cu, In2.Cu, Bottom). Additionally, front_side=0 and back_side=0 are reported even though all 18 footprints are placed on layer 'Top', because the analyzer does not recognize the legacy 'Top' name as the front copper layer.
  (statistics)
- The PCB analyzer reports front_side=0 and back_side=0, with smd_count=6 and tht_count=12. The source PCB file shows all module entries use '(layer Top)', which is the KiCad 5 legacy name for the front copper layer. Because 'Top' is not mapped to the front side, the side-classification logic assigns no footprints to front or back, making the counts wrong. The total of 18 footprints is correctly reported but split as 6 SMD and 12 THT — the THT coaxial connectors are correct but the side assignments are not.
  (statistics)

### Missed
(none)

### Suggestions
(none)

---

## FND-00002366: FOO_P/FOO_N differential pair correctly detected from net names

- **Status**: new
- **Analyzer**: schematic
- **Source**: schematic_kicad_rf_sma-probetarget_oshpark_bve_v0_4_sma-probetarget.sch.json
- **Created**: 2026-03-24

### Correct
- The SMA probe target schematic has two coaxial connectors J4 and J2 connected to nets FOO_N and FOO_P respectively. The analyzer correctly identifies this as a differential pair using the _P/_N naming convention. The pair entry includes has_esd=false which is appropriate since no ESD protection is present in this calibration fixture.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00002367: F1 and F2 'Fixture 0402' components (lib symbol R-TRL-Calkit) classified as 'fuse' type

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: schematic_kicad_rf_4Layers_trl-board_v0_3_4Layers_trl-board.sch.json
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
- F1 and F2 are TRL calibration kit fixture components with value 'Fixture 0402', using a resistor-type symbol from the custom 'R-TRL-Calkit' library but reference designator prefix 'F'. The analyzer classifies them as 'fuse' because the 'F' reference prefix matches the fuse heuristic. These are actually PCB fixture pads for the calibration kit — not fuses. The signal_analysis.protection_devices array incorrectly lists F2 as a fuse protecting net '__unnamed_16' clamped to GND.
  (statistics)

### Missed
(none)

### Suggestions
(none)

---

## FND-00002368: 4-layer gerber set correctly identified with all inner and outer copper layers present

- **Status**: new
- **Analyzer**: gerber
- **Source**: gerber_kicad_rf_OSHPark_4Layers_trl-board_v0_1_oshpark_gerber.json
- **Created**: 2026-03-24

### Correct
- The gerber analyzer correctly identifies all 11 files including F.Cu, B.Cu, In1.Cu, In2.Cu, plus mask, paste, silk, and Edge.Cuts layers. The completeness check passes for required layers (missing_required=[]), and the alignment check passes (aligned=true). The missing drill files (has_pth_drill=false) are correctly flagged, resulting in complete=false, which is accurate — this TRL calibration board has no drilled through-holes except the coaxial connector press-fit pads.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
