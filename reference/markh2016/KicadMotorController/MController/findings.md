# Findings: markh2016/KicadMotorController / MController

## FND-00000750: Q1 (BT139-600 TRIAC) misclassified as 'transistor' type; assembly_complexity smd_count=4 wrong — all components are THT; Component count, BOM, net extraction, and signal analysis all correct

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: MController.kicad_sch.json
- **Created**: 2026-03-23

### Correct
- 11 components, 10 nets, BOM values and footprints correctly extracted. RC filter detection found the R2+C1/C2 phase-shift network (47K, 100nF, 33.86 Hz cutoff). No false positives on voltage dividers, regulators, or bus interfaces. Missing MPN flagged for 10/11 components (only FL1 has MPN) — correct.

### Incorrect
- Q1 has lib_id 'Triac_Thyristor:BT139-600' — it is a TRIAC, not a BJT/MOSFET transistor. The component type is reported as 'transistor' throughout (bom, components, statistics). TRIACs are bidirectional thyristors and should be a distinct type. The transistor_circuits detector also found nothing, which is consistent with no transistor present, but the classification is still wrong.
  (signal_analysis)
- The schematic reports smd_count=4, tht_count=7, package_breakdown={'THT':7,'other_SMD':3,'unknown':1}. However all 11 components use through-hole footprints. The bug: J1 ('TerminalBlock_RND'), J2 ('TerminalBlock_RND'), and F1 ('Fuse:Fuseholder_Cylinder') don't have 'THT' in their footprint library name, so the analyzer classifies them as 'other_SMD'. J3 (no footprint) is 'unknown'. The PCB correctly reports smd_count=0, tht_count=11. The schematic analyzer should also check the footprint name string for known THT patterns beyond just the library prefix.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00000751: Single-sided routing (B.Cu only), component counts, courtyard overlaps, and edge clearance warnings all correct

- **Status**: new
- **Analyzer**: pcb
- **Source**: MController.kicad_pcb.json
- **Created**: 2026-03-23

### Correct
- Correctly identifies 11 THT components (smd=0, tht=11), single copper layer used (B.Cu), 49 track segments, routing complete with 0 unrouted nets. Detected 3 courtyard overlaps (FL1/C1, R1/J3, R2/DIAC1) and 3 edge clearance violations (R2 at -8mm, FL1 at -3.4mm, J2 at -1.4mm). Board is 66.24x55.22mm. All of these appear accurate.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00000752: False alignment warning — Edge.Cuts width mismatch caused by dimension annotations, not a real misalignment; Gerber analyzer attempts to open .git directory as a gerber file; Gerber completeness, d...

- **Status**: promoted
- **Analyzer**: gerber
- **Source**: _home_aklofas_Projects_kicad-happy-testharness_repos_KicadMotorController.json
- **Created**: 2026-03-23

### Correct
- Correctly identifies all 6 gerber layers per gbrjob, 2 drill files (26 PTH + 1 NPTH mounting hole), no vias, 11 components all front-side THT. Trace widths 1.4mm and 1.8mm correctly extracted. No spurious missing-layer warnings despite the 2-layer stackup having only B.Cu copper gerber (gbrjob-driven expected_layers correctly excludes F.Cu).

### Incorrect
- Gerber alignment flagged 'Width varies by 15.1mm across copper/edge layers' (Edge.Cuts=72.1mm vs B.Cu=57.1mm). The board outline is a simple rectangle (~66mm wide), but the Edge.Cuts gerber contains 226 draw strokes — far more than a rectangle requires. KiCad places dimension annotations (arrows, witness lines, text) on the Edge.Cuts layer, which inflates the computed extents. This is a systematic false positive for boards with PCB dimensions drawn on Edge.Cuts.
  (signal_analysis)
- The gerbers list includes an entry for '.git' with error '[Errno 21] Is a directory'. The analyzer is scanning all directory entries including .git. It handles the error gracefully but should filter out directories and non-gerber files before attempting to parse them. This creates noise in the output.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---
