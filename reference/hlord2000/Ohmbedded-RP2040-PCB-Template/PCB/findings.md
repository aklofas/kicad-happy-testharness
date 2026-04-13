# Findings: hlord2000/Ohmbedded-RP2040-PCB-Template / PCB

## FND-00000970: 2x2 key matrix (4 MX switches + 4 SOD-123 diodes) correctly detected

- **Status**: new
- **Analyzer**: schematic
- **Source**: PCB.kicad_sch.json
- **Created**: 2026-03-23

### Correct
- key_matrices detects a 2x2 matrix with GP0/GP1 as rows and GP2/GP3 as columns, 4 switches and 4 diodes, via topology detection. This is accurate.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00000971: 30 undriven_input_label warnings are false positives for a hierarchical sub-sheet

- **Status**: new
- **Analyzer**: schematic
- **Source**: switch_matrix.kicad_sch.json
- **Created**: 2026-03-23

### Correct
(none)

### Incorrect
- switch_matrix.kicad_sch is a sub-sheet consumed by the top-level PCB.kicad_sch. All GP* global labels are driven from the top-level sheet where the RP2040 is instantiated. Generating 30 undriven_input_label warnings for every GP* net is a false positive on a sub-sheet analyzed in isolation — the analyzer has no context that these are driven globally from the parent sheet.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00000972: 4-layer board reported as 2 copper layers used; Routing incomplete (20 unrouted nets) correctly flagged for template board; DFM tier correctly flagged as advanced due to 0.1mm annular rings; Board ...

- **Status**: promoted
- **Analyzer**: pcb
- **Source**: PCB.kicad_pcb.json
- **Created**: 2026-03-23

### Correct
- routing_complete=false, unrouted_net_count=20. This is correct — the RP2040 template has components placed but routing not started, as expected for a PCB template.
- The RP2040 requires fine-pitch vias (0.3mm drill, 0.1mm annular ring). The analyzer correctly identifies this as requiring advanced process and flags the single annular ring violation.
- edge_count=0 and bounding_box=null, indicating no Edge.Cuts outline. board_width_mm and board_height_mm are null. This is expected for a template that has not been shaped yet.

### Incorrect
- The board stackup defines F.Cu, In1.Cu, In2.Cu, and B.Cu (4 layers with explicit FR4 dielectrics). copper_layers_used=2 and copper_layer_names only lists F.Cu and B.Cu. The inner layers have no tracks (template board), but the design intent is a 4-layer board. The analyzer should report the stackup-defined layer count separately from the track-used layer count.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---
