# Findings: Shrimp42 / Case_Rev2_PCB Bottom_PCB Bottom

## FND-00001355: Keyboard switches misclassified as 'relay' type; key_matrices detector fires zero results despite clear CL/RL matrix nets; Component counts correct: 87 total (42 switches + 42 diodes + 1 MCU + 2 co...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: Rev1_non-mirrored Rev1_kibod-01.kicad_sch
- **Created**: 2026-03-24

### Correct
- statistics.total_components=87 with unique_parts=4. BOM entries confirm 42 KEYSW switches, 42 diodes, 1 ProMicro MCU, 2 connectors (J1, J2). This matches the expected Shrimp42 full split layout of 42 keys with per-key diodes and a Pro Micro controller.

### Incorrect
- The 42 KEYSW components (keyboard switches) are categorized under component_types as 'relay' (42 relays) rather than a switch or keyboard-specific type. The footprint 'footprints:100-minimal-no-3d' and value 'KEYSW' are clear keyboard switch indicators, but the analyzer's symbol classification heuristic maps KEYSW to the relay category instead of a keyboard switch category. This causes the BOM type field to show 'relay' for all key switch entries.
  (statistics)

### Missed
- signal_analysis.key_matrices is an empty array even though the schematic has nets named CL0, CL1, CL2, CL3, CL4, CL5 (columns) and RL0, RL1, RL2, RL3 (rows), along with 42 KEYSW components and 42 diodes connected in a classic diode-per-key matrix. The analyzer should detect a 4×6 keyboard matrix but returns no results. The net names match common keyboard matrix naming conventions.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00001356: key_matrices detector returns empty despite CL/RL nets and 21 switch+diode pairs; Rev2 half-board component count correct: 46 components for one keyboard half

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: Rev2_Mirrored Rev2_Shrimp42-mirrored-rev2.kicad_sch
- **Created**: 2026-03-24

### Correct
- statistics.total_components=46 with 21 switches, 21 diodes, 1 ProMicro (U1), 1 TRRS connector (U2), and 2 connectors (J1, J2). Power rails GND and VCC are correctly identified. This is consistent with a 21-key left or right half of a 42-key split keyboard.

### Incorrect
(none)

### Missed
- signal_analysis.key_matrices is empty for the Rev2 Mirrored half-board schematic which has nets CL0-CL5 and RL0-RL3 with 21 KEYSW switches and 21 diodes — a standard 3-or-4-row × 6-column keyboard half matrix. The TRRS connector (U2) and ProMicro (U1) confirm it is a split half PCB. The matrix detector fails to trigger even with canonical row/column net names.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00001357: Case PCB schematic correctly reports zero components

- **Status**: new
- **Analyzer**: schematic
- **Source**: PCB Bottom.kicad_sch
- **Created**: 2026-03-24

### Correct
- The Case/Rev2/PCB Bottom schematic is a case plate (mounting holes and decorative outline only) with no electronic components. The analyzer correctly returns total_components=0, empty bom, empty nets, and empty signal_analysis. This is expected behavior for a mechanical-only PCB file used as a keyboard case layer.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001358: PCB dimensions and component count correct for a full 42-key split layout; PCB net count includes full matrix wiring for 42-key split keyboard

- **Status**: new
- **Analyzer**: pcb
- **Source**: Rev1_non-mirrored Rev1_kibod-01.kicad_pcb
- **Created**: 2026-03-24

### Correct
- Board dimensions 312.8×87.6mm match a side-by-side layout of two 21-key halves (each ~150mm wide with a gap). 87 footprints (42 switches + 42 diodes + 1 Pro Micro + 2 connectors), 2-layer, 442 track segments, 0 vias. Via count of 0 is plausible for a through-hole keyboard. The net_count of 65 includes the CL0-CL5 and RL0-RL3 matrix lines visible in the PCB net list.
- net_count=65 in statistics and 66 unique nets in net_analysis. Named nets include CL0-CL5 (6 columns), RL0-RL3 / RR0-RR3 (8 rows split L/R), RC0-RC3 / CR1-CR5 (right-side rows/columns), plus per-diode unnamed nets. This structure is correct for a combined left+right half schematic with separate row/column groups for each side.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001359: Case plate PCB correctly shows 7 footprints (6 mounting holes + 1 logo), no nets or tracks

- **Status**: new
- **Analyzer**: pcb
- **Source**: PCB Bottom.kicad_pcb
- **Created**: 2026-03-24

### Correct
- footprint_count=7 with 6 THT mounting holes (footprints:hole-m2) and 1 board_only logo graphic. net_count=0, track_segments=0, routing_complete=true. The 2 copper fill zones (F.Cu and B.Cu) are correctly detected as decorative pours over the full board area with fill_ratio ~0.97. Board dimensions 147.3×89.0mm match the Rev2 half keyboard outline.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001360: Rev2 half PCB statistics plausible: 52 footprints, mixed SMD/THT, 47 vias

- **Status**: new
- **Analyzer**: pcb
- **Source**: Rev2_Mirrored Rev2_Shrimp42-mirrored-rev2.kicad_pcb
- **Created**: 2026-03-24

### Correct
- footprint_count=52 with 21 SMD (smd_count=21) and 31 THT (tht_count=31), 592 track segments, 47 vias, 2-layer 147×89mm board. The presence of vias differentiates Rev2 from Rev1 (which has 0 vias). The SMD count of 21 likely reflects SMD diodes used in Rev2 vs through-hole in Rev1. This is consistent with a hardware revision upgrading to SMD components.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001361: Gerber set complete with correct layer count, dimensions, and drill counts; Drill classification correctly identifies switch mounting pins as NPTH component holes

- **Status**: new
- **Analyzer**: gerber
- **Source**: Rev1_non-mirrored Rev1_gerber
- **Created**: 2026-03-24

### Correct
- layer_count=2, board 312.86×87.68mm, 9 signal/mask/silk/edge layers all present, complete=true. total_holes=338: 212 PTH (84 diode pads at 0.99mm + 20 connector pins + 24 MCU pins + 84 switch pads at 1.50mm) + 126 NPTH (84 switch mounting pins at 1.80mm + 42 corner/mounting holes at 3.99mm). Counts are internally consistent and match the 87-component BOM.
- drill_classification assigns 84 holes at 1.80mm as NPTH component holes — these are PCB-mount mechanical pins on MX-compatible keyboard switches. 42 holes at 3.99mm are mounting holes for case standoffs. The x2_attributes-based classification correctly distinguishes functional component holes from mounting holes.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001362: Case plate gerber correctly reports only 6 holes (mounting hardware) and minimal copper

- **Status**: new
- **Analyzer**: gerber
- **Source**: gerber
- **Created**: 2026-03-24

### Correct
- statistics.total_holes=6 (matching 6 M2 mounting holes in the PCB file), gerber_files=9 (correct for 2-layer set), total_flashes=24 (pad flashes for 6 2-pad mounting holes), complete=true. The near-zero trace content and absence of paste apertures confirms this is a mechanical-only PCB used as a keyboard case layer.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001363: Rev2 gerber layer count, dimensions, and drill totals are consistent with PCB analysis

- **Status**: new
- **Analyzer**: gerber
- **Source**: Rev2_Mirrored Rev2_gerber
- **Created**: 2026-03-24

### Correct
- layer_count=2, board 147.37×89.06mm matches PCB analyzer output of 147.32×89.011mm (small rounding difference from gbrjob vs edge-cuts calculation). total_holes=374 (PTH + NPTH combined), higher than Rev1 per-half equivalent due to via holes and SMD diode footprints contributing to the count. complete=true with all 9 expected layers present.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
