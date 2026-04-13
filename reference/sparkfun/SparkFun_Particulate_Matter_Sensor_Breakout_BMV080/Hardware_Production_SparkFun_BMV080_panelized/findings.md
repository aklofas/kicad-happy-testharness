# Findings: sparkfun/SparkFun_Particulate_Matter_Sensor_Breakout_BMV080 / Hardware_Production_SparkFun_BMV080_panelized

## FND-00001505: Component counts are accurate: 24 total, with correct type breakdown; Power rails correctly identified as 3.3V and GND only; Decoupling capacitor analysis correctly identifies 5 caps at 18.8 uF on ...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: Hardware_SparkFun_BMV080.kicad_sch
- **Created**: 2026-03-24

### Correct
- The analyzer correctly identifies 24 total components: 5 capacitors (C1-C5), 5 resistors (R1-R5), 4 jumpers (JP1-JP4), 4 fiducials (FID1-4), 2 connectors (J1, J2), 3 other (G1 OSHW Logo, G2 SparkFun Logo, G3 qwiic Logo), 1 IC (U1 BMV080). These match the source schematic exactly.
- The design is a single-rail 3.3V design with GND. The BMV080 has four separate VDD pins (VDDL, VDDA, VDDD, VDDIO) all connected to 3.3V. The analyzer correctly reports power_rails=['3.3V', 'GND'].
- The analyzer correctly finds C1-C4 (4x 2.2uF) and C5 (10uF) as decoupling capacitors on the 3.3V rail, totalling 18.8 uF. The BMV080 datasheet requires decoupling on each VDD pin. The analyzer correctly flags 'has_bypass': false because all caps are bulk (>=1uF) with no 100nF or smaller bypass caps.
- The analyzer correctly identifies SDA and SCL as I2C bus nets with U1 (BMV080) as the device. The Qwiic connector (J1) and 7-pin header (J2) also carry these signals. The bus topology is correctly traced.
- U1 (BMV080) is correctly typed as 'ic' with the Bosch datasheet URL and correct lib_id 'SparkFun-Sensor:BMV080'. The 13-pin FPC connector footprint (FPC_0.3mm-13) is correctly assigned. All power and signal pins are correctly traced.
- All 23 BOM-included components have empty MPN fields. The analyzer correctly lists all of them in missing_mpn. SparkFun uses a separate BOM management system and often doesn't embed MPNs in the schematic symbol properties.
- G2 and G3 are schematic-only logo symbols with no PCB footprint assigned. The analyzer correctly identifies them as missing_footprint. These are cosmetic/documentation symbols that intentionally have no physical footprint and on_board=false.
- The analyzer correctly reports inconsistent label shapes: SCL has both 'input' and 'output' shaped global labels, and AB0 has both 'input' and 'output' shaped labels. This reflects the dual-role of these signals (SCL drives the sensor, AB0 is bidirectional for address configuration).
- The subcircuit for U1 (BMV080) correctly identifies all 15 neighboring components: 5 capacitors, 2 connectors, 3 jumpers (JP2, JP3, JP4), and 5 resistors. JP1 is missing from the subcircuit neighbor list but it's the mode select jumper which is reasonably separated from the IC's direct periphery.

### Incorrect
- R3 (2.2k) and R5 (2.2k) are I2C pull-up resistors. R3 has pin1=SCL and pin2 connected to JP4 pin B (__unnamed_3). R5 has pin1=SDA and pin2 connected to JP4 pin A (__unnamed_8). JP4 is a 3-pole net-tie solder jumper (SolderJumper_3_Bridged123_No_Silk) with pin C bridged to 3.3V. The schematic text explicitly says 'To remove pull-up resistors on SDA/SCL, cut traces in jumper, JP4 (I2C)'. The analyzer fails to trace the pull-up path through the JP4 net-tie to discover that R3/R5 are pulled to 3.3V. Instead it labels them as 'series' resistors to unnamed nets and reports has_pullup=false.
  (signal_analysis)
- The source KiCad schematic contains 3 no_connect markers (grep confirms 3 occurrences of 'no_connect' in the .kicad_sch file). These are on J1.NC1, J1.NC2 (Qwiic connector NC pins), and U1.13 (BMV080 NC pad). The analyzer reports total_no_connects=0 and no_connects=[]. These NC pins do appear in the nets analysis as 'no_connect' pin_type entries, but are not counted in the statistics. The no_connects list should contain at least these 3 entries.
  (statistics)

### Missed
- U1 pin 7 (PS, Protocol Select) is reported on net '__unnamed_6' with only 1 pin. In the PCB, U1 PS pad is connected to Net-(JP1-C) which routes to JP1 center, connecting through the MODE solder jumper. The schematic shows JP1 center (pin 2/C) on net '__unnamed_9' (also single-pin). These two unnamed nets should represent the same electrical node (wire trace exists between PS pin at 77.47,66.04 and connecting to JP1 region), but the net tracer assigns them separate unnamed net IDs. The practical result is that U1 PS appears to be floating in the analysis when it is actually connected to JP1.
  (connectivity_issues)

### Suggestions
(none)

---

## FND-00001506: Board dimensions correctly reported as 24.13 x 12.7 mm; 2-layer stackup correctly identified (F.Cu and B.Cu only); smd_count=17 undercounts — JP1-JP4 solder jumpers are SMD but classified as 'allow...

- **Status**: promoted
- **Analyzer**: pcb
- **Source**: Hardware_SparkFun_BMV080.kicad_pcb
- **Created**: 2026-03-24

### Correct
- The board outline is a simple rectangle from (116.84, 90.17) to (140.97, 102.87) = 24.13 mm wide x 12.7 mm tall. This matches the expected SparkFun Qwiic breakout board size (approx 1" x 0.5"). The board_outline edge_count=4 is correct for a rectangle.
- The analyzer correctly identifies copper_layers_used=2 with F.Cu and B.Cu. The stackup section confirms a standard 4-layer stack definition but only 2 copper layers are used. Board thickness is 0.82mm (non-standard, used for SparkFun thin Qwiic boards).
- The analyzer correctly reports 60 through-hole vias (all 0.6mm/0.3mm), 177 track segments across F.Cu (83) and B.Cu (94), and routing_complete=true with 0 unrouted nets. The net lengths are detailed and consistent with the 2-layer board layout.
- The analyzer correctly identifies one GND zone spanning both F.Cu and B.Cu layers, with 41 stitching vias and density of 13.4 vias/cm2. The zone fill_ratio is reported as 1.08 which is discussed in a separate finding.
- The analyzer correctly identifies C1 (2.34mm), C2 (3.12mm), C4 (3.61mm), C3 (4.51mm), and C5 (5.5mm) as nearby decoupling capacitors for U1. C1 and C2 are on the same side (F.Cu) as U1, while C3, C4, and C5 are on B.Cu. The closest cap at 2.34mm is good placement for the BMV080's sensitive analog supply.
- The analyzer correctly reports 16 nets including all signal nets (SDA, SCL, AB0, AB1, IRQ), internal jumper nets (Net-JP1-A, Net-JP1-C, Net-JP2-A, Net-JP3-A, Net-JP4-A, Net-JP4-B), NC nets (unconnected-J1-NC-PadNC1, unconnected-J1-NC-PadNC2, unconnected-U1-NC-Pad13), and power nets (3.3V, GND).
- The analyzer correctly classifies J2 (Conn_01x07) as type='through_hole' with 7 pads, and J1 (Qwiic JST 1.0mm right-angle) as type='smd' with 6 pads (4 signal + 2 NC). The Qwiic connector is placed on B.Cu (bottom side) which is typical for SparkFun designs.

### Incorrect
- The PCB reports smd_count=17 and tht_count=1 out of 55 total footprints. However, JP1-JP4 (4 solder jumpers on B.Cu) are physically SMD pads but the analyzer classifies them as type='allow_soldermask_bridges' (the KiCad footprint attribute) rather than 'smd'. They should be counted as SMD. The actual SMD count should be 21 (17 + 4 jumpers). The remaining 33 footprints are board_only decorative/kibuzzard elements and 1 is exclude_from_bom.
  (statistics)
- The GND zone fills both F.Cu (187.19 mm2) and B.Cu (143.9 mm2). The filled_area_mm2=331.09 is the SUM of both layers' copper, while outline_area_mm2=306.45 is the zone polygon area (a single-layer concept). The ratio 331.09/306.45=1.08 exceeds 1.0, creating the misleading impression that the zone overflows its boundary. The correct per-layer fill ratios are F.Cu: 0.61 and B.Cu: 0.47, both well under 1.0. The fill_ratio should either be computed per-layer or use total_copper / (outline_area * layer_count).
  (zones)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001507: Panelized PCB incorrectly reports routing_complete=false due to NC pads treated as unrouted; Panelized board footprint count (2869) and large track/via counts correctly parsed

- **Status**: promoted
- **Analyzer**: pcb
- **Source**: SparkFun_BMV080_panelized.kicad_pcb
- **Created**: 2026-03-24

### Correct
- The panelized board contains 54 copies of the single-board design, correctly reflected in the counts: 2869 footprints, 9558 track segments, 3240 vias, 54 zones, and 54 times the per-instance components. The board dimensions of 160.98 x 132.0 mm reflect the full panel.

### Incorrect
- The panelized board reports routing_complete=false with unrouted_net_count=3. The 3 'unrouted' nets are: unconnected-(J1-NC-PadNC1), unconnected-(J1-NC-PadNC2), and unconnected-(U1-NC-Pad13). These are intentional no-connect pads that KiCad assigns to auto-generated nets; they are not actual routing failures. There are 54 instances of each NC net in the panelized board (because the panel contains 54 copies of the design). The board is fully routed — the NC pads do not need traces.
  (statistics)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001508: v01b panelized PCB also incorrectly reports routing_complete=false due to NC pads

- **Status**: promoted
- **Analyzer**: pcb
- **Source**: SparkFun_BMV080_panelized_v01b.kicad_pcb
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
- Same issue as the main panelized board: routing_complete=false with 3 unrouted nets corresponding to NC pads on J2 (Qwiic connector, note different reference from main schematic) and U1. These are intentional no-connect pads, not routing failures. The v01b panel contains fewer copies (4 copies based on 256 vias vs 3240 in the main panel).
  (statistics)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001509: Edge.Cuts reported missing but .GKO files contain the board outline with Profile apertures; layer_count=4 misleadingly suggests a 4-layer board when both panels are 2-layer designs; All 8 standard ...

- **Status**: promoted
- **Analyzer**: gerber
- **Source**: Hardware_Production
- **Created**: 2026-03-24

### Correct
- The gerber set correctly identifies B.Cu, B.Mask, B.Paste, B.SilkS, F.Cu, F.Mask, F.Paste, and F.SilkS layers (though Edge.Cuts is misidentified — see separate finding). The alignment check correctly reports aligned=true with SameCoordinates=Original in X2 attributes, indicating all gerbers share the same coordinate system.
- The panelized set's drill files are correctly classified: 3240 via holes (0.3mm, the same as in the single-board PCB x54), 378 component holes (1.016mm, for J2 through-hole header x54), and 8 NPTH mounting holes (3.302mm, panel tooling/mounting holes). The v01b set has a smaller panel with 256 vias, 24 component holes (1.016mm), 4 component holes (0.95mm), and 8 NPTH holes.
- The analyzer correctly finds three unique trace widths in the panelized gerbers: 0.2mm and 0.2032mm for signal routes, and 0.508mm for power traces. These match the PCB analyzer's track width distribution (0.2: 69 segments, 0.2032: 89 segments, 0.508: 19 segments). The min_trace_mm=0.2mm is correctly reported.
- The gerber component analysis shows 54 unique components per layer (front_side=31, back_side=23), consistent with the panelized PCB having 54 instances of the design. The pads_per_component counts (e.g., C1: 108 = 2 pads x 54 instances) are internally consistent.

### Incorrect
- The gerber completeness check reports missing_required=['Edge.Cuts'] and complete=false. However, both SparkFun_BMV080_panelized.GKO and SparkFun_BMV080_panelized_v01b.GKO contain the board outline — they use 'Profile' aperture function in their content. The problem is that these .GKO files have the X2 attribute FileFunction=Soldermask,Bot instead of the expected FileFunction,Profile. This causes the analyzer to classify the GKO files as B.Mask (layer_type='B.Mask') instead of Edge.Cuts. This appears to be a KiCad export bug where the panelizer tool embedded the wrong X2 FileFunction attribute in the outline file. The analyzer's behavior (classifying by X2 attribute) is technically correct, but the underlying board outline IS present.
  (completeness)
- The gerber set contains files from two panel versions (panelized and panelized_v01b), each a 2-layer board. The analyzer computes layer_count by counting copper gerber files: 2 per version x 2 versions = 4. This is misleading because a reader would expect layer_count to represent the PCB stack-up copper layer count (which is 2). The actual copper layer stack-up is F.Cu (L1) and B.Cu (L2) for both designs.
  (layer_count)

### Missed
(none)

### Suggestions
(none)

---
