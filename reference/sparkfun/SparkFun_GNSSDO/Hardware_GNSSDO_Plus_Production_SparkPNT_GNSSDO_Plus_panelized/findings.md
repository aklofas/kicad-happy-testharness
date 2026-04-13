# Findings: sparkfun/SparkFun_GNSSDO / Hardware_GNSSDO_Plus_Production_SparkPNT_GNSSDO_Plus_panelized

## FND-00001812: Total component count (296) correct for hierarchical GNSSDO design; key_matrix detected for independent panel switches sharing SD card net names; component_types miscounts relay:1 and transformer:1...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: Hardware_GNSSDO_SparkPNT_GPSDO.kicad_sch.json
- **Created**: 2026-03-24

### Correct
- The flat hierarchical analysis of the KiCad 8.0 root schematic correctly aggregates all sub-sheets (GNSS, Ethernet, Power, USB, Level_Shifting, Level_Shifting_10MHz) plus root-level components to 296 total components. Sub-sheets sum to 247, and the remaining 49 are root-level standoffs, test points, fiducials, and direct components.
- The ethernet_interfaces section correctly identifies U4 (KSZ8041NL/I Ethernet PHY) with connector J5 (MagJack_PoE_RJ45). The PHY lib_id and value are correctly captured. This is also correctly detected in the Ethernet sub-schematic.
- U13 (SiT5358AI-FS033IT-10.000000) is correctly identified as an active_oscillator in crystal_circuits with output_net captured. The 10 MHz TCXO/oscillator module is properly classified.
- The isolation_barriers correctly identifies two ground domains (GND and GND-ISO) from the PoE isolation circuit. The isolated_power_rails lists GND-ISO. The isolation_components list being empty is acceptable since the galvanic isolation is embedded within the MagJack (transformer inside connector body).
- U11 (AP7361C-3.3V) detected as LDO outputting 3.3V from 5V input, and U5 (AP7361C-3.3V) detected as LDO outputting 3.3V_P from 5V input. Both correctly identified via fixed-suffix vref_source. The third regulator U7 (Ag9905M) has unknown topology as expected for a PoE PD controller.
- 11 protection devices correctly identified: DT1042-04SO multi-channel ESD ICs protecting USB and Ethernet differential pairs, DF5A5.6LFU arrays on SD card and I2C lines, PESD0402 TVS diodes on RF and external signal lines, a varistor (V.1) on the DC input, and F1 fuse. Classification as esd_ic, diode, varistor, and fuse types is accurate.

### Incorrect
- The signal_analysis.key_matrices detects 1 key matrix (2 rows, 3 columns, 4 switches) with row_nets=['SD_CMD', '__unnamed_43']. SD_CMD is an SD card SPI signal, not a matrix row. SW1–SW3 are SPST push buttons (panel controls from USB sub-sheet) and SW4 is a DPDT slide switch (from Level_Shifting sub-sheet). These are independent control switches, not a scanning keyboard matrix. The coincidence of SD card net names and switch passive nets triggers a false topological match.
  (signal_analysis)
- SparkFun uses single-letter + dot-number reference designators (A.1, B.1, …, K.1, L.1, T.1, V.1) for solder jumper test pads. The analyzer classifies components by reference prefix: K.1 (a SolderJumper_2_Open) is counted as relay, T.1 (a SolderJumper_2_Open in Level_Shifting_10MHz) is counted as transformer, and L.1 (a SolderJumper_2_Open) is counted as inductor in component_types statistics. All three are actually solder jumpers. The BOM partially compensates by grouping some under varistor (V.1, K.1, L.1 grouped together), creating an inconsistency between statistics and BOM type fields. The correct counts should have relay:0, transformer:0, and jumper increased accordingly.
  (statistics)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001813: STP3593LF OCXO not detected as active oscillator in GNSSDO Plus; U5 (AP7361C-3.3V) output rail misidentified as 3.3V instead of 3.3V_P in top-level flat analysis; GNSSDO Plus: 9 transistor circuits...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: Hardware_GNSSDO_Plus_SparkPNT_GNSSDO_Plus.kicad_sch.json
- **Created**: 2026-03-24

### Correct
- 8 transistor circuits correctly identified as PMOS MOSFETs (DMG2305UX). Q2/Q4 driven by U26 (LTC4418), Q6/Q8 driven by U27 (LTC4418) are correctly attributed. Q3/Q5/Q7/Q9 have unnamed gate nets (internal LTC4418 analog control) — no gate_driver_ic is listed for these but this is expected since they are driven by unnamed intermediate nodes. The transistor count of 9 (including Q1 from PowerPath) is consistent with the design.
- Statistics reports total_components=353, dnp_parts=9. The 9 DNP parts are all 1.0nF bypass capacitors (C51, C64, C66, C67, C75, C76, C82, C87, C88) populated optionally. The GNSSDO original has dnp_parts=0. Both are confirmed correct by cross-referencing BOM entries.

### Incorrect
- In the top-level flat hierarchical analysis, U5 output_rail is detected as '3.3V' instead of the correct '3.3V_P'. The Power sub-schematic (analyzed in isolation) correctly identifies U5 output as '3.3V_P'. The GNSSDO original (same topology) also correctly identifies U5 output as '3.3V_P'. The error is introduced by the hierarchical flattening process in the Plus design, likely due to net scope resolution differences between the two AP7361C instances.
  (signal_analysis)
- U7 (DP5305) is a USB Power Delivery protocol controller IC, not a power regulator. It negotiates USB-PD voltage profiles rather than regulating voltage directly. Classifying it as a power_regulator with topology=unknown is imprecise. However, since the topology is clearly 'unknown' rather than LDO/buck/boost, the practical impact is limited to the regulator list being inflated by 1 non-regulator entry.
  (signal_analysis)

### Missed
- crystal_circuits is empty (0 items) in the GNSSDO Plus top-level schematic and in the Oscillator sub-schematic. U13 (STP3593LF) is an oven-controlled crystal oscillator (OCXO) module — a high-precision active oscillator. The analyzer fails to recognize STP3593LF as an oscillator, likely because the part name does not match known oscillator patterns (e.g., no 'OSC', 'TCXO', 'SiT', 'XTAL' in the name). It should be detected similarly to the SiT5358 in the GNSSDO original.
  (signal_analysis)

### Suggestions
- Fix: DP5305 USB PD controller classified as power_regulator with unknown topology

---

## FND-00001814: Oscillator sub-schematic correctly reports 21 components: STP3593LF OCXO, JPS-3-1+ buffer, PCA9306 level-shifter

- **Status**: new
- **Analyzer**: schematic
- **Source**: Hardware_GNSSDO_Plus_Oscillator.kicad_sch.json
- **Created**: 2026-03-24

### Correct
- The Oscillator sub-schematic correctly identifies all 21 components including U13 (STP3593LF OCXO), U16 (JPS-3-1+ clock buffer/fan-out), and U19 (PCA9306 I2C level-shifter). Component types are all classified as ic (3), resistor (7), capacitor (6), jumper (2), test_point (3). The design_observations correctly flags the 3 single-pin nets on U16 PORT1/PORT2/PORT3 (10MHz output ports that only connect to hierarchical labels).

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001815: 4-layer PCB correctly identified with complete routing (0 unrouted nets); Dual ground domain isolation correctly detected (GND and GND-ISO) with zone coverage; Thermal pad vias correctly identified...

- **Status**: new
- **Analyzer**: pcb
- **Source**: Hardware_GNSSDO_SparkPNT_GPSDO.kicad_pcb.json
- **Created**: 2026-03-24

### Correct
- PCB statistics correctly reports copper_layers_used=4 with layers [B.Cu, F.Cu, In1.Cu, In2.Cu], routing_complete=True, unrouted_net_count=0. The board dimensions 151.9×101.6 mm (approximately 6×4 inches) are correctly captured. Total 438 footprints including 139 kibuzzard annotation overlays from SparkFun's board documentation tool.
- ground_domains correctly identifies 2 domains: GND (136 components, zone on all 4 copper layers) and GND-ISO (2 components including the PoE MagJack J5). The multi_domain_components list correctly identifies C9 as bridging both domains (an isolation coupling capacitor). This accurately reflects the PoE galvanic isolation architecture.
- thermal_analysis.thermal_pads correctly identifies 3 components with thermal pads: U4 (KSZ8041 PHY, 9.92mm² GND pad with 1 nearby via), U11 (AP7361C LDO, 3.76mm² pad with 13 vias), U5 (AP7361C LDO, 3.76mm² pad with 14 vias). The zone_stitching correctly identifies GND (440 vias), VIN+ (12 vias), and VIN- (15 vias) zones with via density metrics.
- dfm correctly reports dfm_tier=standard, min_track_width_mm=0.1778 (7mil), approx_min_spacing_mm=0.1796, min_drill_mm=0.3. These are within typical standard fabrication capabilities. violation_count=1 is reported (likely a minor spacing issue). The metrics are consistent with the KiCad design rules used in the PCB file.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001816: GNSSDO Plus PCB: 472 footprints, 880 vias, fully routed 4-layer board at same dimensions

- **Status**: new
- **Analyzer**: pcb
- **Source**: Hardware_GNSSDO_Plus_SparkPNT_GNSSDO_Plus.kicad_pcb.json
- **Created**: 2026-03-24

### Correct
- GNSSDO Plus PCB correctly shows footprint_count=472 (vs 438 for original, due to more kibuzzard annotations and additional components), via_count=880 (vs 692 for original, reflecting higher density), routing_complete=True, and same board dimensions 151.9×101.6 mm. The higher via count reflects the more complex power path and additional ICs.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001817: Inner copper layers GL2/GL3 (In1.Cu, In2.Cu) not detected in found_layers despite correct TF.FileFunction headers; Drill files missing from gerber analysis despite 816 plated through-holes existing...

- **Status**: promoted
- **Analyzer**: gerber
- **Source**: Hardware_GNSSDO_Production.json
- **Created**: 2026-03-24

### Correct
- alignment.aligned=True with no issues reported. The layer extents show consistent board dimensions across B.Cu, B.Mask, B.Paste, B.SilkS, F.Cu, F.Mask, F.Paste, F.SilkS. This is correct — the panelized gerbers are properly registered.

### Incorrect
(none)

### Missed
- The 4-layer panelized gerber set includes SparkPNT_GPSDO_panelized.GL2 (TF.FileFunction=Copper,L2,Inr) and SparkPNT_GPSDO_panelized.GL3 (TF.FileFunction=Copper,L3,Inr), but completeness.found_layers only lists the 8 outer layers [B.Cu, B.Mask, B.Paste, B.SilkS, F.Cu, F.Mask, F.Paste, F.SilkS]. The inner copper layers are not mapped to In1.Cu/In2.Cu in the found_layers list, causing the gerber analyzer to report only 2 copper layers for a confirmed 4-layer board. This is a gerber analyzer bug where GL2/GL3 extensions with Copper,L2,Inr and Copper,L3,Inr TF.FileFunction are not being translated to KiCad layer names.
  (completeness)
- The drill_report.rpt in the production folder documents 816 plated through-holes (T1-T10 with sizes from 0.3mm to 1.7mm) plus additional NPTH holes. The gerber analyzer reports drills=[] (0 drill files), total_holes=0. The production folder only contains a .drl file referenced in the drill report but no .drl file is physically present — the gerbers were exported without drill files. The analyzer correctly reports has_pth_drill=False and has_npth_drill=False since no Excellon drill files exist in the directory, which is accurate. However, completeness.complete=False with missing_required=['Edge.Cuts'] is partially misattributed — the real completeness issue is missing drill files, not just Edge.Cuts.
  (completeness)
- SparkPNT_GPSDO_panelized.GKO contains board profile/edge cuts data (apertures have TA.AperFunction=Profile) but its TF.FileFunction attribute was incorrectly set to 'Soldermask,Bot' by the panelizer tool. The gerber analyzer correctly reads TF.FileFunction and cannot distinguish the wrong metadata from the actual aperture function. This is a panelizer tool bug (not an analyzer bug), but results in Edge.Cuts being listed as missing_required and completeness.complete=False. The board outline IS present in the file content.
  (completeness)

### Suggestions
(none)

---

## FND-00001818: GNSSDO Plus production gerbers show identical structural issues as GNSSDO original (expected)

- **Status**: new
- **Analyzer**: gerber
- **Source**: Hardware_GNSSDO_Plus_Production.json
- **Created**: 2026-03-24

### Correct
- The Plus panelized gerber set shows the same structural characteristics: 9 gerber files found, drills=0, missing Edge.Cuts (same GKO/TF.FileFunction bug), GL2/GL3 inner layers not in found_layers. Layer alignment is correct (aligned=True). The KiCad 9.0.1 generator version is correctly captured vs 8.0.5 for the original. component_analysis shows front=315, back=62 vs original front=339, back=61, correctly reflecting a different component distribution.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
