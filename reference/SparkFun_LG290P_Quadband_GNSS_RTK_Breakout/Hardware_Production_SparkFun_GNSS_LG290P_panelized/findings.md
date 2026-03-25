# Findings: SparkFun_LG290P_Quadband_GNSS_RTK_Breakout / Hardware_Production_SparkFun_GNSS_LG290P_panelized

## FND-00001445: Component counts are accurate: 62 total, 11 caps, 9 resistors, 4 ICs, 10 connectors, 7 jumpers; LDO regulator RT9080-3.3 correctly detected with topology, input/output rails; RC filter on VCC_RF (R...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: Hardware_SparkFun_GNSS_LG290P.kicad_sch
- **Created**: 2026-03-24

### Correct
- The statistics.total_components=62 correctly includes all schematic symbols (61 in-BOM components plus G1 OSHW logo with in_bom=false). The component_types breakdown is verified: 4 mounting holes (ST1-4), 10 connectors, 11 capacitors (C1-C10, C13), 7 jumpers (JP1-7), 1 fuse (F1), 3 others (G1, G3, G5), 9 resistors (R1-R9), 4 fiducials (FID1-4), 4 ICs (U1-4), 3 LEDs (D1, D2, D4), 1 battery (BT1), 4 diodes (D3, D5, D6, D7), 1 inductor (L1). These all match the KiCad source.
- The RT9080-3.3 (U2) is correctly identified as an LDO, with input_rail=5V, output_rail=3.3V, and estimated_vout=3.3V derived from the fixed suffix on the part number. This matches the schematic where 5V feeds U2 and produces the 3.3V rail.
- Two RC low-pass filters are correctly identified: R6(10Ω)+C4||C3(100pF) at 159kHz cutoff on the VCC_RF supply path, and R7(1kΩ)+C9(1µF) at 159Hz cutoff for the V_BCKP battery backup supply. Both are real filter circuits matching the schematic topology.
- The L1(68nH)+C6(100pF) LC filter at 61.03 MHz is correctly identified. L1 and C6 share the __unnamed_0 net along with J5 (SMA antenna connector) and D3 (ESD protection). This is a genuine RF matching/filtering network in the antenna path for the GNSS receiver.
- D3 (PESD0402 bidirectional TVS) on the antenna line, D6 and D7 (PESD0603-240 bidirectional TVS) on data lines, and F1 (PTC resettable fuse 750mA) are all correctly identified as protection devices with their protected and clamp nets.
- The design_observations correctly reports i2c_bus for SCL and SDA nets with has_pullup=false. The schematic confirms no pull-up resistors connect to the SCL or SDA nets. U3 (LG290P), J4, J7 (Qwiic), J6, J9 connect to these nets. SparkFun's Qwiic ecosystem relies on external devices or separate pullup boards; this board provides none. The observation is accurate.
- The 3.3V rail decoupling analysis correctly lists C5(100nF), C8(33pF), C2(10µF), C13(1µF) for a total of 11.1µF. The coverage is correctly marked as has_bulk=true (C2 10µF), has_bypass=true (C5 100nF), and has_high_freq=true (C8 33pF), reflecting good broadband decoupling practice.
- All four power rails present in the design are identified. 3.3V is the LDO output, 5V is the USB input, GND is ground, and VCC_RF is the GNSS module's internal RF supply output. This matches the schematic power symbols.
- statistics.total_nets=75 matches the PCB net count of 75 (verified in the PCB output nets dictionary). statistics.total_no_connects=20 reflects the intentional NC pins on J1, J2, J4, J7, J8, U1, U2, U3, U4 visible as 'unconnected-*' named nets.

### Incorrect
- The analyzer reports an LC filter pairing L1(68nH) with C4||C3(~100pF) at 1.93 MHz. However, L1 and C4/C3 are on the same net (__unnamed_10) for different purposes: L1 is in series in the RF antenna signal path (J5 SMA → L1 → C6+RF_IN) while C4 and C3 are power supply bypass capacitors on the VCC_RF output side. They share a node topologically but do not form a tuned LC resonator. The genuine LC filter is L1+C6 at 61 MHz (the RF choke with the antenna filter cap).
  (signal_analysis)
- The 5V decoupling analysis marks has_bulk=true with caps C7(1µF) and C1(100nF). Conventionally, 'bulk' decoupling refers to large electrolytics (10µF+) providing bulk charge reservoir. A 1µF ceramic cap is typically bypass/decoupling, not bulk. The has_bulk classification likely uses a threshold ≥1µF, which is more lenient than the standard definition. This may mislead users into thinking there is adequate bulk decoupling on the 5V rail.
  (signal_analysis)

### Missed
- D5 (PMEG4005EJ Schottky diode, SOD-323) connects 3.3V (anode) to __unnamed_40 (cathode), which feeds R7 and ultimately the V_BCKP rail powering the GNSS RTC battery backup. It provides reverse blocking to prevent the backup battery (BT1) from backfeeding the 3.3V rail. The protection_devices list detects D6, D7, D3 (TVS diodes) and F1 (fuse) but misses D5.
  (signal_analysis)

### Suggestions
- Fix: 5V rail has_bulk=true is debatable — C7 (1µF) is not a bulk capacitor by conventional definition

---

## FND-00001446: 4-layer board correctly identified with proper stackup: F.Cu/In1.Cu/In2.Cu/B.Cu; B.Cu layer type reported as 'jumper' — correctly reflects the KiCad source layer definition; 138 total footprints co...

- **Status**: new
- **Analyzer**: pcb
- **Source**: Hardware_SparkFun_GNSS_LG290P.kicad_pcb
- **Created**: 2026-03-24

### Correct
- The PCB correctly reports copper_layers_used=4 with layer names F.Cu (signal), In1.Cu (signal), In2.Cu (power), B.Cu. The stackup is properly extracted including dielectric thicknesses and materials (FR4). Board dimensions are 43.18×43.18mm, verified against the Edge.Cuts rectangle in the source file.
- The KiCad PCB source file defines layer 31 as `(31 "B.Cu" jumper)`. This is an unusual layer type (should typically be 'signal') but the analyzer faithfully reports what is in the file. SparkFun apparently used a non-standard layer type designation. The layer is used as a normal copper signal layer despite the 'jumper' type tag.
- The PCB has 138 footprints total: 78 board_only decorative items (73 kibuzzard PCB art elements, 4 Qwiic logo G*** items, G1 OSHW logo) and 60 real assembly components (47 SMD + 5 THT + 8 jumpers/logos with allow_soldermask_bridges). The statistics.footprint_count=138 is verified correct.
- The single-board PCB (Hardware/SparkFun_GNSS_LG290P.kicad_pcb) correctly reports routing_complete=true and unrouted_net_count=0. The connectivity section confirms 75 total nets with 0 unrouted connections.
- Two zones are correctly detected: GND spanning F.Cu/In1.Cu/B.Cu with 1864mm² outline and 4212mm² filled area across 12 fill regions, and 3.3V on In2.Cu with 1864mm² outline. The thermal analysis correctly identifies 104 stitching vias for GND and 11 for 3.3V. The U4 (CH342F) thermal pad (2.7×2.7mm) with 1 nearby thermal via is also correctly noted.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001447: Panelized PCB reports routing_complete=false with 36 unrouted nets, but all 36 are intentional NC pads; Panelized board statistics are correct: 1103 footprints, 8-up panel (8× single board)

- **Status**: promoted
- **Analyzer**: pcb
- **Source**: SparkFun_GNSS_LG290P_panelized.kicad_pcb
- **Created**: 2026-03-24

### Correct
- The panelized PCB footprint count of 1103 = 8 × 138 (single board footprints) + small deviation from panelization artifacts. The board dimensions 109.704 × 187.92mm represent the full panel. Via count of 1288 = 8 × 161 (single board) confirms an 8-up panel arrangement.

### Incorrect
- The panelized PCB (Hardware/Production/SparkFun_GNSS_LG290P_panelized.kicad_pcb) reports routing_complete=false and unrouted_net_count=36. However, all 36 'unrouted' nets are named with the 'unconnected-*' pattern (NC pins on J1, J2, J4, J7, J8, U1, U2, U3, U4), which are intentional no-connects, not genuine routing failures. The panelization process appears to have created ratsnest entries for NC pads across the 8-up panel. The single-board PCB correctly shows routing_complete=true.
  (statistics)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001448: Inner copper layer Gerbers GL2 (In1.Cu) and GL3 (In2.Cu) not analyzed — critical 4-layer board inner layers missed; GKO file misclassified as B.Mask — it is the board outline (Edge.Cuts/Profile) fi...

- **Status**: promoted
- **Analyzer**: gerber
- **Source**: Hardware_Production
- **Created**: 2026-03-24

### Correct
- The drill classification correctly identifies three categories: 1288 via holes at 0.3mm diameter, 216 component holes (200 at 1.016mm PTH for connector pins, 16 at 0.65mm NPTH for footprint mechanical pins), and 32 NPTH mounting holes at 3.1mm (for the 4 standoffs × 8-up panel). The x2_attributes-based classification method is reported and applied correctly.
- The four unique trace widths (0.1524mm, 0.1778mm, 0.349mm, 0.4064mm) are correctly identified from the front copper Gerber. The minimum feature size of 0.125mm is within standard manufacturing capabilities. DFM tier is correctly classified as 'standard' with no violations.
- The B.Paste layer (GBP file) has aperture_count=0, flash_count=0, draw_count=0 and region_count=0, correctly indicating no SMD components on the back side require solder paste. This is consistent with the PCB analysis showing all 47 SMD components are on the front side (smd_count=47, back_side has only THT and jumpers).

### Incorrect
- The GKO file (SparkFun_GNSS_LG290P_panelized.GKO) is classified as layer_type='B.Mask' in the output, but it is the board outline file. Its X2 metadata erroneously says FileFunction=Soldermask,Bot (a bug in the SparkFun panelizer labeling), but the aperture_analysis correctly identifies a 'Profile' aperture function. The GKO extension conventionally means 'Board Outline' and its content draws the panelized board perimeter. As a result, missing_required=['Edge.Cuts'] and complete=false are reported, when the board outline IS present in GKO form.
  (completeness)
- The gerber output reports board_dimensions={}, providing no board size information. The layer extents in the alignment section show B.Cu and F.Cu both have width=103.354mm and height=174.22mm, which are the actual copper extents of the panel. The board_dimensions field should be populated from the Edge.Cuts/GKO outline data or from these layer extents, but is left empty.
  (board_dimensions)

### Missed
- The gerber analyzer reports 9 gerber files analyzed and layer_count=4, but GL2 and GL3 (the .GL2 and .GL3 extension files) are present in both the loose directory and the zip archive but are not included in the analysis. The analyzer does not recognize the .GL2/.GL3 file extensions as Gerber inner copper layers. Both files have proper X2 attributes: GL2=Copper,L2,Inr and GL3=Copper,L3,Inr. This means In1.Cu and In2.Cu completeness cannot be verified, and the layer_count=4 is inferred but not validated from actual Gerber content.
  (completeness)

### Suggestions
(none)

---
