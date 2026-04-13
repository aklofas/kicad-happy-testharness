# Findings: sparkfun/SparkFun_CO2_Sensor-STC31 / Hardware_SparkFun_STC31

## FND-00001381: I2C bus detected with both STC31 and SHTC3 as devices on SCL/SDA; I2C pull-up resistors reported as missing, but R2 (2.2k) and R3 (2.2k) are present pull-ups behind solder jumper JP2; Component cou...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: SparkFun_STC31.kicad_sch
- **Created**: 2026-03-24

### Correct
- The analyzer correctly identifies the I2C bus with two devices (U3=STC31, U4=SHTC3) on both SCL and SDA nets. The bus_analysis section accurately reflects the design — both Sensirion sensors share the I2C bus, which matches the schematic intent. The ADDR net for address selection is also captured.
- statistics.total_components=31 matches the BOM breakdown: 2 caps, 1 LED, 4 fiducials, 3 graphic/logo symbols (G1/G2/G3), 3 connectors (J3/J4/J5), 5 jumpers (JP1-JP5), 6 resistors (R1-R5/R9), 4 standoffs (ST1-ST4), 2 ICs (U3/U4). The type breakdown (resistor:6, mounting_hole:4, other:4 [incl. G4], connector:3, fiducial:4, jumper:5, led:1, ic:2, capacitor:2) is consistent. Note G4 (OSHW_Logo) is found only in the PCB footprints list, not the schematic components list, explaining the 4 'other' count.
- decoupling_analysis shows rail '3.3V' with C1 and C3 both at 0.1uF, total 0.2uF. This matches the BOM exactly. The observation correctly notes has_bulk=false (no bulk cap like 10uF), has_bypass=true, has_high_freq=false — appropriate for a pure I2C sensor board powered externally via Qwiic.
- assembly_complexity.smd_count=31 and tht_count=0. In reality J4 is a 4-pin PTH (through-hole) header (footprint SparkFun-Connector:1x04 and PCB type=smd is wrong for that footprint class). However the schematic analyzer does not have direct footprint type information, and standoffs (ST1-ST4) also have THT drill holes. The PCB analyzer correctly shows tht_count=1. This discrepancy is acceptable since the schematic analyzer works from symbol type heuristics, not actual footprint pads.

### Incorrect
- bus_analysis.i2c[0].has_pull_up and [1].has_pull_up are both false, and pull_ups arrays are empty. However, R2 (2.2k on SCL) and R3 (2.2k on SDA) are I2C pull-up resistors gated by JP2 (labeled 'I2C', described as 'Solder Jumper, 3-pole, pins 1+2+3 closed/bridged'). The schematic text explicitly labels this section 'I2C Pull-Ups'. The analyzer fails to trace the resistors through the jumper to the SCL/SDA nets. The design_observations section also reports has_pullup=false for both lines. This is a false negative on pull-up detection.
  (bus_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001382: Board dimensions correctly reported as 25.4mm x 25.4mm (1 inch square SparkFun Qwiic form factor); Decoupling placement correctly identifies both caps near the two sensor ICs; footprint_count=58 is...

- **Status**: promoted
- **Analyzer**: pcb
- **Source**: SparkFun_STC31.kicad_pcb
- **Created**: 2026-03-24

### Correct
- statistics.board_width_mm=25.4 and board_height_mm=25.4, consistent with bounding_box (123.266 to 148.666 = 25.4mm in X, 85.406 to 110.806 = 25.4mm in Y). This is the standard SparkFun Qwiic 1-inch square form factor. The single rectangular Edge.Cuts outline (edge_count=1, type=rect) is plausible for this simple board.
- decoupling_placement shows U3 (STC31) with C1 at 3.03mm and C3 at 4.21mm, and U4 (SHTC3) with C3 at 2.22mm and C1 at 6.67mm — all on F.Cu, all sharing 3.3V/GND nets. These are plausible placement distances for a compact 25.4mm board with only two bypass caps serving two sensors. The shared_nets check correctly confirms the caps are wired to the IC's power nets.
- zones[0] shows a GND fill spanning both copper layers with fill_ratio=1.333 (filled_area=859.71mm2 vs outline_area=645.16mm2, expected for a zone that fills both sides of a 25.4x25.4=645mm2 board). The thermal_analysis.zone_stitching correctly counts 23 GND vias at 3.6/cm2 density. This matches the net_lengths entry for GND showing via_count=23.

### Incorrect
- statistics.footprint_count=58 includes 25 kibuzzard-* graphic/decorative footprints (all board_only, exclude_from_bom, pad_count=0) plus multiple G*** logo footprints. The actual electrically-relevant component count is closer to 28-30. The component_groups breakdown shows kibuzzard:25 and G:5 groups. While the count itself is not wrong (it is a footprint count), the practical component count for assembly purposes is overstated. The front_side=33/back_side=25 split is similarly skewed by these decoration-only items.
  (statistics)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001383: Panelized PCB correctly shows ~35x the single-board component count with 2002 footprints; routing_complete=false with unrouted_net_count=4 is likely a false alarm for a panelized board

- **Status**: promoted
- **Analyzer**: pcb
- **Source**: Production_SparkFun_STC31_panelized.kicad_pcb
- **Created**: 2026-03-24

### Correct
- The panelized file has footprint_count=2002, via_count=1435, zone_count=35, board dimensions 142.7x194.5mm. Given the single board is 25.4x25.4mm (645mm2), a panel of ~35 boards in a ~142x194mm array is geometrically consistent (35x645=22575mm2 vs 142.7x194.5=27753mm2, reasonable with rails/fiducials). The 35 zones matches 35 instances. The track_segments=5635 is also approximately 35x161=5635 — exact match, strongly confirming correct panel parsing.

### Incorrect
- The panelized board reports routing_complete=false and unrouted_net_count=4. In panelized PCBs produced by KiKit or similar tools, V-score/mousebite tabs and panel edge rails can create intentionally unconnected net stubs that are not design errors. The single board (Hardware_SparkFun_STC31.kicad_pcb.json) shows routing_complete=true and unrouted_count=0. The analyzer does not note the panelized context, which could cause false DRC alarms.
  (statistics)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001384: GKO (Edge.Cuts outline) file misidentified as B.Mask layer, causing false 'Edge.Cuts missing' completeness error; Drill classification correctly identifies 3 tool sizes: 0.3mm vias (1435), 1.016mm ...

- **Status**: promoted
- **Analyzer**: gerber
- **Source**: Production
- **Created**: 2026-03-24

### Correct
- The drill_classification section correctly uses x2_attributes to distinguish via drills (T1 0.3mm, 1435 holes), component PTH drills (T2 1.016mm, 140 holes), and NPTH mounting holes (T3 3.1mm, 140 holes). The count of 140 for each of the 1.016mm and 3.1mm tools is exactly 4 holes/board x 35 panels = 140, confirming the panel multiplier is consistent.
- layer_count=2 (F.Cu, B.Cu). The found_layers list contains all 8 expected layers: B.Cu, B.Mask, B.Paste, B.SilkS, F.Cu, F.Mask, F.Paste, F.SilkS. B.Paste is correctly present but empty (flash_count=0, draw_count=0) — this board has no back-side paste since all SMD components are on the front side (smd_ratio=0.94 with ComponentPad flashes only on F.Cu). The alignment check passes with all layer extents consistent with a ~133x180mm panel area.

### Incorrect
- The gerber output lists SparkFun_STC31_panelized.GKO with layer_type='B.Mask' and FileFunction='Soldermask,Bot'. However, .GKO is KiCad's standard extension for Edge.Cuts (board outline). Looking at the x2_attributes for the GKO file, the FileFunction is 'Soldermask,Bot' which conflicts with the .GKO extension — this may be a KiCad export anomaly where the GKO file actually contains board outline data but the X2 attribute was incorrectly set, or the analyzer is reading the X2 attribute instead of using the file extension for layer classification. As a result, completeness.missing_required=['Edge.Cuts'] and board_dimensions={} (empty). The actual outline data exists — there are 1219 draw strokes and 4 apertures in that file, consistent with a panel outline.
  (completeness)
- board_dimensions={} because the GKO file was misclassified as B.Mask (see previous finding). The layer_extents in alignment show B.Cu and F.Cu at 133.175x180.647mm, which is the actual panel copper extent and could serve as a proxy for board dimensions. The analyzer should fall back to copper extents when Edge.Cuts is missing, or correctly identify the GKO file as Edge.Cuts.
  (board_dimensions)

### Missed
(none)

### Suggestions
(none)

---
