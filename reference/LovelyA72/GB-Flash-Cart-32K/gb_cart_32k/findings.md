# Findings: LovelyA72/GB-Flash-Cart-32K / gb_cart_32k

## FND-00000556: Component count and BOM correct; Power rails GND and VCC correctly identified; Flash memory interface not detected in memory_interfaces; R1 and R2 pull-up resistors not identified as protection/pul...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: gb_cart_32k.sch.json
- **Created**: 2026-03-23

### Correct
- 5 components (U1, C1, R1, R2, P1), 4 types, all correctly identified with proper values and footprints.
- Both power rails extracted; decoupling analysis correctly finds C1 100n on VCC.
- Source has 3 explicit NoConn markers (lines 16-18) plus one on RAM_CE (line 256), totaling 4. Output reports total_no_connects: 4.
- All 29 nets correctly enumerated: GND, VCC, WE, ROM_OE, RAM_CE, D0-D7 (8), A0-A15 (16). Net count matches source.

### Incorrect
- Both U1 and P1 have pins:[] in the components list. The flash chip and GB connector pins connected via global labels are not traced to their nets. This is a known limitation of legacy .sch parsing where global label connectivity is not fully resolved to component pins, causing nets like D0-D7 and A0-A15 to show pins:[] as well.
  (signal_analysis)

### Missed
- U1 is a SST39SF010 parallel flash with A0-A15 address bus and D0-D7 data bus connected via global labels. The memory_interfaces detector returned empty despite a clear parallel memory topology.
  (signal_analysis)
- R1 pulls WE to VCC (10K) and R2 pulls ROM_OE to VCC (10K). These are classic active-low signal pull-ups but protection_devices and passive_warnings are both empty. The subcircuits entry for U1 also shows empty neighbor_components, missing the associated passives.
  (signal_analysis)

### Suggestions
(none)

---
