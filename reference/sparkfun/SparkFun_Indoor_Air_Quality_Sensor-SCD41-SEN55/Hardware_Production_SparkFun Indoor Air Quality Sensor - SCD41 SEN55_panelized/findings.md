# Findings: SparkFun_Indoor_Air_Quality_Sensor-SCD41-SEN55 / Hardware_Production_SparkFun_AirQuality_Combo_panelized

## FND-00001441: Power regulator detected with same input and output rail (3.3V→3.3V), but AP3012 is a boost converter producing 5V for the SEN55; I2C pull-up resistors R3 (SDA) and R4 (SCL) not detected; analyzer ...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: Hardware_SparkFun Indoor Air Quality Sensor - SCD41 SEN55.kicad_sch
- **Created**: 2026-03-24

### Correct
- The design_analysis.bus_analysis.i2c array contains entries for both SDA and SCL nets, correctly identifying U6 (SEN55_Connector) and U3 (SCD41) as the I2C devices. The bus topology is correctly recognized.
- The design_observations entry for category 'switching_regulator' correctly identifies U1=AP3012 with inductor=L1 and input_rail=3.3V. The detection of the boost topology is correct even though the output rail is misidentified.
- The statistics.power_rails correctly lists ['3.3V', '5V', 'GND'], matching the actual schematic power net structure.
- The decoupling_analysis correctly identifies C1 (0.1uF) and C4 (4.7uF) on the 3.3V rail, and C5 (0.1uF) plus C2 (22uF) on the 5V rail. Rail coverage observations (has_bulk, has_bypass) are accurate.
- U3/SCD41 is correctly identified as type 'ic', with function recognized as photoacoustic CO2 sensor. Its I2C pins (SCL pin 9, SDA pin 10) are correctly mapped to the SCL and SDA nets. GND pads (6, 20, 21) and VDD/VDDH power pins are correctly resolved.

### Incorrect
- The signal_analysis.power_regulators entry for U1/AP3012 reports input_rail='3.3V' and output_rail='3.3V'. This is wrong: the AP3012 is a step-up (boost) converter. Its IN pin (pin 5) is on the 3.3V rail, while the 5V output net (via diode D1/PMEG4005EJ anode and capacitor C2) feeds the SEN55 connector. The feedback network (R2=100k, R3=33k) sets the output voltage, which the decoupling analysis confirms is associated with the 5V rail. The analyzer incorrectly resolved the output rail by tracing the FB pin resistors to the 5V net but still reports 3.3V as output.
  (signal_analysis)
- The BOM reports D1 as value 'PMEG4005EJ', type 'diode', with quantity 1. However, the components array shows D1 appearing twice: once as PMEG4005EJ (Schottky diode, uuid 7f530a75) and once as 'Red' LED (uuid fd234bde, type 'led'). These appear to be genuinely two different schematic symbols both using reference D1 — one is the boost converter's catch diode (PMEG4005EJ, Schottky) and the other is a power-indicator LED. The BOM only captures one D1 entry. The ic_pin_analysis for U1/AP3012 SW pin connects to 'D1' value 'Red' (the LED), further confirming the analyzer is confusing the two D1 components.
  (statistics)
- The schematic statistics report 32 total_components. However, the components array contains duplicate ref 'C1' (two distinct entries: 1.0uF at uuid 10b30d4b and 0.1uF at uuid 154a09c4; both in_bom=true, same ref). Similarly, 'C5' appears twice (1.0uF at uuid 50d7428e and 0.1uF at uuid 8a6daf3c). 'R3' appears three times with different values (2.2k, 4.7k, 33k). 'D1' appears twice. This suggests the schematic has components with shared/reused reference designators or the parser is duplicating entries. The PCB uses entirely different ref numbering (U5 for AP3012, L2 for inductor, D2 for Schottky, R1/R2/R5/R6 instead of R3/R4/R2). The component count of 32 likely undercounts the actual unique components.
  (statistics)
- The design_analysis.cross_domain_signals section flags both SDA and SCL as crossing domains from 3.3V (U3/SCD41) to 5V (U6/SEN55_Connector) and asserts needs_level_shifter=true. However, the Sensirion SEN55 I2C interface operates at 3.3V logic levels — it is powered by 5V but its SDA/SCL logic is 3.3V-compatible. The analyzer infers that U6 is a 5V device because its VDD is on the 5V rail, but the SEN55 I2C interface uses 3.3V signaling. No level shifter is needed or present, and flagging this as a requirement is a false positive.
  (design_analysis)

### Missed
- The schematic has R3 (2.2k) connected between 3.3V and SDA, and R4 (2.2k) connected between 3.3V and SCL. These are classic I2C pull-up resistors. The design_observations i2c_bus entries for both SDA and SCL report has_pullup=false and pullup_resistor=null. The bus_analysis.i2c entries similarly show empty pull_ups arrays and has_pull_up=false. Looking at the net data, on the SDA net R3 pin 1 connects directly to the SDA line, and on the SCL net R4 pin 2 connects directly to SCL — the analyzer failed to recognize these as pull-ups. (Note: in the schematic the pull-up resistors for the I2C bus connecting to the Qwiic connectors are R3=2.2k/SDA and R4=2.2k/SCL; there is also JP2 which can disconnect them.)
  (signal_analysis)
- R2 (100k) connects from the 5V output rail to the AP3012 FB pin, and R3 (33k) connects from the FB pin to GND (via JP2 and a net to GND). This classic resistive voltage divider sets the boost converter output voltage. The signal_analysis.voltage_dividers list is empty. The feedback_networks list is also empty. The ic_pin_analysis shows both resistors on pin 3 (FB) of U1 but the voltage divider pattern was not recognized.
  (signal_analysis)
- The signal_analysis.protection_devices list is empty. D1 (PMEG4005EJ, 40V/500mA Schottky diode) serves as the catch/freewheeling diode in the AP3012 boost converter circuit — a standard component in switching regulator topologies. It is connected between the SW node (U1 pin 1) and the 5V output rail. The analyzer did not detect this protection/rectification diode.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00001442: Footprint count (58), layer count (2), routing completeness, via count (47), and track segment count (119) are correct; GND copper zone spanning F&B.Cu correctly identified with 32 thermal stitchin...

- **Status**: promoted
- **Analyzer**: pcb
- **Source**: Hardware_SparkFun Indoor Air Quality Sensor - SCD41 SEN55.kicad_pcb
- **Created**: 2026-03-24

### Correct
- The PCB has 58 footprints (39 front, 19 back), 2 copper layers (F.Cu, B.Cu), 119 track segments, 47 vias, and is fully routed with 0 unrouted nets. Net count of 32 matches the schematic. These all appear accurate based on cross-checking the footprint list and net table.
- The zones array reports one GND zone on F&B.Cu with outline_area_mm2=1016.13, fill_ratio=1.567 (filled area larger due to both layers), and the thermal_analysis confirms 32 via-stitch vias for the GND zone at 3.1 vias/cm2. This is correct — the board uses a flood GND pour.
- The thermal_analysis.thermal_pads correctly identifies U3 pad 21 (GND thermal pad, 4.8x4.8mm, 23.04mm²) with 9 nearby thermal vias on F.Cu. The via_in_pad analysis also correctly lists 4 vias within the pad courtyard.
- Both J1 and J2 (Qwiic_RA, JST 1mm 4-pin right-angle) are correctly mapped with pad 1=GND, pad 2=3.3V, pad 3=SDA, pad 4=SCL — the standard Qwiic pinout. The NC pads are correctly assigned unconnected nets.
- The tracks.width_distribution correctly shows 0.4064mm (50 segments, power tracks) and 0.1778mm (69 segments, signal tracks). All vias are consistently 0.56mm/0.3mm drill.

### Incorrect
- The board_outline section shows edge_count=0, edges=[], and bounding_box=null. However, the PCB has a defined board outline on the Edge.Cuts layer (confirmed by the gerber output showing an Edge.Cuts/GKO file with draw_count=527 and a Profile aperture). The main PCB layout is clearly bounded (the gerber layer extents show approximately 172.95 x 133.84 mm dimensions for copper layers). The board outline parser either failed to find or parse the Edge.Cuts shapes.
  (board_outline)
- The statistics show 58 footprints (39 front, 19 back), but the component_groups show 21 kibuzzard entries plus other board_only/aesthetic footprints. The kibuzzard entries are PCB artwork elements (logos, decorative text), not real components. The smd_count=30 and tht_count=1 appear more representative of real components but the front/back totals are inflated by these purely decorative footprints. This is a structural limitation but worth noting.
  (statistics)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001443: GKO file (board outline/Edge.Cuts) misclassified as B.Mask layer, causing Edge.Cuts to appear as missing_required; Gerber layer set is complete (8 layers) for a 2-layer board: F.Cu, B.Cu, F.Mask, B...

- **Status**: promoted
- **Analyzer**: gerber
- **Source**: Hardware_Production
- **Created**: 2026-03-24

### Correct
- The completeness.found_layers correctly lists all 8 standard layers for a 2-layer board. Both PTH and NPTH drill files are present (has_pth_drill=true, has_npth_drill=true).
- The drill_classification accurately separates vias (282 at 0.3mm) from component holes (24 at 1.016mm, for J3 4-pin THT connector) and mounting holes (30 at 3.302mm NPTH, for the 5 standoffs across 6 panel copies). These counts are consistent with the panelized PCB having 6 copies of the design.
- The trace_widths section shows exactly 2 unique widths (0.1778mm and 0.4064mm), consistent with the PCB analyzer output. The min_feature_mm of 0.1778mm is accurate.
- The alignment section shows aligned=true with no issues. Layer extents are consistent between F.Cu and B.Cu (both 172.95 x 133.841mm), indicating correct gerber generation.
- The gerbers come from the panelized production file. The drill count of 282 vias matches exactly 6 copies of the single-board via count (47). The 30 mounting holes match 6 × 5 standoffs. The 24 THT component holes = 6 × 4 (J3 connector). Component analysis shows 55 unique components from the panelized file, consistent with 6 copies of ~9 unique SMD types plus board-only elements.

### Incorrect
- The gerber output lists 'SparkFun Indoor Air Quality Sensor - SCD41 SEN55_panelized.GKO' with layer_type='B.Mask'. The .GKO extension is the standard KiCad extension for the board outline (Edge.Cuts / Profile layer), not for the back soldermask. The x2_attributes for this file show FileFunction='Soldermask,Bot' but the Profile aperture function is also present. Because the GKO file is misclassified, Edge.Cuts appears in missing_required and complete=false. The board outline file is actually present and should be correctly identified as Edge.Cuts.
  (completeness)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001444: Panelized PCB reports routing_complete=false with 21 unrouted nets, but the source single-board PCB is fully routed; Panelized PCB board dimensions correctly extracted as 179.3 × 148.05mm for the 6...

- **Status**: promoted
- **Analyzer**: pcb
- **Source**: SparkFun Indoor Air Quality Sensor - SCD41 SEN55_panelized.kicad_pcb
- **Created**: 2026-03-24

### Correct
- Unlike the single-board PCB which failed to extract board dimensions (null), the panelized PCB correctly reports board_width_mm=179.3 and board_height_mm=148.05. The panel contains 6 copies arranged in a 2×3 or similar array.

### Incorrect
- The panelized PCB output reports routing_complete=false and unrouted_net_count=21. However, the single-board PCB (SparkFun Indoor Air Quality Sensor - SCD41 SEN55.kicad_pcb) correctly shows routing_complete=true with 0 unrouted nets. The panelized file uses an older KiCad format (version 20221018) and the routing status parser appears to be incorrectly reading the ratsnest or unconnected status from the panel format. The panel has 350 footprints (6×~58) and 1683mm of track, consistent with a fully routed panel.
  (statistics)

### Missed
(none)

### Suggestions
(none)

---
