# Findings: tmk/alps64_plate / alps64

## FND-00001961: Correct component count of 87 (1 connector + 86 KEYSW) for plate schematic; 86 KEYSW components misclassified as 'relay' in plate schematic (same issue as alps64); Key matrix not detected in plate ...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: alps64.sch.json
- **Created**: 2026-03-24

### Correct
- The alps64_plate schematic contains only P1 (CONN_01X01 ground connector) in the main sheet and 86 KEYSW components in matrix.sch. The analyzer correctly counts 87 total components with unique_parts=2 (the connector and KEYSW types). This is the plate PCB schematic, not the main controller board.

### Incorrect
- All 86 KEYSW components in the plate schematic's matrix.sch are typed as 'relay' instead of 'switch'. This is the same KEYSW misclassification as in the alps64 main schematic. The component_types shows relay=86, connector=1.
  (statistics)

### Missed
- The alps64_plate matrix.sch has the same 8 row and 8 column hierarchical labels (row0-row7, col0-col7) as the alps64 main board, and the same 86 KEYSW components. However the analyzer reports an empty key_matrices list. This is because without a controller IC connected to those hierarchical labels in the main sheet, the row/col nets are not promoted to globally named nets — they appear as __unnamed_N in the output. The key matrix detector relies on net names containing 'row'/'col', which fails when nets are unnamed. The analyzer should ideally detect the matrix from hierarchical label names in sub-sheets even without global resolution.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00001962: Plate PCB correctly identified as a switch plate with 73 SMD footprints and no traces; Plate PCB DFM board-size violation correctly flagged (285x95mm exceeds 100x100mm tier)

- **Status**: new
- **Analyzer**: pcb
- **Source**: alps64.kicad_pcb.json
- **Created**: 2026-03-24

### Correct
- The alps64_plate PCB is a keyboard switch plate that provides mechanical switch cutouts. It has 73 footprints (all SMD — the cutout footprints are registered as SMD), zero track segments, only 1 net (GND), and routing_complete=True (nothing to route). The board has two copper zones on GND covering F.Cu and B.Cu. The 285x95mm board dimensions match the main keyboard PCB.
- Same as the main alps64 PCB, the plate PCB exceeds the 100x100mm standard fab tier at 285x95mm. The analyzer correctly identifies this DFM violation. The silkscreen correctly shows board identification text ('TMK Alps64 AEK plate', 'Ver.B_flip 2018/04') on B.SilkS.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
