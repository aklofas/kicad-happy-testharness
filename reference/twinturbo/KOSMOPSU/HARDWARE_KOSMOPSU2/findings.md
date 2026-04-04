# Findings: KOSMOPSU / HARDWARE_KOSMOPSU2

## FND-00000617: Component counts and BOM extraction correct; False positive: regulator input caps flagged as missing for U1 and U2; Protection devices only lists F1; F2 and F3 (also mains fuses) not detected; Line...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: HARDWARE_KOSMOPSU2.sch.json
- **Created**: 2026-03-23

### Correct
- 27 components parsed correctly: T1, F1-3, D1-5 (split into diode:3 + led:2 for D1/D4/D5 vs D2/D3), C1-6, U1-2, R1-2, J1-3, H1-5. Power rails (+12V, -12V, GND, LINE, NEUT, Earth) all captured.
- U1/L7812 detected as LDO, output +12V; U2/L7912 detected as LDO, output -12V. Subcircuit groupings with surrounding caps, fuses, and diodes are correct.

### Incorrect
- design_observations reports 'missing_caps: {input: __unnamed_3}' for U1/L7812 and 'missing_caps: {input: __unnamed_5}' for U2/L7912. In fact, C3 (0.2uF) is connected on __unnamed_3 (U1 input net) and C4 (0.2uF) is connected on __unnamed_5 (U2 input net). The analyzer fails to find decoupling caps on unnamed internal rails.
  (signal_analysis)
- signal_analysis.protection_devices only contains F1 (LINE fuse). F2 (1.5A 240V) and F3 (1.5A 240V) are secondary-side fuses on the DC rectifier output and are also protection devices that the analyzer misses. Even if their topology differs slightly, they should appear.
  (signal_analysis)

### Missed
- D1 is a KBP206 4-pin bridge rectifier IC forming the AC rectification stage. signal_analysis.bridge_circuits is empty. This is a clear rectifier topology that the analyzer should detect — especially given the 4 distinct net connections and the mains AC supply context.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00000618: kicad_version reported as 'unknown' for file_version 20221018; Edge clearance false positives for F1 (-16.77mm) and J1 (-3.4mm); Routing completeness, net count, board dimensions, and component pla...

- **Status**: promoted
- **Analyzer**: pcb
- **Source**: HARDWARE_KOSMOPSU2.kicad_pcb.json
- **Created**: 2026-03-23

### Correct
- 15 nets, 200 track segments, fully routed, board 153.7x73.9mm — all consistent with PCB source. Layer transitions (nets spanning both Cu layers without vias) noted correctly. No zone fills (no copper pours), 2 SMD-free logo footprints identified.

### Incorrect
- File version 20221018 corresponds to KiCad 6.x era. The analyzer outputs kicad_version: 'unknown' rather than detecting this as KiCad 6. Minor issue but misleading.
  (signal_analysis)
- F1 (googiefuse) and J1 (mains input connector) are intentionally mounted near or at the board edge — this is normal for mains connectors and through-board fuse holders. Reporting negative edge clearance as a warning is a false positive for components designed to mount at board edges.
  (signal_analysis)

### Missed
- LINE and NEUT are 240V mains nets routed with 0.5mm and 3.0mm tracks. The power_net_routing and current_capacity sections only analyze +12V and GND. LINE (28mm total, 0.5mm min width) and NEUT are mains voltage and should be analyzed for creepage/clearance and current capacity. The analyzer silently ignores them.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00000619: Layer completeness and drill classification correct for KOSMOPSU V0.1.4 gerbers; Alignment issue correctly detected: F.SilkS extends 315mm wide vs 153mm board

- **Status**: new
- **Analyzer**: gerber
- **Source**: Boards_KOSMOPSU V0.1.4.json
- **Created**: 2026-03-23

### Correct
- 9 gerber layers, 2 drill files (PTH/NPTH), 69 total holes, all required/recommended layers present. Drill tools classified correctly into component holes and mounting holes.
- alignment.aligned=false with issue 'Height varies by 7.0mm across copper/edge layers'. F.SilkS width 315.187mm is flagged via layer_extents. This is a real issue — the silkscreen content extends well beyond the board boundary, likely due to off-board text or logo art.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00000620: OLDPCB gerbers (KiCad 5.1.5) correctly parsed with single combined drill file; completeness.complete=true despite has_pth_drill=false and has_npth_drill=false

- **Status**: promoted
- **Analyzer**: gerber
- **Source**: Boards_OLDPCB.json
- **Created**: 2026-03-23

### Correct
- Older KiCad 5.1.5 format with single .drl file classified as type 'unknown' (no X2 PTH/NPTH attribute). 68 holes across 11 tools. Layer completeness passes correctly.

### Incorrect
- The OLDPCB has a single .drl file with 68 holes but it is classified as type 'unknown'. Both has_pth_drill and has_npth_drill are false, yet complete=true. This is slightly inconsistent — either the completeness check should flag the missing PTH drill classification, or the drill should be treated as PTH by default when it is the only drill file.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---
