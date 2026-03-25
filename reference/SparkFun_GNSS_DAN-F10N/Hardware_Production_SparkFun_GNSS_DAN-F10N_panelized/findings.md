# Findings: SparkFun_GNSS_DAN-F10N / Hardware_Production_SparkFun_GNSS_DAN-F10N_panelized

## FND-00001421: Component count and power rail detection are accurate; RC and LC filter detection is correct for the GNSS RF power supply network; No I2C bus detected despite DAN-F10N GNSS module supporting I2C; L...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: Hardware_SparkFun_GNSS_DAN-F10N.kicad_sch
- **Created**: 2026-03-24

### Correct
- 52 total components are correctly tallied from component_types (4 mounting holes, 2 LEDs, 9 caps, 4 diodes, 1 fuse, 3 other, 4 ICs, 4 fiducials, 8 resistors, 7 jumpers, 1 battery, 4 connectors, 1 inductor — sum = 52). Power rails [3.3V, 5V, GND, VBUS, VCC_RF, VDD] correctly identify the 3.3V LDO output, 5V USB input, GNSS RF supply, and regulator input domains.
- Two RC filters and one LC filter are detected. R7(1k)+C9(1µF) → 159 Hz low-pass on V_BCKP backup supply line is correct. R6(13.3Ω)+C1||C2(~100pF) → 119 kHz is correct for the VCC_RF supply entry filter. The LC filter with L1(33nH)+C1||C2(~100pF) resonating at 2.77 MHz is mathematically correct. The LDO regulator RT9080-3.3 from VDD→3.3V is correctly identified. The RC filter math and component pairing are accurate.
- The RT9080-3.3 LDO is correctly identified with input_rail=VDD and output_rail=3.3V. The protection devices correctly identify D4 (PESD0402 TVS on ANT_IN) and F1 (6V/0.5A fuse on VBUS). The decoupling coverage observations for 3.3V and VDD rails are correct — 3.3V has bulk+bypass+high-freq, VDD has bulk+bypass but no high-freq capacitor.

### Incorrect
(none)

### Missed
- The DAN-F10N GNSS module supports I2C communication. The design_observations list contains no i2c_bus entries and i2c_buses is absent. The GNSS module (U6) likely has I2C pins that are not connected or left as no-connect in this design, which explains the absence. However, no observation is generated noting this omission. The test_coverage section lists only a UART debug connector — confirming I2C is not wired up — but no explicit note is generated about unused I2C capability.
  (signal_analysis)
- rf_chains and rf_matching both return empty lists despite the design having a clear RF path: RF antenna → U1 (DT1042-04SO ESD protection IC) → ANT_IN → U6 (DAN-F10N GNSS module). The LC filter on VCC_RF supply (L1+C1||C2) is a high-frequency EMI filter for the GNSS RF supply, not a signal-path RF component. The antenna signal path itself (U1 → U6 via ANT_IN net) is not modeled as an RF chain.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00001422: Board dimensions, layer count, and routing completeness are accurate; board_outline lacks area and perimeter despite bounding_box being populated; Footprint count reasonable when accounting for kib...

- **Status**: promoted
- **Analyzer**: pcb
- **Source**: Hardware_SparkFun_GNSS_DAN-F10N.kicad_pcb
- **Created**: 2026-03-24

### Correct
- Board bounding box 40.64×40.64 mm matches SparkFun's standard 1.6"×1.6" form factor exactly. 4 copper layers (F.Cu, In1.Cu, In2.Cu, B.Cu) is correct for this GNSS design. routing_complete=True and unrouted_count=0 confirm the design is fully routed. DFM tier='standard' with min_track_width=0.1524mm (6mil) is consistent with SparkFun's typical fab rules.
- PCB reports 95 footprints vs schematic's 52 components. The discrepancy is accounted for by ~41 kibuzzard-* graphical decoration footprints (SparkFun's PCB art tool), plus fiducials and mounting holes which have PCB footprints but no schematic function. The 50 real component refs in the gerber panel match the 52 schematic components minus G3 (no footprint) and one graphic element. smd_count=40 and tht_count=3 are plausible for a compact GNSS breakout.

### Incorrect
- The board_outline section has edge_count, edges, and bounding_box populated (correctly showing width=40.64, height=40.64 mm), but area_mm2 and perimeter_mm are None. For a rectangular board this is trivially computable (area = 40.64×40.64 = 1651.6 mm², perimeter = 4×40.64 = 162.56 mm). This omission is consistent across all three designs and means consumers of the JSON cannot directly access area/perimeter without recomputing from the bounding box. The board outline is a proper closed rectangle per the Edge.Cuts layer.
  (board_outline)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001423: GKO (Edge.Cuts) file misidentified as B.Mask, causing false 'missing Edge.Cuts' report; Inner copper layers GL2 and GL3 not parsed, layer_count reports only 2 copper layers found; Drill classificat...

- **Status**: promoted
- **Analyzer**: gerber
- **Source**: Hardware_Production
- **Created**: 2026-03-24

### Correct
- 1728 total holes: 1452 vias (0.3mm), 192 PTH component holes (1.016mm), 24 NPTH (0.65mm), 12 NPTH (2.3mm), 48 NPTH mounting holes (3.1mm). The 1452 vias at 0.3mm match the X2-attributed ViaPad flashes exactly. smd_ratio=0.92 is plausible. The panelized board has 12 copies of 4 mounting holes = 48, consistent with a 3×4 or 4×3 panel arrangement. Alignment passes with all layer extents coherent.
- The panelized gerber has 93 unique component refs: 50 real component refs, 41 kibuzzard decoration items. Pad counts per component are multiples of 12 (e.g. C1=24=2×12, U6=1200=100×12, J1=216=18×12), confirming a 12-up panel. This is consistent with the 48 NPTH mounting holes (4 per board × 12 panels). The total_pads=2844 divided by 12 = 237 pads per board copy, reasonable for this design. board_dimensions is empty but layer extents (139×163 mm) match a ~12-up panel at 40.64×40.64 mm per board.

### Incorrect
- The .GKO file (SparkFun_GNSS_DAN-F10N_panelized.GKO) contains the board outline and has a Profile aperture function entry in its aperture_analysis. However, its X2 FileFunction attribute reads 'Soldermask,Bot' (a KiCad quirk for panelized outputs). The analyzer maps layer_type from X2 FileFunction rather than from the .GKO file extension or the Profile aperture function. As a result, layer_type='B.Mask' is assigned to the board outline file, Edge.Cuts is reported missing_required, and complete=False. The same issue affects Flex_pHAT and LG580P gerber outputs. The Profile aperture function in the GKO file is the definitive indicator that this is the board outline.
  (completeness)

### Missed
- The Production directory contains GL2 and GL3 files (verified: X2 FileFunction 'Copper,L2,Inr' and 'Copper,L3,Inr'). Neither appears in the gerbers list in the output. found_layers shows only ['B.Cu', 'B.Mask', 'B.Paste', 'B.SilkS', 'F.Cu', 'F.Mask', 'F.Paste', 'F.SilkS'] — inner copper layers In1.Cu and In2.Cu are absent. The gerber analyzer does not scan .GL2/.GL3 extensions (or possibly does not parse them successfully), so a 4-layer board appears as 2-layer from the gerber perspective. This issue also affects Flex_pHAT and LG580P.
  (statistics)

### Suggestions
(none)

---
