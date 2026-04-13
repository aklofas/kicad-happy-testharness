# Findings: sparkfun/SparkFun_UM980_Triband_GNSS_RTK_Breakout / Hardware_Production_SparkFun_GNSS_UM980_panelized

## FND-00001575: Board outline not extracted: gr_poly on Edge.Cuts produces edge_count=0 and bounding_box=null; Board width and height null despite valid Edge.Cuts polygon

- **Status**: promoted
- **Analyzer**: pcb
- **Source**: Hardware_SparkFun_GNSS_UM980.kicad_pcb
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
(none)

### Missed
- The PCB has a single gr_poly shape on the Edge.Cuts layer defining a non-rectangular 50.8mm x 50.8mm board outline (with a notch, 8 vertices). The analyzer does not parse gr_poly as a board edge, so board_outline.edge_count=0, board_outline.bounding_box=null, and statistics.board_width_mm/board_height_mm are null. The panelized PCB correctly extracts its outline (uses gr_line segments), confirming the parser only handles gr_line, not gr_poly, for Edge.Cuts.
  (board_outline)
- statistics.board_width_mm and board_height_mm are null because the gr_poly on Edge.Cuts is not parsed. The actual board is approximately 50.8mm x 50.8mm (bounding box of the polygon vertices).
  (statistics)

### Suggestions
(none)

---

## FND-00001576: Inner copper layers GL1 (In1.Cu) and GL2 (In2.Cu) not parsed or reported; GKO (Edge.Cuts) gerber file is processed but not mapped to a named layer; Gerber layer alignment verified and SMD pad ratio...

- **Status**: promoted
- **Analyzer**: gerber
- **Source**: 
- **Created**: 2026-03-24

### Correct
- alignment.aligned=true with no issues reported across the 8 recognized layers. The SMD ratio of 0.93 is consistent with a mostly-SMD board (66 SMD vs 6 THT in the PCB output). Drill classification correctly identifies vias (568 at 0.305mm and 0.4mm), component holes (84), and mounting NPTH holes (16 at 3.302mm).

### Incorrect
(none)

### Missed
- The Production directory contains a 4-layer panelized design with gerbers including SparkFun_GNSS_UM980_panelized.GL1 and .GL2 for inner copper layers. The analyzer reports only 9 gerber files processed and found_layers contains only ['B.Cu','B.Mask','B.Paste','B.SilkS','F.Cu','F.Mask','F.Paste','F.SilkS'] — no In1.Cu or In2.Cu. The missing inner copper layers are not flagged in missing_required or missing_recommended, so a 4-layer board effectively appears as 2-layer to the analysis.
  (completeness)
- SparkFun_GNSS_UM980_panelized.GKO is the board outline (Edge.Cuts) gerber using the legacy KiCad extension. The analyzer parses it (contributing to gerber_files=9) but does not map it to 'Edge.Cuts' — the layer does not appear in found_layers or layer_extents. completeness.missing_required=['Edge.Cuts'] correctly reports it as missing, but the cause is the extension not being recognized as Edge.Cuts, not an absent file.
  (completeness)

### Suggestions
(none)

---

## FND-00001577: RF signal chain (SMA antenna connector to UM980 RF input) not detected in rf_chains or rf_matching; bus_topology reports width=7 for 3-signal UART groups RXD1..RXD3 and TXD1..TXD3; cross_domain_sig...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: Hardware_SparkFun_GNSS_UM980.kicad_sch
- **Created**: 2026-03-24

### Correct
- signal_analysis.power_regulators correctly identifies U2 as an LDO with input_rail='+5V', output_rail='3.3V', and estimated_vout=3.3V (inferred from the '-3.3' suffix). The separate 3.3V_A rail for the UM980 GNSS IC is correctly understood as a filtered derivative of 3.3V via the L2 ferrite bead — the decoupling_analysis correctly groups C15/C16/C17 under 3.3V_A.
- usb_compliance.connectors[0].checks shows cc1_pulldown_5k1=pass, cc2_pulldown_5k1=pass, and usb_esd_ic=pass. R1 and R2 are both 5.1k resistors on CC1 and CC2 respectively (correct for USB-C device/sink advertisement), and U1 (DT1042-04SO) is correctly identified as the USB ESD protection IC.
- bus_analysis.i2c correctly identifies SDA and SCL pins on U5 with has_pull_up=false and pull_ups=[]. The UM980's I2C interface is unused in this design (SPI_SDA/SPI_SCL are marked as unconnected in the schematic with unconnected net names), so the missing pull-up observation is accurate.

### Incorrect
- The bus_topology.detected_bus_signals shows prefix='RXD', width=7, range='RXD1..RXD3' and prefix='TXD', width=7, range='TXD1..TXD3'. There are exactly 3 RXD signals (RXD1, RXD2, RXD3) and 3 TXD signals (TXD1, TXD2, TXD3) in the design. The width=7 is incorrect; the expected value is 3 for a 3-port UART group. The range string is correctly computed but the width field contains an erroneous value.
  (bus_topology)
- design_analysis.cross_domain_signals reports that D+ and D- cross power domains (+5V for U1 vs 3.3V for U8) and sets needs_level_shifter=true. U1 (DT1042-04SO) is a 4-channel unidirectional TVS ESD protection diode array — it is a passive clamp device, not a domain-crossing active IC. It has a VBUS pin connected to +5V for correct clamping voltage, but its I/O paths are bidirectional 15pF clamps regardless of VCC domain. No level shifter is needed or appropriate here. usb_compliance.usb_esd_ic=pass correctly identifies U1 as the USB ESD IC, contradicting the cross_domain needs_level_shifter claim.
  (design_analysis)
- U7 uses library SparkFun-Aesthetic:Ordering_Instructions — it is a graphical annotation footprint containing PCB ordering notes, not a real IC. The analyzer classifies it as type='ic', inflating the IC count to 5 (true functional ICs are U1, U2, U5, U8 = 4). It also appears in statistics.component_types.ic count and missing_mpn. The correct type is 'other' (as used for G1 OSHW_Logo and G3/G5 SparkFun_Logo components).
  (statistics)
- signal_analysis.design_observations contains entries for 'usb_data' category with net='D+' and net='D-', both reporting has_esd_protection=false and listing devices=[U8,U1,J1,J1]. U1 (DT1042-04SO) is explicitly an ESD protection IC for USB differential lines. usb_compliance.connectors[0].checks.usb_esd_ic='pass' correctly identifies U1. The two outputs are internally inconsistent; the design_observations value is wrong.
  (signal_analysis)

### Missed
- The schematic includes a complete RF antenna input path: J5 (SMA edge connector) -> Net-(D6-A2) -> C7 (100pF DC-blocking capacitor) -> ANT_IN -> U5 (UM980 GNSS IC). L1 (68nH inductor) connects the ANT_BIAS rail to the same RF node for active antenna bias injection. D6 (PESD0402 TVS) provides ESD protection on the RF node. C4+C6 form additional filtering on ANT_BIAS. The signal_analysis.rf_chains and rf_matching arrays are both empty — this is a significant missed detection for a GNSS receiver design.
  (signal_analysis)

### Suggestions
- Fix: U7 (SparkFun-Aesthetic:Ordering_Instructions) classified as type='ic' instead of 'other'

---

## FND-00001854: Component inventory and BOM extraction are accurate; AP2112K-3.3 LDO regulator correctly detected with input/output rails; CH340C USB-UART bridge function correctly identified; ESD protection devic...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: Hardware_SparkFun_GNSS_UM980.kicad_sch
- **Created**: 2026-03-24

### Correct
- All 83 components across 14 type categories are correctly identified and counted: 25 resistors, 13 capacitors, 8 jumpers, 6 connectors, 5 ICs, 5 diodes, 4 mounting holes, 4 fiducials, 4 LEDs, 3 other/aesthetic, 2 inductors, 2 test points, 1 fuse, 1 battery. The sum of component_types matches total_components exactly.
- U2 is correctly identified as an LDO regulator with input_rail '+5V', output_rail '3.3V', estimated_vout 3.3V from the fixed suffix. Topology is correctly inferred as LDO.
- U8 CH340C is correctly identified as a 'USB-UART bridge' in ic_pin_analysis. UART nets RXD1/TXD1 are correctly associated with U8.
- All three quadruple ESD protection arrays are correctly detected in protection_devices with their protected nets: D9 protects RXD2/RXD3/TXD2/TXD3, D10 protects EVENT/PPS/PVT_STAT/RTK_STAT, D11 protects ERR_STAT/V_ANT_EXT/RESET.
- 3.3V_A has 3 caps (44.1uF total: 2x22uF bulk + 0.1uF bypass), 3.3V has 5 caps (3.3uF: 2.2uF + 1uF + 0.1uF + 2x100pF), +5V has 1 cap (0.1uF). The has_bulk/has_bypass/has_high_freq flags are accurate.
- The differential pair analysis correctly identifies the USB D+/D- pair shared across J1 (USB-C), U1 (ESD clamp), and U8 (CH340C), and flags has_esd: True with esd_protection: ['U8', 'U1'].
- R7 (1k) and C3 (1uF) form an RC low-pass filter at 159.15 Hz on the V_BCKP net, which is the backup battery trickle supply for the UM980. The filter is correctly identified with correct cutoff frequency.
- L1 (inductor) uses a capacitor footprint C_0402, D6 (TVS diode) uses a capacitor footprint C_0402, and JP1 jumper footprint Jumper_3_NC-1_Trace does not match the SolderJumper*Bridged12* filter pattern. All three footprint mismatches are correctly flagged.

### Incorrect
- design_observations contains two entries with category 'usb_data' and has_esd_protection: false for both D+ and D-. However, U1 (DT1042-04SO) is a dedicated 4-channel USB ESD protection IC whose I/O3 and I/O4 pins connect directly to D- and D+. The differential_pairs analysis correctly shows has_esd: True with esd_protection: ['U8', 'U1']. The two analyses are inconsistent — the usb_data observation is incorrect.
  (signal_analysis)
- cross_domain_signals flags D+ and D- as needing level shifters because U1 is powered from +5V while U8 is on 3.3V. However, U1 (DT1042-04SO) is a passive ESD clamp — it uses VCC merely as a clamping reference and does not drive the USB data lines. There is no voltage level translation concern on the USB data path between U1 and U8; the USB signal swings are determined by the USB host and CH340C, not by U1's VCC pin.
  (design_analysis)
- U5 is a UM980 triband GNSS RTK receiver, but ic_pin_analysis reports function as an empty string. The lib_id is 'SparkFun-GPS:UM980' and the description field is also empty in the schematic. The analyzer could infer the GNSS function from the lib_id path containing 'GPS' or from the part name 'UM980', but does not do so.
  (ic_pin_analysis)

### Missed
- The L1 (68nH) + D6 (TVS) + C4/C6/C7 (100pF/100pF bypass) arrangement on VCC_RF → ANT_BIAS → antenna is a classic bias-T for active antenna powering, which is an RF-specific circuit pattern. This is detected as generic LC filters (resonant 1.93 MHz and 61 MHz) but not as an rf_chains or rf_matching entry. The rf_chains and rf_matching arrays are both empty.
  (signal_analysis)
- 3.3V_A is the analog power domain for the UM980 GNSS core, filtered from 3.3V through L2 (30Ohm ferrite bead, MPZ1608 series). The ferrite bead forms a low-pass power filter separating the analog rail. No power_regulator or LC filter entry captures this relationship. L2 is parsed with parsed_value=30.0 (numeric ohms treated as henries by the value parser), which could cause confusion in LC filter calculations.
  (signal_analysis)
- The design_observations note that VCC_RF has no decoupling caps on U5, but VCC_RF powers the antenna bias via L1+C4+C6. The decoupling_analysis lists these caps under ANT_BIAS not VCC_RF. The observation 'rails_without_caps: [VCC_RF]' is technically correct from the U5 perspective but misleading — the design uses an off-IC bias-T topology.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00001855: GKO (Edge.Cuts) file misclassified as B.Mask layer type

- **Status**: promoted
- **Analyzer**: gerber
- **Source**: SparkFun_GNSS_UM980_panelized.GKO
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
- The gerber analyzer assigns layer_type 'B.Mask' to SparkFun_GNSS_UM980_panelized.GKO because it reads the X2 TF.FileFunction attribute which incorrectly says 'Soldermask,Bot' in the GKO file itself. The GKO file is actually the board outline (Edge.Cuts / Profile layer), as confirmed by the %TA.AperFunction,Profile% aperture in its content. Consequently, completeness.missing_required includes 'Edge.Cuts' and completeness.complete is false — both are wrong. The GKO file is present and correctly outlines the board; the misclassification stems from a KiCad 7.0.6 export bug where GKO was given the wrong FileFunction X2 attribute.
  (completeness)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001856: Inner copper layer gerbers GL1 (In1.Cu) and GL2 (In2.Cu) not processed

- **Status**: promoted
- **Analyzer**: gerber
- **Source**:  (GL1, GL2 files)
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
(none)

### Missed
- The production directory contains SparkFun_GNSS_UM980_panelized.GL1 (FileFunction: Copper,L2,Inr) and SparkFun_GNSS_UM980_panelized.GL2 (FileFunction: Copper,L3,Inr) for the two inner copper layers of the 4-layer board. The gerber output shows only 9 gerber files (F.Cu, B.Cu, F/B Mask, F/B Silk, F/B Paste, GKO/outline). GL1 and GL2 are missing from the gerbers list, meaning the inner layer copper analysis is absent. The completeness.found_layers list should also include In1.Cu and In2.Cu.
  (completeness)

### Suggestions
(none)

---

## FND-00001857: Board outline (Edge.Cuts gr_poly) not parsed — board_width_mm and board_height_mm are null; 4-layer stackup correctly identified with all copper layer names; GND copper pour zone across all 4 layer...

- **Status**: promoted
- **Analyzer**: pcb
- **Source**: Hardware_SparkFun_GNSS_UM980.kicad_pcb
- **Created**: 2026-03-24

### Correct
- copper_layers_used: 4 and copper_layer_names: [B.Cu, F.Cu, In1.Cu, In2.Cu] correctly reflect the 4-layer design. The detailed stackup with prepreg thicknesses (0.1mm) and core (1.24mm FR4) matching a standard 1.6mm board is correctly extracted.
- The single copper zone is correctly identified as GND net, spanning all four copper layers [F.Cu, In1.Cu, In2.Cu, B.Cu] with clearance 0.1778mm and thermal relief 0.1778mm. The filled_area_mm2: 8490.96 indicates a large poured region.
- statistics.routing_complete: true and unrouted_net_count: 0 are correct for the SparkFun_GNSS_UM980.kicad_pcb. The board has 427 track segments, 142 vias, and 1047.83mm total track length.
- 62 kibuzzard-prefixed footprints are correctly flagged as board_only: true, exclude_from_bom: true, exclude_from_pos: true with zero pads. These are SparkFun's decorative PCB art elements.
- trace_widths correctly identifies five distinct widths: 0.1778mm (7mil signal), 0.25mm, 0.349mm (13.74mil coplanar waveguide for GNSS RF per schematic annotation), 0.4064mm, 0.5588mm (22mil power). The schematic text annotation documents the RF trace as 13.74mil/0.349mm for 50-ohm coplanar waveguide.

### Incorrect
- The PCB contains one Edge.Cuts element: a gr_poly with 8 vertices forming the USB connector notch cutout outline (approximately 50.8 × 50.8 mm based on coordinates 101.6–152.4 in both axes). The board_outline reports edge_count: 0, edges: [], bounding_box: null, and statistics.board_width_mm and board_height_mm are both null. The analyzer appears to handle only gr_line and gr_arc for Edge.Cuts, missing gr_poly.
  (statistics)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001858: Antenna sub-circuit components correctly extracted: 7 components, 6 nets; Single-pin global label nets correctly identified in antenna sub-schematic

- **Status**: new
- **Analyzer**: schematic
- **Source**: Hardware_UM980_antenna.kicad_sch
- **Created**: 2026-03-24

### Correct
- L1 (68nH inductor), C4 (0.1uF), C6/C7 (100pF x2), D6 (PESD0402 TVS), JP1 (3-pole solder jumper), J5 (SMA edge connector) are all correctly identified. LC filter between L1 and C7 (61 MHz resonance) and bias-T filter with L1+C4+C6 (1.93 MHz resonance) are detected.
- VCC_RF, ANT_IN, ANT_BIAS, V_ANT_EXT appear as single-pin nets in the antenna schematic because their other endpoints are in the root schematic. This is correct per-sheet behavior — each of these 4 global labels connects to multiple nets across the hierarchical design.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001859: Connector sub-schematic correctly identifies UART2/UART3 buses and ESD protection

- **Status**: new
- **Analyzer**: schematic
- **Source**: Hardware_UM980_connectors.kicad_sch
- **Created**: 2026-03-24

### Correct
- 10 components correctly identified: 4 connectors (J4/J6/J7/J8), 3 ESD arrays (D9/D10/D11 PESD3V3L4UG), 2 jumpers (JP6/JP8), 1 resistor (R8). UART bus analysis correctly detects RXD2/TXD2/RXD3/TXD3 nets. Power rails +5V, 3.3V, GND are correct.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001860: Panelized PCB board dimensions and Edge.Cuts correctly extracted

- **Status**: new
- **Analyzer**: pcb
- **Source**: SparkFun_GNSS_UM980_panelized.kicad_pcb.json
- **Created**: 2026-03-24

### Correct
- The panelized PCB correctly reports board_width_mm: 121.896, board_height_mm: 115.8, edge_count: 8, and routing_complete: false (the panel has unrouted nets from board-to-board connections). Footprint_count: 584 reflects 4 panel copies.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001861: Drill file classification correctly separates vias, component holes, and mounting holes

- **Status**: new
- **Analyzer**: gerber
- **Source**: SparkFun_GNSS_UM980_panelized.drl
- **Created**: 2026-03-24

### Correct
- 568 via holes (T1: 0.305mm x564, T2: 0.4mm x4), 76 component holes (T4: 0.95mm x8 PTH, T5: 1.016mm x68 PTH), 8 NPTH component holes (T6: 0.65mm), and 16 NPTH mounting holes (T7: 3.302mm) are correctly classified. Mixed file correctly noted as spanning layers 1-4.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
