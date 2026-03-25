# Findings: MM1_EEPROM_32k_A / MM1_EEPROM_32k_A

## FND-00000871: Legacy .sch parser misses U1 data pin net connections for all 8 MEMDATA nets; Net classifier misclassifies all MEMADDRESS_* lines as 'chip_select' instead of 'address'; memory_interfaces detector f...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: MM1_EEPROM_32k_A.sch.json
- **Created**: 2026-03-23

### Correct
- EEPROM: 4 components (1 connector, 2 capacitors, 1 IC), FLASH: 6 components (connector, 2 caps, IC, jumper, resistor), SRAM: 9 components (connector, 5 ICs, 3 caps). All correctly typed and extracted with proper reference designators.
- All three boards: 100nF bypass caps on +3.3V correctly reported, has_bulk=false and has_bypass=true is accurate. SRAM correctly shows 3 caps (0.3uF total). +5V rail has no decoupling caps which is correct — it's a pass-through supply on the module.

### Incorrect
- MEMDATA_0 through MEMDATA_7 nets each show only J1 (connector) in pins list, missing the AT28BV256 U1 I/O pins. Address nets (MEMADDRESS_*) correctly show both J1 and U1. Data pins are connected via Text Labels at U1 pin positions but the label-to-pin resolution fails for these pins. This means U1's bidirectional data bus connectivity is invisible to downstream analysis.
  (signal_analysis)
- 17 nets named MEMADDRESS_0 through MEMADDRESS_15 are classified as 'chip_select' in design_analysis.net_classification. Only MEM_~CE is a true chip select; the address lines are regular address bus signals. This misclassification is identical across all three MM1 boards.
  (signal_analysis)
- 17 ERC warnings of type 'no_driver' are generated for all MEMADDRESS nets. All pins on these nets are either 'passive' (J1 connector) or 'input' (U1 memory IC). In a module/card design like this, the edge connector provides the drivers — there is no missing driver. These warnings are technically correct per ERC rules but misleading for this design pattern.
  (signal_analysis)
- The annotation_issues field type is dict ({}) but semantically should be a list (no annotation issues found). This is a minor type inconsistency in the output schema — other list fields return [] when empty.
  (signal_analysis)

### Missed
- signal_analysis.memory_interfaces is empty [] for all three boards despite each having a clearly identified memory IC (AT28BV256 EEPROM, SST39LF010 Flash, IS61LV256AL SRAM) with address/data/control signals on named nets. The detector should recognize these as parallel memory bus interfaces.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00000872: kicad_version reported as 'unknown' for KiCad 5 PCB file_version 20171130; Footprint count, placement side, and SMD/THT classification are accurate; Routing completeness, track/via counts, board di...

- **Status**: promoted
- **Analyzer**: pcb
- **Source**: MM1_EEPROM_32k_A.kicad_pcb.json
- **Created**: 2026-03-23

### Correct
- EEPROM: 4 footprints (3F/1B, 4 SMD), FLASH: 6 footprints (4F/2B, 4 SMD/2 THT for PLCC socket and pin header), SRAM: 9 footprints (5F/4B, all SMD). All consistent with the actual footprint library refs in the PCB file.
- All three boards: routing_complete=true, unrouted=0, correct board dimensions (51.5x34.0mm identical across the MM1 series), correct via counts matching drill files. GND zones correctly identified on both layers with fill data.
- All three boards have exactly one GND domain with all components listed. EEPROM: [C1,C2,J1,U1], FLASH adds R1/JP1, SRAM: all 9 components. Zone coverage correctly noted on both copper layers.

### Incorrect
- All three boards use file_version '20171130' which is the KiCad 5 PCB format. The kicad_version field reports 'unknown' instead of '5' or '5 (legacy)'. The schematic analyzer correctly identifies '5 (legacy)' for the matching .sch files.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00000873: pad_summary reports smd_apertures=0 for boards that are predominantly or entirely SMD; Layer completeness, board dimensions, and alignment analysis are accurate; NPTH drill files with 0 holes are i...

- **Status**: promoted
- **Analyzer**: gerber
- **Source**: documents_MM1_EEPROM_32k_A_gerbert.json
- **Created**: 2026-03-23

### Correct
- All three boards: 7 gerber files + 2 drill files, required layers present (F.Cu, B.Cu, F.Mask, B.Mask, F.SilkS, B.SilkS, Edge.Cuts), F.Paste correctly flagged as missing_recommended (these are SMD boards without paste files). Board dimensions 51.5x34.0mm consistent across all three. Layers are aligned (confirmed by SameCoordinates X2 attribute).

### Incorrect
- All three boards show smd_apertures=0 with smd_source='x2_aperture_function'. EEPROM and SRAM have 4 and 9 SMD footprints respectively, yet no SMD apertures are detected. The x2_aperture_function method is failing to identify SMD pads from these KiCad 5 gerbers. FLASH correctly shows tht_holes=34 for the THT components but smd_apertures still shows 0.
  (signal_analysis)
- All three boards have NPTH drill files containing 0 holes, yet has_npth_drill=true. An NPTH file with no holes doesn't meaningfully indicate NPTH drill presence. This is an edge case in completeness checking — it should perhaps be has_npth_drill=false or noted as 'empty NPTH file'.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---
