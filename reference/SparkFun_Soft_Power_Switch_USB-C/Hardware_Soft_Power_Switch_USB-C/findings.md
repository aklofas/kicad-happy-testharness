# Findings: SparkFun_Soft_Power_Switch_USB-C / Hardware_Soft_Power_Switch_USB-C

## FND-00001489: Component count correct: 42 total components, 39 nets, 0 no-connects; No-connect count correctly 0: all 'no_connect' strings are symbol pin type declarations; Q3 (SIL2308 dual MOSFET) N-channel uni...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: Soft_Power_Switch_USB-C.kicad_sch
- **Created**: 2026-03-24

### Correct
- The schematic analyzer correctly reports 42 total_components, 39 total_nets, and 0 total_no_connects. The 0 no-connect count is confirmed accurate — the 5 occurrences of 'no_connect' in the source file are all inside symbol pin type declarations (library definitions), not placed NC cross symbols on the schematic. The 10 NC-only nets arise from pins typed no_connect in their symbol definitions.
- total_no_connects=0 is correct. Verified by inspecting the source .kicad_sch: all 5 occurrences of 'no_connect' appear as '(pin no_connect line' inside symbol definitions, which are library pin type annotations, not placed NC cross symbols. The design intentionally has no unconnected pins.
- The analyzer correctly identifies two RC filters: R5 (100Ω) + C2 (47µF) giving ~33.86 Hz cutoff (output supply filtering), and R2 (200kΩ) + C2 (47µF) giving ~0.017 Hz cutoff (very slow timing RC). Both are real RC filter pairs. The frequency calculations are accurate.
- The analyzer correctly identifies F1 (Polyfuse/resettable fuse) as a protection device in protection_devices. This is the only protection device on the schematic. The value and footprint are consistent with a standard SMD resettable fuse protecting the output.

### Incorrect
- Q3 is a SIL2308 dual MOSFET with two schematic units: unit 1 is an N-channel MOSFET (gate=EN via R9, drain=R10/gate drive) and unit 2 is a P-channel MOSFET (gate=CTRL, source=VIN, drain=VOUT). The transistor_circuits list only captures unit 2 (P-channel). Unit 1 (N-channel) performs the gate-drive enable function and is a separate circuit element that should be independently analyzed. The N-channel unit is part of the power switch control path.
  (signal_analysis)
- The USB compliance checker reports J2 as failing CC pull-down requirements. However, J2 is the VOUT USB-C connector — a downstream-facing port (DFP) acting as a power source output, not a device input (UFP). CC 5.1kΩ pull-downs are required only for UFP (device) ports to indicate they want power. A DFP power source uses Ra (800Ω–1200Ω) on CC or leaves CC unconnected with a current source. The absence of 5.1kΩ pull-downs on J2 is correct for this topology. The compliance check does not distinguish UFP from DFP roles.
  (signal_analysis)
- The design_analysis.erc_warnings list includes PWR_FLAG warnings. This is a connector-powered design (power enters through J1 USB-C, no on-board regulator generating power nets). KiCad ERC requires PWR_FLAG symbols on nets that have no driver, but in a pass-through power switch topology this is common and expected. These are not real electrical errors. The analyzer correctly surfaces ERC warnings but lacks context to classify them as expected/benign.
  (design_analysis)
- The schematic analyzer reports assembly_complexity.tht=0 and assembly_complexity.smd=45, but the PCB confirms J1 and J2 (USB-C connectors) and J3 (6-pin header) are through-hole components with PTH drilled holes. The schematic analyzer cannot determine footprint mounting type (SMD vs THT) because this information is in the footprint assignment, not the symbol definition. All components are being counted as SMD. Additionally, total assembly_complexity=45 exceeds the schematic's 42 total_components by 3, suggesting power symbols or other non-component elements are being counted.
  (assembly_complexity)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001490: PCB footprint count correct: 61 total (42 front, 19 back), 2-layer board 25.4×25.4mm; PCB SMD/THT split correct: 35 SMD, 3 THT (J1, J2 USB-C connectors + J3 header); GND copper pour zone correctly ...

- **Status**: promoted
- **Analyzer**: pcb
- **Source**: Soft_Power_Switch_USB-C.kicad_pcb
- **Created**: 2026-03-24

### Correct
- The analyzer correctly reports 61 total footprints (42 front-side, 19 back-side). The board dimensions are 25.4×25.4mm (1 inch square), consistent with a compact SparkFun breakout. The layer count of 2 is correct (F.Cu and B.Cu). Track count 284 and via count 55 are consistent with a compact 2-layer USB power switch design.
- The PCB analyzer correctly identifies 35 SMD and 3 THT footprints from the actual footprint assignments. J1 and J2 are USB-C through-hole connectors, J3 is a 6-pin through-hole header. The remaining 3 footprints not in SMD/THT counts (61 total vs 35+3=38) are likely board_only/fabrication footprints such as Kibuzzard decorative artwork elements that have no pads.
- The analyzer correctly identifies 1 copper zone (GND net pour covering the board). The fill_ratio of 1.125 is slightly above 1.0, which is physically valid since copper pours can have slightly more surface area than the zone boundary due to thermal relief spokes extending beyond zone edges. The zone is on a copper layer and is filled.

### Incorrect
- The via_in_pad detection flags C2 pad 1 with same_net=False. C2 is the 47µF filter capacitor. If a via is placed within C2's pad footprint keepout zone or physical pad area, same_net=False would indicate a different net via intruding on the pad — a genuine DFM concern. However, same_net=False could also arise from a GND-connected pad and a GND-named via having slightly different net name representations (e.g., 'GND' vs '/GND'). This finding should be verified against the actual PCB layout.
  (connectivity)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001491: Edge.Cuts layer falsely reported missing: GKO file IS board outline but has wrong X2 FileFunction metadata; GKO file classified as B.Mask instead of Edge.Cuts due to wrong X2 FileFunction attribute

- **Status**: promoted
- **Analyzer**: gerber
- **Source**: Production_Soft_Power_Switch_USB-C.GKO
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
- The .GKO file's X2 header says %TF.FileFunction,Soldermask,Bot*% which causes the analyzer to map it to B.Mask. The file actually contains the board profile (Profile aperture + 4 line segments forming the 25.4mm×25.4mm board boundary). This means B.Mask is double-counted (both the real B.Mask .GBS file and the .GKO file are mapped to B.Mask) and Edge.Cuts is missing from found_layers. The root cause is a KiCad export bug, but the analyzer could detect the Profile aperture function as a fallback to identify Edge.Cuts files regardless of FileFunction.
  (layer_analysis)

### Missed
- The gerber analyzer reports missing_required=['Edge.Cuts'] and complete=False. However, the .GKO file (Soft_Power_Switch_USB-C.GKO) is the board outline file — GKO is the standard Gerber Keep-Out/board outline extension. Inspection of the file shows it uses a Profile aperture (standard for Edge.Cuts) and contains a 4-segment rectangle matching the 25.4×25.4mm board boundary. The X2 attribute in the file header incorrectly says FileFunction=Soldermask,Bot (a KiCad 8.0.5 export quirk where .GKO files get wrong X2 metadata). The analyzer relies solely on X2 FileFunction and maps this to B.Mask, missing the true Edge.Cuts layer. A secondary check on aperture function (Profile) or file extension (.GKO) would fix this.
  (layer_analysis)

### Suggestions
(none)

---

## FND-00001492: Drill classification correct: 55 vias (0.3mm), 10 component holes (J1/J2/J3), 4 NPTH mounting holes; Component reference count in gerbers (58) slightly exceeds schematic count (42): Kibuzzard artwo...

- **Status**: new
- **Analyzer**: gerber
- **Source**: Production_
- **Created**: 2026-03-24

### Correct
- The analyzer correctly classifies 55 via holes (0.3mm drill, consistent with the PCB's 55 vias), 10 component holes at 0.65mm and 1.016mm (matching J1+J2 USB-C connector mechanical pads and J3 6-pin header through-hole pins), and 4 mounting holes at 3.1mm NPTH (standard SparkFun 4-corner mounting hole pattern). Total 69 drilled holes. The USB-C connector mechanical pads being classified as component_holes is correct per their X2 AperFunction=ComponentDrill attribute.
- The gerber component_analysis reports 58 unique component references while the schematic has 42 components. The difference of 16 extra refs in gerbers is consistent with Kibuzzard decorative PCB artwork footprints (board_only type, no schematic symbols) contributing reference designators to the fab layers. These artwork footprints appear on silkscreen/fabrication layers but have no electrical schematic counterparts. This is expected behavior for boards using PCB artwork libraries.
- The analyzer finds 8 layers: B.Cu, B.Mask, B.Paste, B.SilkS, F.Cu, F.Mask, F.Paste, F.SilkS. This is the expected layer set for a 2-layer PCB with complete front/back copper, solder mask, paste (for SMD stencil), and silkscreen. No inner layers are present (correct for 2-layer). Note: Edge.Cuts is falsely absent (see separate finding on GKO misidentification).

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
