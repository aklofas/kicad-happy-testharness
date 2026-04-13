# Findings: sparkfun/SparkFun_Qwiic_Fingerprint_Sensor_FPC2534 / Hardware_Production_SparkFun_Qwiic_Fingerprint_Sensor_FPC2534_panelized

## FND-00001449: Total component count of 45 is correct; Component type breakdown is accurate; LDO regulator U2 (RT9080-3.3) correctly detected; Decoupling capacitors on 3.3V and VBUS rails correctly identified; I2...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: Hardware_SparkFun_Qwiic_Fingerprint_Sensor_FPC2534.kicad_sch
- **Created**: 2026-03-24

### Correct
- The schematic has C×4, D×2, FID×4, G×3 (G1,G2,G3 in_bom=true), G4 (in_bom=false, OSHW logo), J×7, JP×5, R×12, ST×4, TP×1, U×2 = 45 total. The analyzer correctly counts 45 total_components.
- jumper:5, mounting_hole:4, other:4, resistor:12, fiducial:4, capacitor:4, connector:7, led:2, test_point:1, ic:2 — all verified against the BOM and component list.
- RT9080-3.3 is correctly identified as an LDO topology with input_rail=VBUS and output_rail=3.3V, matching the schematic. The fixed output voltage suffix extraction (3.3) is correct.
- C4 (1.0uF) and C5 (10uF) decoupling 3.3V, C2 (10uF) and C3 (1.0uF) decoupling VBUS, all correctly detected. Total 11uF per rail is accurate.
- All four power rails are correctly extracted. EGND is the analog/earth ground for the fingerprint sensor standoffs, distinct from digital GND — correct.
- J4 is correctly classified as a USB_C_Receptacle connector with DP and DM bidirectional nets, CC1/CC2 lines (pull-down resistors R2/R4 at 5.1k for UFP mode), and VBUS power. All pin assignments match the source schematic.
- TX and RX signals from U1 (FPC2534) to J7 are correctly detected in bus_analysis.uart. The sensor supports multiple interface modes including UART.
- 39 total nets matches the PCB net list, which also shows 39 nets. The net breakdown includes 4 power rails and various signal nets.
- G1 (qwiic_Logo) and G3 (SparkFun_Logo) both have empty footprint fields in the schematic. They are correctly listed in missing_footprint. G2 has a footprint assigned so it is correctly not listed.

### Incorrect
- The differential_pairs entry reports has_esd=true with U1 (FPC2534 fingerprint sensor) as the ESD protection device. U1 is the main fingerprint sensor IC, not an ESD protection device. There is no dedicated TVS diode or ESD protection IC on the USB data lines. The analyzer appears to count the IC connected to DP/DM as ESD protection, which is incorrect.
  (design_analysis)

### Missed
- The analyzer reports has_pullup=false for both SCL and SDA nets. However, R12 (2.2k) connects SCL to JP4 pin A, and R11 (2.2k) connects SDA to JP4 pin C. JP4 is a 3-pole solder jumper whose center pad (pin 2/B) connects to 3.3V. When JP4 is bridged (its default closed state), R11 and R12 serve as I2C pull-ups to 3.3V. The pull-up detection fails because the path goes through JP4 rather than a direct resistor-to-rail connection.
  (signal_analysis)
- The design has a clear SPI interface: ~{CS} (chip select), SCK (clock), POCI (peripheral out), PICO (peripheral in) — all connected between U1 (FPC2534 fingerprint sensor) and J5 (6-pin header). The bus_analysis.spi array is empty, indicating the SPI bus was not detected. This is likely because the signal names use POCI/PICO (IUPAC naming) rather than MISO/MOSI, and CS is active-low with tilde prefix.
  (design_analysis)
- CFG1 net: R6 (100k) pulls to GND and JP2/R5 (1k) can pull to 3.3V — forming a selectable pull-down configuration. CFG2 net: R7 (100k) to GND and JP3/R8 (1k) to 3.3V via jumper. These resistor pairs forming interface configuration dividers are not detected in signal_analysis.voltage_dividers (which is empty).
  (signal_analysis)

### Suggestions
(none)

---

## FND-00001450: PCB footprint count of 87 matches source file; 4-layer stackup correctly identified with named copper layers; Board dimensions 25.4mm × 25.4mm (1 inch square) correctly extracted; Routing completen...

- **Status**: promoted
- **Analyzer**: pcb
- **Source**: Hardware_SparkFun_Qwiic_Fingerprint_Sensor_FPC2534.kicad_pcb
- **Created**: 2026-03-24

### Correct
- The PCB contains 87 footprints total: standard components (C×4, D×2, FID×4, G4, J×7, JP×5, R×12, ST×4, TP×1, U×2 = 45) plus 42 kibuzzard decorative items. The analyzer correctly reports 87.
- The PCB uses F.Cu, In1.Cu, In2.Cu, B.Cu — a 4-layer stack. The analyzer correctly reports copper_layers_used=4. Layer names match the PCB file (In1.Cu used for GND zone and some signal routing, In2.Cu for EGND plane).
- Board outline is a rectangle from (123.266, 85.406) to (148.666, 110.806), giving width=25.4mm and height=25.4mm. This is a 1-inch square SparkFun Qwiic form factor.
- routing_complete=true, unrouted_net_count=0, 379 track segments with 57 vias. The connectivity section confirms 0 unrouted connections.
- The design uses dual ground domains: digital GND (zone on F.Cu, B.Cu, In1.Cu) and analog EGND for the fingerprint sensor housing (zone on In2.Cu). JP5 (BZL jumper) bridges EGND to GND and is correctly identified in multi_domain_components. U1 is also correctly listed as spanning both domains.
- Vias in pads of J1/J2 NC pins and R2/R4 CC-line resistors are flagged with same_net=false. These NC pad vias are correct routing artifacts for this densely packed 25.4×25.4mm board.
- The FPC2534 fingerprint sensor is on the back side (B.Cu) with a custom LGA-style footprint of 47 pads, correctly identified by the analyzer. This matches the physical design where the sensor attaches to the back of the board.
- All 57 vias are uniform through-hole vias with 0.56mm pad diameter and 0.3mm drill, correctly reported in vias.size_distribution.
- DP and DM nets each use 3 copper layers (B.Cu, F.Cu, In1.Cu) with 2 vias each, mostly routed on In1.Cu. This demonstrates correct differential pair routing practice through an inner layer.
- power_net_routing shows VBUS uses only 0.4064mm tracks on F.Cu with 19 segments. This is appropriate heavier trace width for the USB power bus. GND also correctly uses thicker traces (up to 0.4064mm).

### Incorrect
- The GND zone reports outline_area_mm2=645.16 but filled_area_mm2=1021.71, giving fill_ratio=1.584. A fill ratio above 1.0 is physically impossible for a single layer. This occurs because the zone spans 3 copper layers (F.Cu, B.Cu, In1.Cu) and the filled area appears to be the sum of fill across all layers rather than per-layer. This is a display/calculation artifact in the PCB analyzer zone reporting.
  (zones)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001451: GKO (outline/Edge.Cuts) file misidentified as B.Mask layer type; 4-layer gerber set correctly identified from B.Cu through F.Cu copper layers; Drill classification correctly separates vias (1425 × ...

- **Status**: promoted
- **Analyzer**: gerber
- **Source**: Hardware_Production
- **Created**: 2026-03-24

### Correct
- The gerber set includes F.Cu (L1,Top) and B.Cu (L4,Bot) confirmed via x2_attributes, correctly reporting layer_count=4. This matches the PCB stackup.
- 1425 via holes at 0.3mm via drill tool T1 (PTH, ViaDrill), 350 component holes at 1.016mm (T3), 100 at 3.1mm (T4), 50 NPTH at 0.65mm (T5), 25 NPTH at 2.3mm (T6). Total 1950 holes correctly reported.
- alignment.aligned=true with no issues. All copper layers (B.Cu and F.Cu) have identical extents (133.175×143.288mm), confirming the panelized board has consistent layer registration. The SilkS, Paste, and Mask layers have slightly smaller extents as expected.
- Total 13,237 flashes and 436,410 draws across 9 gerber files reflect a panelized board with 25 copies of the 25.4mm×25.4mm board. The high via count (1425 via flashes per copper layer) confirms this is a panel.
- trace_widths.min_trace_mm=0.1524mm with 5 unique widths (0.1524, 0.1778, 0.2616, 0.3048, 0.4064mm). These conductor widths are correctly identified from x2 aperture attributes in both B.Cu and F.Cu gerbers.
- pad_summary.smd_ratio=0.86 with 3206 SMD apertures vs 525 THT holes. The board is primarily SMD with some THT connectors and standoffs, which matches the design.

### Incorrect
- The file SparkFun_Qwiic_Fingerprint_Sensor_FPC2534_panelized.GKO has layer_type='B.Mask' and x2_attributes showing FileFunction='Soldermask,Bot'. The .GKO extension conventionally denotes Edge.Cuts/board outline, and the aperture_analysis shows 'Profile' aperture function indicating this is the board outline. The layer_type and x2 attributes are likely being read from the previous file's x2 context or the GKO file contains incorrect x2 data. This causes Edge.Cuts to appear in missing_required incorrectly.
  (completeness)
- drill_tools shows '0.6mm' with count=0. The drill file defines tool T2 with diameter=0.6mm but zero actual hole placements. This is likely a tool defined in the Excellon header but never used, or it maps to a different tool after the 0.65mm NPTH tool was added. This anomaly should be flagged but the analyzer accepts it silently.
  (drill_classification)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001452: Panelized PCB has inflated component count relative to single board

- **Status**: new
- **Analyzer**: pcb
- **Source**: SparkFun_Qwiic_Fingerprint_Sensor_FPC2534_panelized.kicad_pcb
- **Created**: 2026-03-24

### Correct
- The panelized PCB has 82 unique component references in the gerber component_analysis (vs 45 schematic components on single board plus kibuzzard items). The panel multiplies the board copies and the analyzer correctly processes this as a distinct file from the single-board PCB.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
