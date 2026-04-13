# Findings: hasecilu/PCBsCollection / 8x8MatrixOldSchool

## FND-00001704: Component count and net topology correctly parsed for simple 2-connector ISP adapter; J2 'USBasp' flagged as USB connector in usb_compliance check; Assembly complexity marks PinSocket THT connector...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: USBasp2ICSP_USBasp2ICSP.kicad_sch.json
- **Created**: 2026-03-24

### Correct
- The schematic has exactly 2 components (J1 ICSP 6-pin, J2 USBasp 10-pin), 9 nets (MISO, MOSI, SCK, nRST, +5V, GND, and 3 unnamed unconnected pins 3/4/5 on J2), and 3 no-connects. All correctly reported. Net classification is correct: MISO/MOSI as data, SCK as clock, nRST as control.

### Incorrect
- The USB compliance checker detected J2 (value='USBasp') as a USB connector because 'USB' appears in the value string. However, USBasp is an AVR programmer dongle that uses a 10-pin ISP header, not a USB connector. The J2 footprint is PinSocket_2x05_P2.54mm which is a standard 2x5 0.1" header. This triggers a spurious USB ESD IC recommendation.
  (usb_compliance)
- The assembly_complexity section reports smd_count=2, tht_count=0 for J1 (PinSocket_2x03_P2.54mm) and J2 (PinSocket_2x05_P2.54mm). Both footprints are through-hole pin sockets with 2.54mm pitch — definitively THT. The PCB analysis for the same design correctly identifies tht_count=2, smd_count=0. The schematic analyzer is misclassifying 2.54mm pitch PinSocket footprints as SMD.
  (assembly_complexity)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001705: UART bus falsely detected on CNC stepper direction, limit, and Arduino serial pin nets; All 9 connector components correctly identified with proper types

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: CNC_shield_CNC_shield.kicad_sch.json
- **Created**: 2026-03-24

### Correct
- The CNC shield schematic contains 9 connectors (P1 Power, P2 Analog, P3 Digital, P4 Digital as Arduino socket headers, plus J1-J3 JST-XH 6-pin and J4-J5 2x13 headers). All 9 are correctly classified as connector type with proper footprints identified.

### Incorrect
- Four nets are incorrectly flagged as UART: 'DirX' (contains substring 'RX' when uppercased: 'DIRX'), 'LimitX' (contains 'TX' in 'LIMITX'), '1(TX)' (Arduino digital pin 1 labeled TX), and '0(RX)' (Arduino digital pin 0 labeled RX). None of these are UART signals in this design context: DirX and LimitX are stepper motor direction and limit switch signals routed from the Arduino digital headers to JST connectors, while 0(RX) and 1(TX) are single-pin connector nets (pin count 1) with no UART IC attached. The pattern-matching on substring TX/RX in arbitrary net names is too broad.
  (design_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001706: Custom 'Earth' ground net not recognized as ground domain; All 4 NPN transistor switch circuits detected and base resistors identified; Component count correct: 20 components across 6 unique parts

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: LED_Display7segx2_Display7segx2.kicad_sch.json
- **Created**: 2026-03-24

### Correct
- Four MMBT3904 NPN transistors (Q1-Q4) are all detected in transistor_circuits with correct base resistors (R9-R12, all 10k). Each transistor drives a segment of the 7-segment display. Base driver and pulldown detection is working correctly.
- The schematic has U1 (CC56-12EWA dual 7-segment display), R1-R12 (12 resistors), Q1-Q4 (4 NPN transistors), J1 (13-pin connector), H1-H2 (2 mounting holes) = 20 total components. The analyzer reports exactly 20 with the correct type breakdown.

### Incorrect
- The design uses 'Earth' as the ground net name (instead of 'GND'). The ground_domains section reports ground_nets={} (empty) and multiple_domains=false, meaning the analyzer failed to identify 'Earth' as a ground rail. Consequently, the 4 NPN transistor switches (Q1-Q4 MMBT3904) all show emitter_is_ground=False even though their emitters connect to the Earth net. The analyzer should recognize 'Earth' as a ground rail based on its connection to power symbols or net characteristics.
  (ground_domains)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001707: Component count and type classification correct for 8x8 LED matrix driver board; Net count matches PCB exactly at 34 nets

- **Status**: new
- **Analyzer**: schematic
- **Source**: 8x8MatrixOldSchool.kicad_sch.json
- **Created**: 2026-03-24

### Correct
- The schematic contains U1 (ULN2803A Darlington array), 8 resistors (R1-R8), 1 LED matrix display (D1), 2 connectors (J1 9-pin, J2 8-pin), 2 mounting holes (H1-H2) = 14 components. The analyzer correctly reports 14 total with proper type breakdown: ic=1, resistor=8, led=1, connector=2, mounting_hole=2.
- The schematic reports 34 total nets. The PCB analyzer for the same design also reports net_count=34. This cross-analyzer consistency confirms correct net extraction from the schematic.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001708: EE-SX1105 optical slot sensors (Q1, Q2) classified as 'transistor' type; SN74LVC2G17DCKT Schmitt-trigger buffer classified as IC with decoupling observation

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: Encoder_Encoder.kicad_sch.json
- **Created**: 2026-03-24

### Correct
- U1 is correctly identified as an IC (type='ic'). The design_observations correctly flags that U1's +5V rail lacks decoupling capacitors, which is accurate — the Encoder board has no bypass caps for the buffer IC. Net count of 12 matches the PCB exactly.

### Incorrect
- The EE-SX1105 is an Omron optical slot sensor (photointerrupter) containing an infrared LED and phototransistor in a housing — not a discrete transistor. The library reference 'Q1' and 'Q2' with lib_id '2021-04-25_18-55-55:EE-SX1105' are classified as type='transistor', which leads to them appearing under component_types.transistor=2. They should be classified as 'sensor' or 'optical_sensor'. The transistor_circuits array is correctly empty (since the IC can't be analyzed as a discrete BJT switch topology), but the type label is wrong.
  (statistics)

### Missed
(none)

### Suggestions
- Fix: EE-SX1105 optical slot sensors (Q1, Q2) classified as 'transistor' type

---

## FND-00001709: Unannotated subcircuit template sheet correctly flagged with annotation issues

- **Status**: new
- **Analyzer**: schematic
- **Source**: Encoder_SnglChann.kicad_sch.json
- **Created**: 2026-03-24

### Correct
- The SnglChann.kicad_sch is a reusable subcircuit template with unannotated references R? and Q?. The analyzer correctly reports annotation_issues with duplicate_references=['R?'] and unannotated=['Q?', 'R?'], and also correctly flags missing_footprint for R?. The 2-component detection (1 resistor + 1 transistor/optical sensor) is correct.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001710: PCB correctly analyzed as 2-layer 33x33mm fully routed board with 16 footprints

- **Status**: new
- **Analyzer**: pcb
- **Source**: 8x8MatrixOldSchool.kicad_pcb.json
- **Created**: 2026-03-24

### Correct
- The 8x8MatrixOldSchool PCB is a 33.02x33.02mm 2-layer board (F.Cu + B.Cu) with 14 real components plus 2 artwork logos (16 footprints total). The analyzer correctly identifies footprint_count=16, copper_layers_used=2, routing_complete=True, via_count=3, and net_count=34 matching the schematic exactly.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001711: Encoder PCB correctly identified as 33x18mm 2-layer board with DFM tier standard

- **Status**: new
- **Analyzer**: pcb
- **Source**: Encoder_Encoder.kicad_pcb.json
- **Created**: 2026-03-24

### Correct
- The Encoder PCB is 33.02x17.78mm with 2 copper layers, 15 footprints (12 real + 2 svg2mod logos + 1 G*** LOGO), 74 track segments, 2 vias, and 1 copper zone. Routing is complete with 0 unrouted nets. DFM metrics show min track 0.25mm, min drill 0.4mm — standard tier. All correctly reported.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001712: copper_layers_used reports only 1 (B.Cu) despite F.Cu content in gerbers

- **Status**: promoted
- **Analyzer**: pcb
- **Source**: LED_LED_BAR_LED_BAR.kicad_pcb.json
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
- The PCB analyzer reports copper_layers_used=1 with copper_layer_names=['B.Cu'] only. However the generated gerbers include both F.Cu and B.Cu files, with F.Cu containing pad data (25.4mm wide extent). The discrepancy arises because the analyzer counts copper usage from routed tracks and zones (all on B.Cu), ignoring component pad copper that physically exists on F.Cu. This leads the gerber analyzer to flag alignment warnings when comparing F.Cu (25.4mm) to Edge.Cuts (30.48mm), but the underlying cause is that F.Cu only contains pads (not tracks), which the PCB analyzer correctly excludes from 'copper layers used for routing'.
  (statistics)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001713: Compact 14x16mm adapter PCB correctly parsed with custom rounded-rectangle outline

- **Status**: new
- **Analyzer**: pcb
- **Source**: USBasp2ICSP_USBasp2ICSP.kicad_pcb.json
- **Created**: 2026-03-24

### Correct
- The USBasp2ICSP PCB has a compact 13.97x16.51mm outline with rounded corners (12 Edge.Cuts edges including arcs). The analyzer correctly identifies 2 THT footprints, 1 copper layer (F.Cu), 17 track segments, 0 vias, and 9 nets matching the schematic. The complex outline with arcs is correctly parsed into a bounding box.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001714: Display7segx2 PCB correctly analyzed: 22 footprints, 2 layers, 64 copper zones

- **Status**: new
- **Analyzer**: pcb
- **Source**: LED_Display7segx2_Display7segx2.kicad_pcb.json
- **Created**: 2026-03-24

### Correct
- The 52x26mm 2-layer PCB has 20 real components (matching the schematic's 20) plus 2 artwork items = 22 footprints. The large zone_count=64 is consistent with a design using many individual copper zones for the 7-segment display layout. net_count=29 matches the schematic's total_nets=29 exactly. Routing is complete.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001715: Complete 2-layer gerber set with correct board dimensions and drill classification

- **Status**: new
- **Analyzer**: gerber
- **Source**: fab.json
- **Created**: 2026-03-24

### Correct
- The fab/ directory contains 9 gerber files (both copper layers, masks, paste, silkscreen, edge cuts) plus 2 drill files (PTH/NPTH). Board dimensions 33.02x33.02mm match the PCB file exactly. All layers are present, alignment is within tolerance, and via count (3) matches the PCB analysis. Drill tools correctly classify 16 holes at 0.65mm (connector pins), 17 holes at 1.0mm (DIP package), and 2 NPTH mounting holes at 2.2mm.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001716: Drill-only directory correctly flagged as incomplete gerber set

- **Status**: new
- **Analyzer**: gerber
- **Source**: LED_Display7segx2.json
- **Created**: 2026-03-24

### Correct
- The project root directory contains only Display7segx2-NPTH.drl and Display7segx2-PTH.drl files, with no copper or other gerber layers. The analyzer correctly reports completeness.complete=False with missing_required=['B.Cu','B.Mask','Edge.Cuts','F.Cu','F.Mask'] and gerber_files=0. The complete gerber set is in the fab/ subdirectory (analyzed separately as LED_Display7segx2_fab.json).

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001717: Alignment warning triggered by legitimate design: F.Cu pads smaller extent than Edge.Cuts

- **Status**: promoted
- **Analyzer**: gerber
- **Source**: LED_LED_BAR_fab.json
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
- The gerber analyzer flags alignment=False with 'Width varies by 5.1mm across copper/edge layers' and 'Height varies by 4.3mm across copper/edge layers'. The F.Cu layer extent is 25.4x23.6mm while Edge.Cuts is 30.48x27.94mm. This is not a genuine misalignment — all routing tracks and zones are on B.Cu, and F.Cu contains only component pad copper which legitimately does not span the full board width. There is no actual layer origin offset; the gerbers are correctly produced. The alignment check is overly sensitive to legitimate designs where component pads don't extend to board edges.
  (alignment)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001718: Encoder fab gerbers complete with correct drill hole classification

- **Status**: new
- **Analyzer**: gerber
- **Source**: Encoder_fab.json
- **Created**: 2026-03-24

### Correct
- 11 gerber files plus 2 drill files for the 33x18mm board. The completeness check passes with all required layers present. Via count (2) matches the PCB analysis. Component holes include 22 PTH holes for the THT connectors, mounting holes, and DIP IC. The X2 attribute-based classification is correctly used.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001719: Legacy .sch parser creates 22 extra unnamed nets vs 1 in the KiCad 6 version

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: CNC_shield_CNC_shield.sch.json
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
- The legacy KiCad 5 CNC_shield.sch is parsed to report 51 total nets (29 named + 22 unnamed), while the KiCad 6+ CNC_shield.kicad_sch of the same design reports 30 total nets (29 named + 1 unnamed). The 21 extra unnamed nets in the legacy format are artifacts of the legacy parser failing to merge connected wire segments at junction points into unified nets, creating spurious isolated net stubs. The named net count (29) is consistent between both parsers.
  (statistics)

### Missed
(none)

### Suggestions
(none)

---
