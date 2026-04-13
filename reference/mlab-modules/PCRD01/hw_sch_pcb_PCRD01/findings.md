# Findings: mlab-modules/PCRD01 / hw_sch_pcb_PCRD01

## FND-00001074: Op-amp circuit detection correct: U1 (MAX4475) and U2 (AD8692) both found with configurations; assembly_complexity reports 41 SMD, 0 THT — misses 9 THT connectors/mounting holes

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: PCRD01.kicad_sch
- **Created**: 2026-03-23

### Correct
- U1 detected as charge-amplifier/compensator with R4=2M feedback, C4=1pF. U2 detected in two roles: compensator (lowpass with R6/C11) and inverting amplifier (gain=-1.95, matching '2x' annotation). Signal chain analysis is largely correct.

### Incorrect
- J1 (2x03 straight header), J2 (2x05), J3 (1x03), J4 (1x02), J5 (2x03) are THT pin headers. P1-P4 are 3mm mounting holes (THT). PCB output confirms 10 THT footprints. The schematic assembly_complexity analyzer does not classify 'Straight', 'Mlab_Pin_Headers', 'MountingHole' footprints as THT.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001075: U1 (MAX4475 in MLAB_IO:SOT-23-6) classified as through_hole — it is SMD; 2-layer routing, dimensions, net count, zone coverage all correct

- **Status**: promoted
- **Analyzer**: pcb
- **Source**: PCRD01.kicad_pcb
- **Created**: 2026-03-23

### Correct
- 2-layer board (F.Cu, B.Cu), 50.292 x 29.972mm, 39 footprints, 18 nets, 133 segments, 25 vias, 2 zones, routing complete. Component refs correctly extracted (C1-C15, J1-J5, P1-P4, Q1, R1-R12, U1, U2).

### Incorrect
- Raw PCB file confirms all 6 pads of U1 are '(pad smd rect)' with B.Cu/B.Paste/B.Mask layers. The footprint has '(attr smd)' attribute. The PCB analyzer classifies it as through_hole, likely because the custom MLAB_IO library name does not match a known SMD pattern. This inflates THT count from 9 to 10 and deflates SMD from 30 to 29.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001076: Layer completeness, drill classification, and component count from X2 attributes are correct; Gerber alignment flagged as misaligned with 17.8mm variance — likely a false positive

- **Status**: promoted
- **Analyzer**: gerber
- **Source**: hw_cam_profi_gbr
- **Created**: 2026-03-23

### Correct
- All 9 expected layers found (F.Cu, B.Cu, F/B Mask, F/B Paste, F/B SilkS, Edge.Cuts). PTH: 56 holes (25 vias at 0.635mm, 27 component at 0.889mm, 4 large at 3.0mm). NPTH file present but empty (0 holes). Component count from X2: 39 total matches PCB footprint count. SMD ratio 0.7 is plausible.

### Incorrect
- F.Cu layer reports 67.978 x 47.658mm extent vs Edge.Cuts 50.292 x 29.972mm — a 17.7mm discrepancy. However B.Mask, F.Mask, and drill extents are all within expected range. This discrepancy suggests F.Cu has copper drawing outside the board edge (possibly a frame/panel artifact or silkscreen-like drawing on copper). The blanket 'aligned: false' verdict may be too aggressive — the other layers are consistent. The analyzer should report per-layer vs edge alignment individually rather than one global flag.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---
