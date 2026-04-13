# Findings: Mage-Control-Systems-Ltd/NCCM / tests_test-project-nccm-large

## FND-00000956: netclass_flag objects not detected or reported; assembly_complexity misclassifies THT LED as SMD; Component count, BOM, net topology all correct; PWR_FLAG warning correctly fired for battery-powere...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: tests_test-project-nccm_test-project-nccm.kicad_sch
- **Created**: 2026-03-23

### Correct
- 3 components (R1, BT1, D1), 3 nets (GND + 2 unnamed), 8 wires all correctly parsed. BOM entries match source symbols. Net connectivity is accurate.
- GND net has power_in pin (#PWR01) and passive pins but no PWR_FLAG symbol, so ERC would flag it. The warning is accurate for this schematic.

### Incorrect
- The schematic output reports smd_count=1 (D1) and package_breakdown 'other_SMD':1. The source schematic has D1 using footprint 'LED_THT:LED_D1.8mm..._Horizontal', which is explicitly a THT part. The PCB output correctly identifies D1 as through_hole (tht_count=3). The schematic analyzer is apparently classifying D1 based on symbol type rather than footprint library prefix.
  (signal_analysis)

### Missed
- The schematic contains 3 KiCad 9 netclass_flag items (BAT+, BAT-, LED) used to assign net classes to nets. The analyzer produces no output field for these — they are silently ignored. This is a key feature of KiCad 9 and is the entire point of the NCCM test project.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00000957: Large test project: 33 components, 2 unique parts, power rails correctly extracted

- **Status**: new
- **Analyzer**: schematic
- **Source**: test-project-nccm-large.kicad_sch
- **Created**: 2026-03-23

### Correct
- 33 components (32 resistors at 1M + 1 battery), 33 nets, power_rails=[GND, PWR_FLAG, VCC] all match what a stress-test netclass matrix project would contain. BOM grouping of 32 resistors into one line item is correct.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00000958: PCB analysis accurate: 3 THT footprints, 2-layer board, GND zone, fully routed; fill_ratio=1.862 is physically impossible (filled area > outline area); DFM, silkscreen, net routing all correctly an...

- **Status**: promoted
- **Analyzer**: pcb
- **Source**: tests_test-project-nccm_test-project-nccm.kicad_pcb
- **Created**: 2026-03-23

### Correct
- footprint_count=3, tht_count=3, smd_count=0, 2 copper layers, 1 GND zone spanning both layers, 6 track segments, routing_complete=true, board outline missing (edge_count=0) which matches source. All net assignments correct.
- min_track_width=0.4mm, dfm_tier=standard with no violations, silkscreen warnings for missing board name/revision are appropriate for a test project with no board name in silkscreen.

### Incorrect
- The GND zone has outline_area_mm2=6288.2 but filled_area_mm2=11707.86, giving fill_ratio=1.862. Filled area cannot exceed outline area. This indicates a bug in how the filled area is computed — likely summing both copper layers' fill areas without realizing they overlap in 2D footprint. The zone fills both F.Cu and B.Cu (6024+5683=11707), but the outline polygon is 2D and only 6288 mm2. Filled area should be reported per-layer or capped.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00000959: No gerber files exist in repo — prompt referenced non-existent output files

- **Status**: promoted
- **Analyzer**: gerber
- **Source**: 
- **Created**: 2026-03-23

### Correct
(none)

### Incorrect
(none)

### Missed
- The gerber manifest is empty and the NCCM repo contains no gerber outputs. The prompt referenced 'nccm_output.json' and 'nccm_output_2.json' which do not exist on disk. No gerber analysis was possible or performed. This is expected for a plugin test-project repo.
  (signal_analysis)

### Suggestions
(none)

---
