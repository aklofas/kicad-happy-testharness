# Findings: SATABAL01 / hw_sch_pcb_SATABAL01

## FND-00001183: RF balun transformer circuit not detected in signal_analysis — rf_chains and isolation_barriers both empty; Component counts correct: 2 transformers, 3 connectors, 4 mounting holes, 9 total

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: SATABAL01.kicad_sch
- **Created**: 2026-03-23

### Correct
- BOM and component_types match the actual design. The ETC1-1-13 transformers are correctly typed as 'transformer'. Mounting holes are excluded from BOM (in_bom: false) and correctly counted separately.

### Incorrect
(none)

### Missed
- This board is explicitly an RF balun: two ETC1-1-13 1:1 transmission-line transformers converting between unbalanced SMA/MCX coax and balanced SATA differential pairs. Neither rf_chains nor isolation_barriers captures this. The transformers are classified only as generic 'transformer' type components with no RF/balun context.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00001184: Zone fill_ratio of 1.451 is physically impossible (>1.0 means filled area exceeds outline area); Missing revision warning is a false positive — 'SATABAL01A' silkscreen text contains a revision suffix

- **Status**: new
- **Analyzer**: pcb
- **Source**: SATABAL01.kicad_pcb
- **Created**: 2026-03-23

### Correct
(none)

### Incorrect
- The GND zone reports outline_area_mm2: 1386.3 but filled_area_mm2: 2011.41, giving fill_ratio: 1.451. A fill ratio > 1.0 is impossible — filled copper cannot exceed the zone outline polygon area. This is likely a calculation error when the zone spans two layers (F.Cu + B.Cu) and the combined area is compared against a single-layer outline. The per-layer breakdown (B.Cu: 974.98, F.Cu: 1036.42, sum ≈ 2011.4) shows the issue: filled_area_mm2 accumulates both layers but outline_area_mm2 reflects only one layer's polygon.
  (signal_analysis)
- The PCB analyzer reports 'missing_revision' because it did not find 'Rev', 'V1.0', etc. However, the silkscreen includes the text 'SATABAL01A' where the 'A' suffix is the revision designator — a common convention for MLAB/professional designs. The analyzer's revision-detection heuristic only looks for explicit 'Rev'/'V' prefixes and misses letter-suffix revision conventions.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001185: Gerber completeness and layer alignment correctly verified — all 9 layers present, aligned, complete; mounting_holes count is 0 despite 4 x 3mm drilled mounting pads (H1-H4) present

- **Status**: promoted
- **Analyzer**: gerber
- **Source**: hw_cam_profi_gbr
- **Created**: 2026-03-23

### Correct
- completeness.complete: true, all expected layers found, has_pth_drill and has_npth_drill both present. Layer extents are consistent across copper, mask, and drill files.

### Incorrect
- The drill_classification reports mounting_holes.count: 0 and component_holes.count: 23. The four 3mm holes for H1-H4 are classified as component holes rather than mounting holes. Since the gerber NPTH file is empty (0 holes) and the 3mm holes are plated PTH (they are pads connected to GND), the x2_attribute classification method cannot distinguish mounting from component holes purely from X2 data. This is a known limitation but results in a misleading count.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---
