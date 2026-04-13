# Findings: RWeick/FCD-0003.1S-Xplorer64 / FCD-0003.1S

## FND-00000562: All component refs extracted as None — ref extraction fails for this schematic style; statistics.total_components (13) counts unique refs but components list has 22 instances — semantic inconsisten...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: FCD-0003.1S.kicad_sch.json
- **Created**: 2026-03-23

### Correct
- The annotation_issues.duplicate_references correctly identifies C6 (5 instances), R12 (5 instances), J3 (2 instances) as duplicate references. This is a real design quality issue in this schematic.
- Source grep confirms 13 wire elements and 309 label elements, matching statistics.total_wires=13 and labels list length=309. This label-heavy topology (virtually no direct wires) is correctly handled.
- Source has exactly 2 no_connect markers matching statistics.total_no_connects=2. Net count of 88 is plausible for 309 signal labels across the design.
- U4 has value='~' in the source, which is KiCad's placeholder for an unset value. The analyzer correctly identifies it in annotation_issues.missing_value.

### Incorrect
- Every entry in d['components'] has ref=None, and BOM entries show '?' for all refs. The schematic uses inline instance properties (e.g. '(property "Reference" "C6"' at line 3302) rather than the nested lib_symbol default. The analyzer fails to read instance-level Reference properties, leaving all 13 unique designators (C6, U1-U4, J1, J3-J6, D1, R12, S1) unresolved.
  (signal_analysis)
- The statistics block deduplicates duplicate refs (C6 appears 5×, R12 appears 5×, J3 appears 2×) and reports 13 unique refs as total_components. But the components list contains all 22 individual instances. This makes total_components misleading — it neither counts instances nor unique parts accurately, especially when duplicate refs represent distinct physical components.
  (signal_analysis)
- Because component_types counts unique refs per type, it reports resistor=1 (R12 is one unique ref, but 5 physical resistors with different values: 221, 103, 103, 101, Empty), capacitor=1 (C6 × 5 bypass caps), connector=5 (6 instances). IC count is correct at 4. The counts in the components list (5 resistors, 5 caps, 6 connectors) are accurate but misalign with the statistics block.
  (signal_analysis)
- The N64 cartridge edge connector (J3) has many GND pins (power_out type) and multiple 3.3V pins driving VCC. These are legitimate multi-pin power connections in a connector footprint, not ERC conflicts. The same applies to 12V (4 drivers), UNUSED_Front/Rear (2 drivers each). Only /write, ALE_H, ALE_L with 2 drivers each warrant investigation; the power rail entries are false positives.
  (signal_analysis)
- The 12V net from the N64 cartridge edge connector is classified as 'signal' in design_analysis.net_classification. It should be classified as a power rail since it's a supply voltage (used for some N64 cartridge SRAM types). The net has 4 power_out drivers from connector pins, strongly indicating it is a power supply net.
  (signal_analysis)

### Missed
- The design contains two SST29LE010 parallel NOR flash chips (U2, U3) with address/data buses (A0-A18, AD0-AD15) and an AT90S1200 AVR microcontroller (U4). signal_analysis.memory_interfaces is empty. The address bus signals (A0-A18) and parallel data lines are present in nets but no parallel flash interface is detected.
  (signal_analysis)

### Suggestions
(none)

---
