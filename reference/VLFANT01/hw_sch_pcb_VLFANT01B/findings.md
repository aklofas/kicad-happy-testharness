# Findings: VLFANT01 / hw_sch_pcb_VLFANT01B

## FND-00001790: Component count correct: 9 total (5 connectors + 4 mounting holes); Mounting holes M1-M4 classified as 'other' instead of 'mounting_hole'; No signal detectors triggered for passive antenna intercon...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: VLFANT01B.kicad_sch.json
- **Created**: 2026-03-24

### Correct
- VLFANT01B has 5 connectors (J1-J3 RJ45, J7 SMA, J9 2×3 header) and 4 mounting holes (M1-M4), totaling 9. The analyzer reports total_components=9 matching the source schematic exactly.
- VLFANT01B is a passive RF interconnect panel (VLF antenna signal router) with only connectors and mounting holes. All 21 signal path detectors correctly return empty arrays — no active components, no filters, no regulators, no protocols.

### Incorrect
- The four HOLE-type components (M1-M4, library VLFANT01B-rescue:HOLE) are classified as component_type='other' instead of 'mounting_hole'. Other designs with similar mounting hole footprints are classified correctly. The rescue library prefix may be preventing the type classifier from recognizing the HOLE symbol name.
  (statistics)

### Missed
(none)

### Suggestions
- Fix: Mounting holes M1-M4 classified as 'other' instead of 'mounting_hole'

---

## FND-00001791: 2-layer PCB with 9 footprints and full routing; GND zone stitching correctly identified on both copper layers

- **Status**: new
- **Analyzer**: pcb
- **Source**: VLFANT01B.kicad_pcb.json
- **Created**: 2026-03-24

### Correct
- PCB reports 9 footprints (matches schematic), 2 copper layers (F.Cu, B.Cu), 151 track segments, 47 vias, and routing_complete=true with 0 unrouted nets. All values consistent with the source .kicad_pcb file.
- Three GND copper zones are detected (one on F.Cu, two on B.Cu) with 41 stitching vias at 0.4 mm drill. Ground domain analysis correctly shows 3 components (J2, J3, J9) connected to GND.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
