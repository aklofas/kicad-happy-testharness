# Findings: SOLARMINI01 / hw_sch_pcb_SOLARMINI01B

## FND-00001294: SPV1040 MPPT IC detected as switching regulator with L1 inductor; design_observations incorrectly flags missing output caps for U1; Voltage divider not detected: R7(560k)/R8(270k) feedback network ...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: SOLARMINI01B.kicad_sch
- **Created**: 2026-03-24

### Correct
- power_regulators correctly identifies U1 as switching topology with inductor L1. current_sense shunt R6=0R47 correctly detected. RC and LC filters found.
- protection_devices correctly identifies D2=SMBJ5.0A as a TVS clamping device on the internal switching node.

### Incorrect
- The observation claims output rail '__unnamed_1' has missing caps, but C1, C6, C7 (47uF tantalum caps) are present on the output side. The issue is that unnamed nets prevent correct cap association.
  (signal_analysis)

### Missed
- R7=560k and R8=270k form a feedback voltage divider for the SPV1040 MPPT IC. voltage_dividers is empty. This is a real signal path the analyzer missed.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00001295: PCB stats correct: 28 footprints, 2-layer, 40x40mm, routing complete

- **Status**: new
- **Analyzer**: pcb
- **Source**: SOLARMINI01B.kicad_pcb
- **Created**: 2026-03-24

### Correct
- Component count (28), layer count (2), board dimensions (40.132x40.132mm), and routing_complete=true all look accurate.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001296: Gerber set complete with 9 layers, all present and aligned; NPTH drill file reports 0 holes but file exists — NPTH may just be empty

- **Status**: promoted
- **Analyzer**: gerber
- **Source**: hw_cam_profi
- **Created**: 2026-03-24

### Correct
- 9 gerber files plus 2 drill files, completeness=true, aligned=true. F.Paste present but empty (0 flashes) which is correct for an all-SMD-back design.

### Incorrect
- has_npth_drill=true from gbrjob but NPTH drill file has hole_count=0. This is technically correct (empty file is present) but could mislead — a note that the NPTH file is empty would be more accurate.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---
