# Findings: DotBots/TS4231-breakout-board / TS4231-BOB

## FND-00001628: TS4231 light-to-digital converter correctly parsed: 6 components, 8 nets, +3.3V and GND power rails; pwr_flag_warnings for +3.3V and GND are valid — no PWR_FLAG symbols present in design; C2 (1 µF ...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: TS4231-BOB.kicad_sch.json
- **Created**: 2026-03-24

### Correct
- statistics reports total_components=6 (C1, C2, D1, J1, R1, U1), unique_parts=6, total_nets=8, power_rails=[+3.3V, GND]. This is accurate. U1 is the TS4231 IC, D1 is the BPW34S photodiode (Device:D_Photo, classified as 'diode'), C1=100 nF and C2=1 µF are the supply bypass caps.
- The TS4231 schematic has no PWR_FLAG symbols at all (confirmed by searching the source file). The warnings that '+3.3V' and 'GND' have power_in pins but no power_out or PWR_FLAG are accurate and match what KiCad ERC would report.

### Incorrect
(none)

### Missed
- C2 (1 µF) has pin 1 connected to __unnamed_0 (the AVDD power-in pin of U1) and pin 2 to GND. The net is classified 'power_internal' rather than a named rail, so the decoupling_analysis only reports C1 (100 nF) on +3.3V with cap_count=1, total=0.1 µF. C2's role as AVDD decoupling for the TS4231's analog supply is not captured. The design_observations correctly notes that +3.3V has no bulk capacitor, but doesn't account for AVDD decoupling.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00001629: Small 2-layer 12×12.9 mm board with 6 footprints, fully routed, correctly parsed; J1 edge_clearance_mm reported as -7.2 mm — this is an intentional edge-mounted pin header, not a real clearance vio...

- **Status**: promoted
- **Analyzer**: pcb
- **Source**: TS4231-BOB.kicad_pcb.json
- **Created**: 2026-03-24

### Correct
- statistics: footprint_count=6, smd_count=3 (C1, C2, U1), tht_count=3 (D1 SMA, J1 pin-header, R1 — actually D1 is SMD and J1/R1 are THT-style), routing_complete=true, net_count=8. GND copper pours on both sides with 10 stitching vias. DFM standard tier, no violations.

### Incorrect
- J1 is a 1×4 2.54 mm pitch through-hole pin header placed at (129.2, 54.9) rotated 90°. At 90° rotation the four pins extend along the Y axis, reaching to approximately Y=59.7 mm — well beyond the board edge at Y=56.9 mm. This is a deliberate design choice (connector intended to be soldered flush with the board edge for mating). The edge_clearance_warnings entry with edge_clearance_mm=-7.2 is technically correct but not a manufacturing defect in context.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001630: TS4231 gerber set complete: 9 signal/mask/paste/silkscreen layer files + 2 drill map files, board 12×12.9 mm

- **Status**: new
- **Analyzer**: gerber
- **Source**: output.json
- **Created**: 2026-03-24

### Correct
- completeness: found_layers=[B.Cu, B.Mask, B.Paste, B.SilkS, Edge.Cuts, F.Cu, F.Mask, F.Paste, F.SilkS], complete=true. alignment.aligned=true. board_dimensions 12.0×12.9 mm matches PCB. Note: the 11 gerber files include 2 drill-map .gbr files (PTH-drl_map.gbr, NPTH-drl_map.gbr) in addition to the 9 layer gerbers — these are included in the statistics.gerber_files count of 11 but are not separate drill files.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
