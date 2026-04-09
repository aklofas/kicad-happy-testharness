# Findings: hyves42/kicad-proto-pcb / protoboard

## FND-00002511: Protoboard PCB with 1726 copper pads, 12 SOIC6 areas, 12 SOT23 areas, 1 TQFP64 area, and 4 mounting holes. Component counts and net building are correct, but type classifications for custom prototyping symbols are inaccurate.

- **Status**: confirmed
- **Analyzer**: schematic
- **Source**: protoboard.sch.json
- **Created**: 2026-04-09

### Correct
- Total component count of 1755 matches schematic exactly (1726 PAD + 12 PROTO_SOIC6 + 12 PROTO_SOT23 + 1 PROTO_TQFP64 + 4 HOLE)
- Wire count of 284 matches schematic
- H1-H4 (HOLE) correctly classified as mounting_hole
- Signal analysis correctly returns empty results for all detector categories (no active circuits on a bare protoboard)

### Incorrect
- TQFP1 (PROTO_TQFP64, 64-pin prototyping footprint area) classified as 'transformer' — it is a prototyping pad array for TQFP packages, not a transformer
  (statistics.component_types.transformer)
- 1617 PAD components with U-prefix classified as 'ic' — these are bare copper pads on a protoboard, not integrated circuits. The reference prefix 'U' is misleading the classifier
  (statistics.component_types.ic)

### Missed
(none)

### Suggestions
- PROTO_TQFP64 -> transformer misclassification likely from pin count heuristic; should not map 64-pin custom symbols to transformer without stronger evidence
- Consider recognizing PAD as a generic/passive type rather than defaulting to ic based on U-prefix

---
