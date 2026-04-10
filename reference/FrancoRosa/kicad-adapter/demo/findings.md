# Findings: kicad-adapter / demo_demo

## FND-00002236: 1206 test points correctly identified as test_point type with no false detectors firing

- **Status**: new
- **Analyzer**: schematic
- **Source**: schematic_kicad-adapter_demo_demo.kicad_sch.json
- **Created**: 2026-03-24

### Correct
- The kicad-adapter schematic is a pure test-point adapter board with 1206 PILE/INV-prefixed TestPoint components. The analyzer correctly classifies all of them as test_point type, reports unique_parts=1 (all share the same footprint/value), and properly fires no signal-path detectors. No power rails are present, which is also correctly reflected.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00002237: routing_complete=true is misleading when 1166 of 1186 nets are stub unconnected-(PILE-Pad1) nets; board dimensions null and smd_count/tht_count both 0 despite 1206 footprints present

- **Status**: promoted
- **Analyzer**: pcb
- **Source**: pcb_kicad-adapter_demo_demo.kicad_pcb.json
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
- The PCB reports routing_complete=true and unrouted_count=0, which is technically accurate (no ratsnest unrouted segments), but the connectivity section shows only 20 of 1186 nets are actually routed. The remaining 1166 nets are single-pad unconnected-(PILExxx-Pad1) stubs where the test points are not connected to each other by design. The stat routed_nets=20 vs total_nets_with_pads=1186 creates a confusing picture without any explanatory flag for this expected single-pad-net pattern.
  (statistics)
- The PCB has 1206 footprints but board_width_mm and board_height_mm are null because Edge.Cuts has no outline (edge_count=0). Additionally, smd_count=0 and tht_count=0 despite all 1206 footprints being present on F.Cu with pads. This is because all footprints have the 'exclude_from_pos_files' attribute set, causing the analyzer to miscategorize or exclude them from the SMD/THT count. The footprint_count=1206 is correct but the component type breakdown is lost.
  (statistics)

### Missed
(none)

### Suggestions
(none)

---
