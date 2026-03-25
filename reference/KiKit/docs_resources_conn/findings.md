# Findings: KiKit / docs_resources_conn

## FND-00000721: Duplicate sheet path in top-level sheets list; Component extraction, BOM grouping, and hierarchical net naming all correct

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: test_resources_assembly_project_1_KiCAD6_assembly_project_1_KiCAD6.kicad_sch.json
- **Created**: 2026-03-23

### Correct
- All 4 resistors extracted with correct values, footprints, and LCSC part numbers. Net names use the hierarchical UUID path format correctly. BOM groups R3/R4 together correctly (shared value/footprint/LCSC). KiCAD7 equivalent output is identical in structure.

### Incorrect
- The 'sheets' array lists bottom_sheet.kicad_sch at both index 2 and index 3 (same absolute path, different _sheet indices 2 and 3). This is because two hierarchical instances of the nested sheet both ultimately reference bottom_sheet.kicad_sch. The deduplication in the sheets list does not occur, which can mislead consumers into thinking the file exists twice as separate physical files.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00000722: False-positive label_shape_warnings for hierarchical sub-sheet labels

- **Status**: new
- **Analyzer**: schematic
- **Source**: test_resources_assembly_project_1_KiCAD6_bottom_sheet.kicad_sch.json
- **Created**: 2026-03-23

### Correct
(none)

### Incorrect
- bottom_sheet.kicad_sch has hierarchical labels A and B (input-shaped) that connect to the parent sheet. When analyzed standalone, the analyzer fires 'undriven_input_label' warnings on both nets. These are false positives — hierarchical input labels get their driver from the parent. The same issue appears in nested.kicad_sch and both KiCAD7 sub-sheets.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00000723: DFM board_size violation false positive for narrow panel boards

- **Status**: new
- **Analyzer**: pcb
- **Source**: test_resources_multiboard.kicad_pcb.json
- **Created**: 2026-03-23

### Correct
(none)

### Incorrect
- The board is 110x20mm. The DFM check triggers a 'higher fabrication pricing tier' violation because 110mm > 100mm threshold. However this is a KiKit multiboard panel/test fixture — only one dimension exceeds 100mm and the board area (22cm²) is well within standard fab limits. The check compares each dimension independently rather than using a combined area or aspect-ratio-aware threshold.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00000724: PCB analysis correct: component types, routing, via-in-pad detection, net lengths

- **Status**: new
- **Analyzer**: pcb
- **Source**: test_resources_conn.kicad_pcb.json
- **Created**: 2026-03-23

### Correct
- 6 footprints correctly classified (2 SMD, 2 THT, 2 mounting holes). 149 track segments, 9 vias, all nets routed. Via-in-pad correctly detected for J3 pogo pads 2 and 3. Edge clearance warnings for J1/J2 (courtyard extends outside board) are valid — J1/J2 courtyards start at x=93 but board edge is at x=105.5.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00000725: KiCad v8 file correctly parsed; footprint type reclassification (SMD→THT) reflects actual file content change

- **Status**: new
- **Analyzer**: pcb
- **Source**: test_resources_conn-fail-ignored.kicad_pcb.json
- **Created**: 2026-03-23

### Correct
- conn-fail-ignored (v20221018) correctly shows smd_count=0, tht_count=4 while older conn-fail (v20171130) shows smd_count=2, tht_count=2. The pogo (J3) and Molex (J4) footprints changed pad types across KiCad versions in the test repo. The analyzer faithfully reflects the file content — this is correct behavior.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
