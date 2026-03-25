# Findings: KiCadFiles / examples_test_test

## FND-00000706: Single-pin nets not flagged in connectivity_issues

- **Status**: new
- **Analyzer**: schematic
- **Source**: examples_test_test.kicad_sch.json
- **Created**: 2026-03-23

### Correct
(none)

### Incorrect
- R1 and R2 are completely unconnected (no wires) — all 4 nets are single-pin. connectivity_issues.single_pin_nets is empty [] when it should list all 4 __unnamed_0..3 nets. This is a real connectivity problem the analyzer silently misses.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00000707: RC filter not detected despite bypass caps around TL072

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: tests_fixtures_schematic_multichannel_mixer.kicad_sch.json
- **Created**: 2026-03-23

### Correct
(none)

### Incorrect
(none)

### Missed
- Design has a TL072 op-amp (IC1), bypass caps C1-C4, and resistors forming an audio mixer. The opamp_circuits entry is correct, but rc_filters is empty []. C3 (100nF) on the power supply and the input RC networks should produce at least one RC filter hit.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00000708: Crystal, regulator, and full 125-component BOM parsed correctly

- **Status**: new
- **Analyzer**: schematic
- **Source**: tests_fixtures_schematic_tinytapeout-demo.kicad_sch.json
- **Created**: 2026-03-23

### Correct
- X1 crystal detected in crystal_circuits, AP2112K-1.8 detected in power_regulators, all 125 components with correct type classification including fuse (F1) and net_tie. dnp_parts=8 matches design intent.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00000709: unconnected_hierarchical reports a false positive for /ENABLE label

- **Status**: new
- **Analyzer**: schematic
- **Source**: tests_fixtures_schematic_RoyalBlue54L-Feather.kicad_sch.json
- **Created**: 2026-03-23

### Correct
(none)

### Incorrect
- The label '/0a43c989.../ENABLE' is flagged as unconnected_hierarchical, but it appears in the labels list as a hierarchical_label with coordinates — it is present on the sheet. The sibling sheet's '/79d06a01.../ENABLE' net is populated in the nets dict with 4 points, suggesting the ENABLE hierarchy is connected. This may be a cross-sheet resolution issue.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00000710: 66-component ColdFire dev kit correctly parsed with all component types

- **Status**: new
- **Analyzer**: schematic
- **Source**: tests_fixtures_schematic_kit-dev-coldfire-xilinx_5213.kicad_sch.json
- **Created**: 2026-03-23

### Correct
- All 12 component types identified (IC, capacitor, connector, resistor, inductor, switch, diode, jumper, ferrite_bead, transistor, LED, crystal), 7 power rails extracted, 101 nets found.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00000711: 94-footprint 2-layer USB hub PCB parsed accurately

- **Status**: new
- **Analyzer**: pcb
- **Source**: tests_fixtures_pcb_StickHub_new.kicad_pcb.json
- **Created**: 2026-03-23

### Correct
- Correct footprint counts (94 total, 37 front/57 back, 86 SMD/1 THT), 87 vias, 47 nets, board dimensions 16.5x40mm, routing_complete=true, stackup extracted correctly.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00000712: Empty PCB handled gracefully with no false positives

- **Status**: new
- **Analyzer**: pcb
- **Source**: tests_fixtures_empty_empty.kicad_pcb.json
- **Created**: 2026-03-23

### Correct
- All statistics zero, board_outline edge_count=0, bounding_box=null, copper_presence warning correctly issued, silkscreen warnings appropriate.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00000713: copper_layers_used=0 despite F.Cu and B.Cu defined in layers list

- **Status**: new
- **Analyzer**: pcb
- **Source**: examples_test_test.kicad_pcb.json
- **Created**: 2026-03-23

### Correct
(none)

### Incorrect
- The PCB has 2 footprints placed on F.Cu (front_side=2) but copper_layers_used=0 with empty copper_layer_names. This is technically correct (no tracks routed) but misleading — the board clearly uses F.Cu for pads. A board with placed SMD components should report at least 1 copper layer used.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---
