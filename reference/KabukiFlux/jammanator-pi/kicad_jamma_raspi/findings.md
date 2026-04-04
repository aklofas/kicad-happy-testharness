# Findings: jammanator-pi / kicad_jamma_raspi

## FND-00000249: JAMMA arcade interface (25 components). Multi-project schematic duplication: analyzer includes ALL project instances instead of filtering to target project (56 counted vs 25 actual). Zero signal detections correct for passive I/O buffer design.

- **Status**: confirmed
- **Analyzer**: schematic
- **Source**: jamma_raspi.kicad_sch.json
- **Created**: 2026-03-16

### Correct
(none)

### Incorrect
- Component count inflated from 25 actual to 56 reported - analyzer includes all project instances instead of filtering to target project
  (statistics)

### Missed
(none)

### Suggestions
- Filter schematic analysis to target project only in multi-project repos

---
