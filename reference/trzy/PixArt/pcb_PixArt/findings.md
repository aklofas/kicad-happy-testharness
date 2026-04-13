# Findings: trzy/PixArt / pcb_PixArt

## FND-00001089: Component counts, power rails, and no-connect counts are accurate; Dual I2C interface on PAJ7025 correctly detected (G7_SCL_M/G8_SDA_M and CP_SCL/CP_SDA); Decoupling analysis empty despite C1 (10uF...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: PixArt.sch
- **Created**: 2026-03-23

### Correct
- 4 components (1 IC, 2 caps, 1 connector), 3 power rails, 13 no-connects all match the design. Legacy KiCad 5 unnamed nets handled correctly.
- Both I2C interfaces identified with has_pull_up: false, which is accurate — no pull-up resistors exist in the schematic.

### Incorrect
(none)

### Missed
- The decoupling_analysis section is empty. C1 and C2 are on net __unnamed_20 (their positive pins) while their negative pins go to GND. No decoupling relationship to VCC was detected — possibly because caps connect to an unnamed net rather than VCC directly in the legacy netlist.
  (signal_analysis)
- Pins 14 (VSSD), 17 (VDDMA), 20 (VSSD_LED) have power_in type but sit on unnamed single-pin nets (__unnamed_14, __unnamed_17, __unnamed_10). These look like floating power pins — a real design concern not flagged in erc_warnings or design_observations.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00001090: DFM annular ring violation correctly detected (0.1mm, requires advanced process); GND copper pour on B.Cu correctly detected and associated with all 4 components; Board outline reports 5 edges for ...

- **Status**: promoted
- **Analyzer**: pcb
- **Source**: PixArt.kicad_pcb
- **Created**: 2026-03-23

### Correct
- All 5 vias have 0.1mm annular ring. Correctly classified as advanced tier DFM requirement.
- Zone covers full board on B.Cu, fill_ratio 0.898, all 4 components in ground domain.

### Incorrect
- The edge_cuts section has 5 lines including a duplicate/redundant segment (128.27,100.33 to 128.27,81.28 overlaps the left side). This should be flagged as an outline anomaly but no warning is generated.
  (signal_analysis)

### Missed
- U1 is an SMD footprint with 20 pads, yet pad_summary.smd_apertures = 0 and smd_ratio = 0.0. The smd_source is 'x2_aperture_function' which relies on gerber data not PCB data, so the PCB analyzer should derive SMD counts from footprint type directly.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00001091: Complete layer set detected, F.Paste missing correctly flagged for SMD design; Alignment mismatch correctly detected — copper layers don't span full board extent

- **Status**: new
- **Analyzer**: gerber
- **Source**: gerbers_PCBUnlimited.2
- **Created**: 2026-03-23

### Correct
- All required layers present. F.Paste absence for a board with SMD U1 is a valid recommendation.
- Components are placed asymmetrically (U1 near center, caps and connector in lower portion), so copper extents naturally differ from Edge.Cuts. The 19mm/14mm variance is genuine and correctly reported.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001092: Older gerber set correctly identified as incomplete — missing B.Mask and F.Mask; PixArt-NonPlatedThroughHole.drl misclassified as PTH instead of NPTH; B.Cu layer extent 182mm far exceeds board size...

- **Status**: promoted
- **Analyzer**: gerber
- **Source**: gerbers_PCBUnlimited
- **Created**: 2026-03-23

### Correct
- complete: false with missing_required [B.Mask, F.Mask] is accurate for this 6-file set.

### Incorrect
- The drill file named 'NonPlatedThroughHole' is classified as type PTH in the drills array. The NPTH indicator was missed (possibly the file lacks the Excellon NPTH header marker). This causes the 4 x 0.9mm holes to be counted as PTH and the has_npth_drill flag to be false.
  (signal_analysis)
- The older B.Cu gerber reports width=182mm vs Edge.Cuts 49.53mm. This massive discrepancy (likely a mis-scaled or offset legacy export) causes alignment to flag a 151.8mm variance but no separate 'layer_outside_board' warning is generated.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---
