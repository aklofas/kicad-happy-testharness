# Findings: mlab-modules/PINHOLDER01 / hw_sch_pcb_PINHOLDER01

## FND-00001039: Small utility board (5 footprints, 3 nets) correctly analyzed

- **Status**: new
- **Analyzer**: pcb
- **Source**: PINHOLDER01.kicad_pcb
- **Created**: 2026-03-23

### Correct
- Correctly identifies J1 on B.Cu (back side SMD connector), two mounting holes grounded to GND zone on B.Cu, two test points. Zone fill ratio and copper presence analysis are accurate.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001040: Gerber alignment flagged as misaligned but variance is normal (mask/silk smaller than copper); 3.0mm mounting hole drills classified as 'component_holes' instead of 'mounting_holes'

- **Status**: new
- **Analyzer**: gerber
- **Source**: hw_cam_profi_gbr
- **Created**: 2026-03-23

### Correct
(none)

### Incorrect
- alignment.aligned=false citing 'Width varies by 9.1mm, Height varies by 6.6mm'. This is expected: solder mask and silkscreen only cover component areas, not the full board extent. Comparing their extents to Edge.Cuts/copper introduces false misalignment warnings. Only copper layers and Edge.Cuts should be compared for alignment.
  (signal_analysis)
- drill_classification shows mounting_holes.count=0 and component_holes.count=2 for the 3.0mm PTH drills. These are M3 mounting holes (footprint MountingHole_3mm), not component drills. The X2 attribute says 'ComponentDrill' because KiCad exports grounded mounting holes as PTH ComponentDrill, but the gerber analyzer should use diameter heuristics (>=2.5mm PTH with no net signal) to reclassify them as mounting holes.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001041: Minimal board (5 components, 3 nets) correctly parsed with accurate test point coverage; M3/M4 mounting holes flagged in missing_mpn sourcing audit

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: PINHOLDER01.kicad_sch
- **Created**: 2026-03-23

### Correct
- Test points TP1/TP2 covering 2 nets correctly identified. GND PWR_FLAG warning correctly raised. Missing MPN audit correct (all 3 sourced components lack MPN).

### Incorrect
- Mounting holes (M3, M4) have no MPN by design — they are mechanical, not electrical components. Including them in missing_mpn and sourcing audit inflates the mpn_coverage gap. The sourcing audit should exclude mounting holes from the MPN coverage metric.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---
