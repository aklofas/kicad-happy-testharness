# Findings: SparkFun_Soft_Power_Switch_Mk2 / Hardware_Production_Soft_Power_Switch_panelized

## FND-00001457: Component counts are accurate: 40 total, correct breakdown by type; Power rails correctly identified as GND, VIN, VOUT; Net count is accurate at 25 nets; Decoupling capacitors correctly detected on...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: Hardware_Soft_Power_Switch.kicad_sch
- **Created**: 2026-03-24

### Correct
- The schematic reports 40 total components matching the source: 10 resistors (R1-R10), 4 capacitors (C1-C4), 3 transistors (Q1-Q3), 3 ICs (U2, U3, U4), 3 connectors (J1-J3), 2 LEDs (D2, D3), 1 diode (D1), 1 fuse (F1), 1 switch (SW1), 2 jumpers (JP1, JP2), 4 fiducials (FID1-FID4), 4 standoffs (ST1-ST4), 1 logo (G1), and 1 OSHW logo (G3 with in_bom=false). All type categorizations match the source library identifiers.
- The schematic correctly identifies three power rails: GND, VIN, and VOUT. This matches the design: J1/J2 are LiPo battery connectors (VIN input), Q3 (SIL2308 dual MOSFET) provides the switched output (VOUT), and GND is the common return. The VIN net fans out to U2, U3, U4 VCC pins and also serves as the D input to U4 flip-flop.
- The schematic reports 25 total nets. The named nets are: GND, VIN, VOUT, BTN, EN, OFF, PUSH, BTN and unnamed nets __unnamed_0 through __unnamed_17 (18 unnamed). This matches the structure in the source — the design uses many local, unnamed nets between discrete components in the soft-power-switch logic chain.
- The ic_pin_analysis section correctly identifies C3 (1.0uF) and C4 (0.1uF) on the VIN rail as decoupling capacitors for U2, U3, and U4. The has_decoupling_cap flag is correctly set to true for all VCC pins. C1 (1.0uF) is correctly identified as filtering for the BTN signal line rather than a VCC decoupling cap.
- The schematic correctly detects that G1 (SparkFun_Logo) has an empty footprint field. The source schematic shows G1 with lib_id SparkFun-Aesthetic:SparkFun_Logo and an empty footprint property, making missing_footprint detection accurate.
- All 10 resistors (R1-R10) are correctly identified: R1, R6, R8, R9 at 1k; R3, R4, R7 at 10k; R2 at 200k; R5 at 100; R10 at 100k. Parsed_value fields are numerically correct (1000.0, 10000.0, 200000.0, 100.0, 100000.0). This matches the BOM entries and the source schematic.
- F1 (6V/2.0A/4.0A resettable PPTC fuse) is correctly categorized as type 'fuse' with the correct BOM row showing it on the VIN path. The net analysis shows F1 connecting from a pre-VIN node to the VIN rail, correctly reflecting the series protection topology.
- The subcircuits section correctly groups U4 (SN74LVC1G175DCK D-flip-flop) with its nearest-neighbor ICs U2 (Schmitt inverter) and U3 (Schmitt buffer), along with the R8 and R9 series resistors. This accurately reflects the topology where U2 generates the clock edge and U3 drives the asynchronous clear, both feeding into U4.

### Incorrect
- G1 (SparkFun_Logo) is listed in missing_mpn. In the source schematic it has in_bom=true but represents a graphical logo element that has no assembly part. This is technically correct (the MPN field is empty) but the part is a graphical symbol, not a component requiring an MPN. The OSHW logo (G3) is correctly excluded from missing_mpn because it has in_bom=false. G1 should ideally also have in_bom=false — the analyzer correctly captures the schematic data as-is, but this is a design inconsistency that could be flagged.
  (statistics)

### Missed
- The signal_analysis section has no voltage_dividers array. The design has notable resistor networks: R7 (10k) pulls the OFF signal low to GND; R6 (1k) is in series on the OFF net forming a classic pull-down with voltage dividing. Similarly, R2 (200k) from BTN to the timing node and R1 (1k) pull-up to VIN form a potential divider for the Schmitt trigger input threshold detection. These should be candidates for voltage divider detection. The schematic output does not include a signal_analysis section at all, suggesting it may not run the voltage divider detector on this design.
  (signal_analysis)
- D1 (BAS16J) is a fast-switching diode connected in the BTN signal path with its anode on BTN and cathode going to the timing capacitor C2 node. In the context of this soft-power circuit, D1 acts as a signal steering diode (not a Zener or TVS protection diode), but the circuit topology — D1 allowing current from BTN to charge the timing capacitor while preventing discharge back through BTN — is a diode steering/protection pattern. The analyzer correctly categorizes D1 as 'diode' type but the signal_analysis section does not flag any protection device detection.
  (statistics)

### Suggestions
(none)

---

## FND-00001458: PCB footprint count of 63 is correct including board-only kibuzzard/logo footprints; Board dimensions accurately reported as 25.4mm x 25.4mm (1 inch square); Via count of 47 matches drill file data...

- **Status**: promoted
- **Analyzer**: pcb
- **Source**: Hardware_Soft_Power_Switch.kicad_pcb
- **Created**: 2026-03-24

### Correct
- The PCB reports 63 total footprints. The schematic has 40 real components plus G3 (OSHW logo, exclude_from_bom), plus the board-only kibuzzard annotations (SparkFun graphical elements). The PCB has 35 real component footprints, 4 FIDs, 4 standoffs, 1 SW1, 3 connectors, 2 jumpers, plus 13 board_only kibuzzard annotations and 1 G3 (Creative Commons), 1 G*** (Flame), 1 G*** (LOGO), 1 Ref**. Total matches the 63 reported.
- The PCB correctly identifies the board as a 25.4mm x 25.4mm square. This is confirmed by the board_outline with start [115.57, 99.06] and end [140.97, 124.46], giving exactly 25.4mm in both X and Y dimensions. SparkFun ProtoBoard-style 1-inch square boards are a common SparkFun form factor.
- The PCB reports 47 vias, all 0.56mm outer diameter with 0.3mm drill. The gerber drill file (Hardware_Production_Single_PCB.json) confirms 47 via holes at 0.3mm. The annular ring is a uniform 0.13mm ((0.56-0.3)/2), which is acceptable but tight for standard fabrication. This is consistent across the PCB and gerber outputs.
- The zone analysis correctly identifies one GND zone spanning F&B.Cu with the fill area (789.23 mm²) exceeding the outline area (645.16 mm²) due to the poured fill extending into keepout areas on both layers. The fill_ratio of 1.223 and the layer-specific breakdown (B.Cu: 446.06, F.Cu: 343.17) are consistent with a double-sided pour on a 25.4x25.4mm board.
- The connectivity section correctly reports routing_complete=true with unrouted_count=0. The PCB has 24 total nets with pads and all are routed. This matches the board which is a production-ready design from SparkFun.
- The via_in_pad analysis correctly identifies 3 instances: a via in C2 pad 1 (the 47uF tantalum's positive pad) and two vias on J1's NC1 and NC2 pads. The same_net=false flag for all three is accurate — for C2, the via connects different nets (the timing node Net-(C2-Pad1) vs. via net), and for J1's NC pads these are truly unconnected. This is correctly detected.
- The PCB reports two track widths: 0.1778mm (7-mil, used for 168 signal segments) and 0.5588mm (22-mil, used for 43 power/wider segments). These match the gerber aperture data which shows the same two conductor widths. The 0.1778mm minimum is appropriate for the small 25.4mm board, though tight for high-current paths — mitigated by the copper pours.
- The PCB net list correctly captures all 24 nets including the meaningful signal names: BTN (button sense), EN (enable output from flip-flop), OFF (soft-off control), PUSH (button push output), VOUT (switched output), VIN (input), GND. Unnamed nets follow the KiCad convention Net-(ref-pad). This is consistent with the schematic's 25 nets (1 unnamed phantom net disappears in PCB translation).
- The PCB setup section correctly reports a 1.6mm board thickness with the standard stackup: F.SilkS / F.Paste / F.Mask (0.01mm) / F.Cu (0.035mm) / core dielectric 1.51mm FR4 (ε=4.5, tan δ=0.02) / B.Cu (0.035mm) / B.Mask (0.01mm) / B.Paste / B.SilkS. This is the standard JLC/OSHPARK 2-layer configuration and is accurately parsed.
- The PCB component_groups section shows R group with count=10 and references R1 through R10, exactly matching the schematic. All resistors are SMD type on F.Cu layer, correctly reflected in the footprint entries.
- SW1 (SMD 5.2×5.2mm tactile switch) is correctly identified as type='smd' with pad_count=4 and placed on F.Cu. The footprint has courtyard bounds consistent with a 5.2mm square push switch. The net connections (GND on pin 1, BTN on pin 2) match the schematic.

### Incorrect
- The PCB reports 63 total footprints, front_side=44, back_side=19, smd_count=35, tht_count=1. Counting actual SMD real components from the footprints list: Q3 (6-pin SMD), U2 (5-pin), U3 (5-pin), U4 (6-pin), D1 (SOD-323 SMD), D2, D3 (LED SMD), F1 (SMD 1210 fuse), C1,C2,C3,C4 (SMD caps), R1-R10 (SMD resistors), J1,J2 (SMD JST), JP1,JP2 (SMD jumpers), Q1,Q2 (SOT-23 SMD), SW1 (SMD push button), FID1-FID4 (SMD fiducials), 4 standoffs (classified as 'smd' with pad_count=1) = 35 SMD components. This is correct, though the J3 connector is THT (through_hole with 6 PTH pins) and the 4 ST standoffs are classified as 'smd' which is technically how they appear in KiCad.
  (statistics)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001459: Edge.Cuts layer missing_required flag is a false alarm — GKO file is present but misidentified; GKO file misclassified as B.Mask instead of Edge.Cuts based on incorrect X2 FileFunction attribute; P...

- **Status**: promoted
- **Analyzer**: gerber
- **Source**: Hardware_Production
- **Created**: 2026-03-24

### Correct
- The panelized gerbers show 1995 total holes: 1645 vias (35 × 47), 210 component holes (35 × 6 THT), and 140 mounting holes (35 × 4 NPTH). This is consistent with a 35-up panel of the single PCB design which has 47 vias, 6 THT holes (J3 connector), and 4 mounting holes (standoffs). The multiplication factor of 35 is consistent across all hole types.
- The panelized gerber alignment check reports aligned=true with no issues. The layer extents are consistent: F.Cu and B.Cu share the same 128.491mm × 184.975mm bounding box, confirming correct coordinate alignment across all copper layers in the panel. Mask and silkscreen layers have slightly different extents due to expansion rules, which is expected.
- The panelized gerbers report the same two conductor widths as the single PCB gerbers: 0.1778mm and 0.5588mm. This is expected since the panel is composed of repeated copies of the same PCB design. The consistency across both gerber outputs confirms the panelization preserved all electrical design rules.

### Incorrect
- The gerber output reports missing_required=["Edge.Cuts"] and complete=false. However, a file named Soft_Power_Switch_panelized.GKO is present in the gerber set (it appears in the gerbers array). The .GKO extension is the KiCad convention for the board outline (Edge.Cuts layer). The analyzer correctly parses GKO as having FileFunction "Soldermask,Bot" from its X2 attribute — but this is wrong. The GKO file's X2 attribute says Soldermask,Bot which is incorrect for an Edge.Cuts file; however the aperture_analysis shows a 'Profile' aperture function, indicating it IS the board outline file. The completeness check is failing to recognize GKO as Edge.Cuts despite the Profile aperture function evidence.
  (completeness)
- The analyzer classifies Soft_Power_Switch_panelized.GKO as layer_type='B.Mask' because its X2 FileFunction attribute reads 'Soldermask,Bot'. However, GKO is the well-established KiCad extension for Edge.Cuts/board outline, and the file contains a 'Profile' aperture function which unambiguously identifies it as a board outline layer. The analyzer should fall back to extension-based classification when the FileFunction attribute appears misconfigured. This causes the 'Edge.Cuts missing' false alarm.
  (completeness)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001460: Same GKO misclassification as B.Mask occurs in Production_Single_PCB gerbers; Single PCB gerber drill data correctly identifies 47 vias, 6 THT component holes, 4 NPTH mounting holes; Layer set is c...

- **Status**: promoted
- **Analyzer**: gerber
- **Source**: Single_PCB
- **Created**: 2026-03-24

### Correct
- The Production_Single_PCB drill file shows 57 total holes: 47 via drills at 0.3mm, 6 component drills at 1.016mm (J3 is a 6-pin 0.1" header), and 4 NPTH holes at 3.1mm (corner standoffs). All tool types are correctly classified using X2 aperture function attributes. The 1.016mm (40-mil) drill matches standard 0.1" pitch through-hole header pads.
- Both copper layers (F.Cu, B.Cu), all solder mask layers (F.Mask, B.Mask), silk layers (F.SilkS, B.SilkS), paste layers (F.Paste, B.Paste), and the board outline file (GKO misidentified as B.Mask) are all present. No recommended layers are missing. The 9 gerber files + 1 drill file constitute a complete fabrication package for a standard 2-layer board.
- The pad_summary reports 84 SMD apertures, 94 via apertures, 6 THT holes, and an smd_ratio of 0.93. This accurately reflects a design dominated by SMD components with only J3 as through-hole. The smd_ratio calculation (84/(84+6) = 0.933) is correct.
- Both the single PCB and panelized gerbers show B.Paste with 0 apertures, 0 flashes, and 0 draws. This is correct — all SMD components are on the front side (F.Cu), and the back-side components (JP1, JP2 solder jumpers, FID2, FID3, kibuzzard annotations) either do not require paste (jumpers/fiducials) or are graphical-only. The F.Paste layer correctly shows 17 apertures with 76 flashes (single PCB) covering the front-side SMD pads.

### Incorrect
- The same issue occurs in the single-PCB gerber set: Soft_Power_Switch.GKO is listed as layer_type='B.Mask' with FileFunction='Soldermask,Bot', but contains Profile aperture functions. The missing_required=['Edge.Cuts'] false alarm applies here as well. The GKO X2 attributes in both production sets appear to have been generated with an incorrect FileFunction tag, but the file content and extension confirm it is Edge.Cuts.
  (completeness)

### Missed
(none)

### Suggestions
(none)

---
