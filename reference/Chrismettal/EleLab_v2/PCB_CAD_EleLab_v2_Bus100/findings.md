# Findings: Chrismettal/EleLab_v2 / PCB_CAD_EleLab_v2_Bus100

## FND-00000527: Component counts, power rails, and types all correctly identified for power distribution bus board

- **Status**: new
- **Analyzer**: schematic
- **Source**: PCB_CAD_EleLab_v2_Bus100_EleLab_v2_Bus100.sch.json
- **Created**: 2026-03-23

### Correct
- 40 components correctly reported: 36 connectors (J1-J4 as Conn_02x08_Odd_Even bus connectors; J5-J36 as 32 single-pin power rail headers for +12V/+24V/+5V/GND), 4 mounting holes (H1-H2 reported as 4 which actually includes LO_1/LO_2 logo symbols treated as mounting holes — acceptable). Power rails ['+12V', '+24V', '+5V', 'GND'] all correctly detected from KiCad 5 power symbols. File version correctly identified as '5 (legacy)'. No signal paths expected or produced — appropriate for a pure power distribution board with no active circuitry.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00000528: Component counts, types, and empty power_rails all correctly reported for passive front panel board

- **Status**: new
- **Analyzer**: schematic
- **Source**: PCB_CAD_EleLab_v2_Frontpanel_a_EleLab_v2_Frontpanel_a.sch.json
- **Created**: 2026-03-23

### Correct
- 28 components correctly counted: 20 connectors (J1-J20), 2 fuses (F1-F2 Polyfuse_Small), and 6 mounting holes (H1-H4 plus LO_1/LO_2 treated as mounting holes). Power rails correctly reported as empty []: the front panel has no KiCad power symbols — power rail names (+24V, +12V, VBUS, GND, D+, D-) appear only as connector value labels and net labels, not as power symbols, so the analyzer correctly does not report them as power rails. USB_A connectors (J3, J4) correctly typed as connectors. Polyfuses F1-F2 correctly typed as fuse. File version correctly identified as '5 (legacy)'.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00000529: All 15 components, 7 power rails, and 10 no-connects correctly reported for ATX-style power feed board

- **Status**: new
- **Analyzer**: schematic
- **Source**: PCB_CAD_EleLab_v2_PowerFeed_EleLab_v2_PowerFeed.sch.json
- **Created**: 2026-03-23

### Correct
- 15 components correctly reported: 10 connectors (J1-J10), 5 mounting holes (H1-H3 plus LO_1/LO_2). Power rails ['+12V', '+12V_F', '+24V', '+24V_F', '+5V', '+5V_F', 'GND'] all 7 correctly detected — the '_F' suffix variants (fused power rails routed through polyfuses on another board) are correctly treated as distinct power domains. PS_ON correctly treated as a signal net rather than a power rail (it is a text label, not a KiCad power symbol). total_no_connects=10 correctly matches the 10 no-connect markers on unused pins of J1 (24-pin ATX connector). File version correctly identified as '5 (legacy)'.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00000530: statistics.total_components reports 4 (unique unannotated groups) instead of 73 (actual component instances); kicad_version reported as 'unknown' for a KiCad 6.0 schematic (file_version 20210621); ...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: PCB_CAD_EleLab_v2_RDecSchematic_RDecSchematic_RDecSchematic.kicad_sch.json
- **Created**: 2026-03-23

### Correct
- The analyzer correctly identifies annotation_issues with duplicate_references=['J?', 'R?', 'SW?'] and unannotated=['#LOGO?', 'J?', 'R?', 'SW?']. This accurately reflects the schematic state — every component uses a template reference (ending in '?') meaning no components have been through KiCad's annotation tool. The unannotated list correctly includes #LOGO? (the Binary-6 logo symbol). The duplicate detection is appropriate since multiple instances share the same unannotated reference string.
- The schematic has no net labels (no named signals beyond power symbols, and this design has no power symbols at all). All internal nodes receive auto-generated names (__unnamed_0 through __unnamed_70). This is correct behavior: 71 unnamed nets corresponds to the internal interconnect nodes of the resistor decade network — the tap points between switch contacts and resistor terminals. Each decade contributes approximately 10 internal nodes (9 resistor junctions plus the decade output), and 7 decades gives roughly 70 nodes, consistent with the 71 reported.

### Incorrect
- The schematic contains 73 component instances: 63 resistors (R?, 9 per decade across 7 decade values), 7 thumbwheel switches (SW?), 2 connectors (J?), and 1 logo (#LOGO?). All references are unannotated (ending in '?'). The analyzer collapses all R? instances into one BOM entry, all SW? into one, etc., and reports statistics.total_components=4 — the count of unique unannotated reference prefixes rather than actual instances. This is confirmed by the discrepancy with simulation_readiness.total_components=73 in the same output, which correctly counts instances. The statistics section should count instances, not unique groups. This is a KiCad 6 parser bug when handling unannotated designs.
  (signal_analysis)
- The file header contains '(version 20210621)' which is the KiCad 6.0 release file format version (date-stamped format used in KiCad 6.x). The analyzer correctly reads this as file_version=20210621 and correctly identifies the format as kicad_new, but then reports kicad_version='unknown' rather than mapping the date-based version number to the KiCad major version '6' or '6.0'. The version mapping table in the analyzer is missing the 20210621 entry (and likely other KiCad 6.x date-stamped versions). This leaves users unable to determine which KiCad major version produced the file.
  (signal_analysis)

### Missed
- The schematic implements a classic resistor decade box: 7 decades (1R through 1M in decade steps), each decade consisting of a KSA-2 thumbwheel switch (SW?) selecting between 9 series resistors (e.g., 1R, 2R, 3R...9R for the units decade). The 7 switch outputs are connected in series between the two J? output connectors, creating a precision adjustable resistor from 0 to 9,999,999 ohms. The analyzer produces no signal_paths detections for this topology. While a generic 'resistor_ladder' or 'decade_network' detector does not currently exist, the design contains 63 passive components arranged in a clear functional network that is worth characterizing. This is a missed detection opportunity rather than an error — the current analyzer does not have a decade-box detector.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00000531: Component count, BOM, net extraction, and power rails all correct for Bus100; point_count on power nets is 42 but actual pin count is 20 or 26; kicad_version correctly identified as '5 (legacy)' fo...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: PCB_CAD_EleLab_v2_Bus100_EleLab_v2_Bus100.sch.json
- **Created**: 2026-03-23

### Correct
- 40 components (36 connectors + 4 mounting holes) correctly identified. Power rails +5V/+12V/+24V/GND correctly extracted. Net structure correct with 8 nets. Unnamed nets for the 2 floating pins on J3 (pin 6, pin 8) are legitimate — those socket pins are unconnected.
- EESchema file version 4 is correctly mapped to '5 (legacy)'. Missing MPNs correctly reported for all 36 connectors.

### Incorrect
- All four power nets (+24V, +12V, +5V, GND) show point_count=42 in the nets dict, but the actual pin arrays contain 20 or 26 entries. point_count appears to be counting wire segment endpoints (junctions/coordinates) rather than component pins. This mismatch may confuse downstream consumers expecting pin-based counts.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00000532: total_components reports 4 but actual component count is 73 — deduplication bug with unannotated references; kicad_version reported as 'unknown' for file_version 20210621 (KiCad 6); No detectors se...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: PCB_CAD_EleLab_v2_RDecSchematic_RDecSchematic_RDecSchematic.kicad_sch.json
- **Created**: 2026-03-23

### Correct
- annotation_issues.duplicate_references=['J?','R?','SW?'] and unannotated=['#LOGO?','J?','R?','SW?'] are correctly identified. The 71 nets are also correctly extracted despite the component counting failure.

### Incorrect
- The design uses unannotated references (all resistors are 'R?', all switches are 'SW?', etc.). The analyzer deduplicates by reference string, so all 63 R? instances collapse to 1, 7 SW? instances to 1, etc. statistics.total_components=4 and BOM quantities are all 1. Actual component array has 73 entries. This is a significant bug when designs have unannotated or template schematics.
  (signal_analysis)
- File version 20210621 is a KiCad 6 .kicad_sch format. The analyzer correctly parses the file but reports kicad_version='unknown' instead of '6'. Version mapping table appears to be missing the 2021-era version numbers.
  (signal_analysis)

### Missed
- The Bus100 output includes signal_analysis, design_analysis, subcircuits, and labels sections; the RDecSchematic output has none of these. The design has 71 nets and 73 components including a 12-position rotary switch with resistor decade network — a resistor ladder/voltage divider pattern that detectors should find. Likely caused by the component count bug causing early exit or the unannotated refs breaking detector input.
  (signal_analysis)

### Suggestions
(none)

---
