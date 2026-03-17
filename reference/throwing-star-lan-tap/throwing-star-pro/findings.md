# Findings: throwing-star-lan-tap / throwing-star-pro

## FND-00000071: Legacy wire-to-pin connectivity completely broken: all 32 RJ45 data pins appear as isolated unnamed nets instead of being connected to SIG1-SIG8 labeled nets

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: throwing-star.sch.json
- **Related**: KH-016
- **Created**: 2026-03-13

### Correct
- 6 components correctly extracted (2 caps, 4 RJ45 connectors) with correct values, footprints, and MPNs from legacy custom fields
- All 8 labels (SIG1-SIG8) correctly identified
- GND correctly identified as only power rail
- BOM correctly extracts MPN (C315C221K1G5TA, RJHSE5080) and manufacturer from legacy Field entries

### Incorrect
- 32 RJ45 data pins appear as isolated __unnamed_0 through __unnamed_31 single-pin nets. All should be on SIG1-SIG8. SIG1-SIG3,SIG6 have zero pins resolved. SIG4,SIG5,SIG7,SIG8 each only have 1 cap pin (missing 3 RJ45 pins each).
  (nets)
- Reports 41 nets but actual design has only 9 (GND + SIG1-SIG8). Inflated by 32 spurious single-pin nets from broken wire tracing.
  (statistics.total_nets)

### Missed
(none)

### Suggestions
- This is a minimal repro case for KH-016: only 6 components, 8 signal wires, and pure wire-based connectivity. Good test fixture for debugging the legacy wire tracer.

---

## FND-00000072: PCB analysis correct overall but copper_layers_used=0 despite tracks on both Front and Back, and front_side/back_side component counts are 0 — RESOLVED: now reports copper_layers_used=2, front_side=6

- **Status**: resolved
- **Analyzer**: pcb
- **Source**: throwing-star.kicad_pcb.json
- **Created**: 2026-03-13

### Correct
- All 6 real components + 1 logo correctly identified with correct net assignments
- Track layer distribution correct: Front:130, Back:74. 204 total segments, 4 vias.

### Incorrect
- copper_layers_used=0 but tracks exist on both Front and Back copper layers
  (statistics.copper_layers_used)
- front_side=0 and back_side=0 but all 6 components are on Front
  (statistics.front_side)

### Missed
(none)

### Suggestions
- copper_layers_used should count layers from track.layer_distribution
- front_side/back_side should count footprints by their layer

---
