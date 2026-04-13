# Findings: Jana-Marie/OtterPill / HW v1.1_OtterPill

## FND-00001798: Component count correctly matches source (43 components); components[] array uses 'reference' key but outputs 'ref'=None for all entries; Power regulator (SY8201 buck converter) correctly detected ...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: HW v1.4_OtterPill.kicad_sch.json
- **Created**: 2026-03-24

### Correct
- The v1.4 KiCad 6 schematic contains 43 components (C1-C12, D1-D2, J1-J7, L1, R1-R16, SW1, U1-U4), and the analyzer reports total_components=43 with correct type breakdown: resistor=16, capacitor=12, connector=6, ic=4, led=2, switch=1, inductor=1, test_point=1 (J7 via TestPoint footprint).
- U3 (SY8201) detected as a switching regulator with L1, VIN input, +3V3 output. Feedback divider R6=100kΩ, R7=22kΩ gives Vout = 0.6 × (1 + 100k/22k) = 3.327V. Output shows estimated_vout=3.327 with vref_source='lookup'. This matches the SY8201 datasheet Vref=0.6V.
- R6/R7 (100k/22k) forms the SY8201 feedback divider from +3V3 to GND (is_feedback=true), and R14/R15 (100k/22k) forms a VBUS monitoring divider into PA0/ADC. Both are correctly identified with proper top/bottom/mid net names and ratios (0.180328 each).
- U1 (USBLC6-4) is correctly identified as an ESD IC protecting CC1, CC2, USB_N, and USB_P. The vbus_esd_protection:fail result is also accurate—VBUS itself has no dedicated ESD clamp device, only a decoupling capacitor.
- Both SCL and SDA buses show devices U4 (FUSB302) and U2 (STM32F072), with R10 and R11 (3.3kΩ) pull-ups to +3.3V. The bus_analysis i2c section correctly identifies both lines, their devices, and pull-up values.
- The design uses both +3.3V (pull-up rail for I2C) and +3V3 (main 3.3V output) as separate net names. The analyzer correctly identifies both as distinct power rails in statistics.power_rails, and generates separate PWR_FLAG warnings for each.

### Incorrect
- All 43 entries in the components[] array have ref=null (the 'ref' key is absent). Component reference designators are stored under the 'reference' key, which holds the correct values (R5, SW1, J1, etc.). Signal analysis items (power_regulators, protection_devices, etc.) correctly use 'ref'. This schema inconsistency means code consuming components[] via .get('ref') will silently get None for every component. The 'reference' key is present and correct. This affects both the KiCad 5 and KiCad 6 parsers.
  (components)
- usb_compliance shows cc1_pulldown_5k1:fail and cc2_pulldown_5k1:fail. However, U4 (FUSB302BMPX) is a USB PD controller with integrated Rd (5.1kΩ) pull-down resistors on CC1 and CC2 that are configured in firmware. No external discrete CC resistors are needed or expected. The analyzer does not recognize that this IC class handles CC termination internally, causing two spurious failures.
  (usb_compliance)

### Missed
- R14 (100kΩ) is connected in series between VBUS and PA0, while C12 (100nF) is connected from PA0 to GND, forming an RC low-pass filter for the VBUS ADC monitoring path. The signal_analysis.rc_filters list is empty (0 items). The divider topology (R14 in series, R15 and C12 in parallel to GND) may not match the filter detector's expected R-C topology.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00001799: components[] uses 'reference' key but 'ref' key is absent (same as v1.4); Component count and types match source for v1.3 (43 components)

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: HW v1.3_OtterPill.sch.json
- **Created**: 2026-03-24

### Correct
- KiCad 5 .sch parser correctly extracts all 43 component references matching the source file. Type breakdown matches v1.4: resistor=16, capacitor=12, connector=6, ic=4, led=2, switch=1, inductor=1, test_point=1. The v1.3 and v1.4 schematics are equivalent designs.

### Incorrect
- The KiCad 5 legacy parser also produces components with 'reference' key (not 'ref'). All 43 component entries have .get('ref') == None. The correct values are accessible via .get('reference'). The same schema inconsistency is present across both parsers.
  (components)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001800: v1.1 ACT4088 switching regulator correctly detected; D3/D4 Schottky diodes correctly classified

- **Status**: new
- **Analyzer**: schematic
- **Source**: OtterPill.sch.json
- **Created**: 2026-03-24

### Correct
- v1.1 uses ACT4088 (not SY8201 used in later versions) as the step-down regulator, correctly detected as switching topology with inductor L1. D3 and D4 (SS310 Schottky) are correctly classified as 'diode' type. D1 and D2 (LEDs) are correctly classified as 'led'. Component count of 36 matches the source file.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001801: v1.2 SY8201 regulator correctly detected with VBUS as input rail

- **Status**: new
- **Analyzer**: schematic
- **Source**: HW v1.2_OtterPill.sch.json
- **Created**: 2026-03-24

### Correct
- v1.2 does not have a separate VIN net (no barrel jack); the SY8201 (U3) is powered directly from VBUS. The power regulator entry correctly shows input_rail='VBUS'. Component count of 39 matches the source file exactly.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001802: vG1.0 component count (37) correctly matches source

- **Status**: new
- **Analyzer**: schematic
- **Source**: HW vG1.0_OtterPillG.sch.json
- **Created**: 2026-03-24

### Correct
- The vG1.0 variant schematic has 37 components (C1-C5, C8-C9, C11-C13, D1-D2, J1-J6, L1, R1-R13, SW1, U1-U4). The analyzer correctly reports 37 with the same component type breakdown as v1.3 minus J7 and two capacitors. Power rails correctly limited to +3V3, GND, VBUS (no VIN in this variant).

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001803: Empty edgerails schematic correctly produces zero-component output

- **Status**: new
- **Analyzer**: schematic
- **Source**: HW v1.2_edgerails_edgerails.sch.json
- **Created**: 2026-03-24

### Correct
- The edgerails .sch file is a stub (72 bytes, KiCad format header only, no components). The analyzer correctly returns total_components=0, total_nets=0, and all type counts at zero.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001804: PCB footprint count (45) correctly includes 43 schematic components + 2 logo footprints; Board dimensions correctly extracted as 43.2mm × 17.6mm; Full routing confirmed (0 unrouted nets, routing_co...

- **Status**: new
- **Analyzer**: pcb
- **Source**: HW v1.4_OtterPill.kicad_pcb.json
- **Created**: 2026-03-24

### Correct
- The v1.4 PCB has 43 components (matching the schematic) plus two G*** logo footprints (otter_laying_3411 and otterpill_126x46, both on B.Cu with no pads). The analyzer correctly counts 45 footprints total, with 36 SMD and 7 THT (6 connectors + 1 logo classified as through_hole).
- The Edge.Cuts outline spans x: 20.0–63.2mm (43.2mm width) and y: 19.8–37.4mm (17.6mm height) with rounded corners. The analyzer correctly reports board_width_mm=43.2 and board_height_mm=17.6 in both statistics and board_outline.bounding_box.
- The v1.4 PCB has 57 nets, all routed. connectivity.unrouted_count=0 and statistics.unrouted_net_count=0. The board has 519 track segments and 144 vias with a GND copper pour on both layers.
- The OtterPill is an extremely dense 2-layer board. The analyzer correctly identifies 34 courtyard overlaps including significant overlaps: J3 vs J2 (10.5mm²) and J4 vs J6 (10.2mm²) for pin headers placed edge-to-edge, plus numerous smaller overlaps between 0402 passives and the STM32 QFN (U2 vs C9, R14, R15, C12). These are real DRC flags reflecting the tight layout.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001805: Incomplete routing correctly detected (PA0 net unrouted)

- **Status**: new
- **Analyzer**: pcb
- **Source**: HW vG1.0_OtterPillG.kicad_pcb.json
- **Created**: 2026-03-24

### Correct
- The vG1.0 PCB has 1 unrouted net: PA0, which has 4 pads (R11.1, R10.2, C8.1, U2.11) but no routing connecting them. The analyzer correctly reports routing_complete=false and unrouted_count=1 with specific pad identification.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001806: v1.1 PCB correctly shows 37 footprints (36 components + 1 logo) with full routing

- **Status**: new
- **Analyzer**: pcb
- **Source**: OtterPill.kicad_pcb.json
- **Created**: 2026-03-24

### Correct
- v1.1 has 36 schematic components plus one back-side logo footprint, totaling 37. The analyzer reports footprint_count=37, routing_complete=true, and the same 43.2×17.6mm board dimensions as later revisions.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001807: Edgerails PCB correctly detected as minimal board (1 footprint, no routing)

- **Status**: new
- **Analyzer**: pcb
- **Source**: HW v1.2_edgerails_edgerails.kicad_pcb.json
- **Created**: 2026-03-24

### Correct
- The edgerails PCB is a manufacturing panel helper board with a single footprint (the edge rail connector) and no traces. The analyzer correctly reports footprint_count=1, copper_layers_used=0, track_segments=0, via_count=0, and routing_complete=true (no nets to route).

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001808: v1.1 gerber set complete with all 9 required layers and 2 drill files

- **Status**: new
- **Analyzer**: gerber
- **Source**: gerber.json
- **Created**: 2026-03-24

### Correct
- All standard 2-layer layers present: B.Cu, B.Mask, B.Paste, B.SilkS, Edge.Cuts, F.Cu, F.Mask, F.Paste, F.SilkS. Both PTH (145 holes) and NPTH (2 holes) drill files present. completeness.complete=true with no missing layers.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001809: v1.3 gerber set correctly identifies duplicate Edge.Cuts files and reports complete; Layer alignment correct across all copper and mask layers

- **Status**: new
- **Analyzer**: gerber
- **Source**: HW v1.3_gerber.json
- **Created**: 2026-03-24

### Correct
- The v1.3 gerber directory contains two Edge.Cuts files (OtterPill-Edge_Cuts.gko and OtterPill-Edge_Cuts.gm1). The analyzer correctly processes both (statistics.gerber_files=10), de-duplicates in the found_layers list (Edge.Cuts appears once), and reports completeness.complete=true. All 9 standard layers are covered.
- All copper layers (F.Cu, B.Cu), solder masks, paste, and silkscreen layers share the same 43.2×17.6mm extents. The F.SilkS layer is slightly wider (50.625mm) due to silkscreen text extending beyond the board edge—this is flagged in the extent data. alignment.aligned=true is correct.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001810: Edgerails gerber correctly reported as incomplete (no PTH drill file)

- **Status**: new
- **Analyzer**: gerber
- **Source**: HW v1.2_edgerails_gerber.json
- **Created**: 2026-03-24

### Correct
- The edgerails board has only an NPTH drill file (mounting holes only, no component PTH pads). The analyzer correctly sets has_pth_drill=false and complete=false. The edgerails PCB has one footprint with no plated pads, so the missing PTH drill is accurate.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001811: vG1.0 gerber set complete with correct board dimensions

- **Status**: new
- **Analyzer**: gerber
- **Source**: HW vG1.0_gerber.json
- **Created**: 2026-03-24

### Correct
- All 9 layers present, PTH (159 holes) and NPTH (2 holes) drill files present. completeness.complete=true. Board dimensions 43.2×17.6mm match the PCB source and other revisions. layer_count=2 is correct.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
