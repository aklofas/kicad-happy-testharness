# Findings: mlab-modules/STEPUPDC01 / hw_sch_pcb_STEPUPDC01A

## FND-00001300: MAX5026 step-up output_rail incorrectly identified as 'Vin' instead of 'Vout'; Feedback voltage divider R2(140k)/R3(6k49) from Vout to FB to GND not detected; Missing footprints for U1 and D2 corre...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: STEPUPDC01A.kicad_sch
- **Created**: 2026-03-24

### Correct
- missing_footprint lists U1 and D2, which are rescue-library symbols without assigned footprints in this legacy KiCad 5 project. This is accurate.

### Incorrect
- power_regulators sets output_rail='Vin' for U1=MAX5026. This is a step-up (boost) converter: Vin is the input and Vout is the output. The analyzer appears to have confused input and output rails, likely due to net naming in this legacy KiCad 5 schematic.
  (signal_analysis)

### Missed
- The MAX5026 datasheet shows the feedback network sets Vout. R2=140k connects Vout to FB, R3=6k49 connects FB to GND — a classic 2-resistor voltage divider. voltage_dividers is empty.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00001301: smd_apertures=0 and smd_ratio=0.0 is wrong — board has 12 SMD components; Alignment issue correctly detected in old KiCad 5 gerbers; Missing F.Paste layer correctly flagged as recommended-only (not...

- **Status**: promoted
- **Analyzer**: gerber
- **Source**: hw_cam_profi
- **Created**: 2026-03-24

### Correct
- aligned=false with 'Height varies by 2.2mm across copper/edge layers' is a real observation for this 2018-era gerber set where layer extents differ.
- missing_recommended includes F.Paste but complete=true. This is correct — the old-style KiCad 5 export omits the F.Paste layer. The distinction between required and recommended is handled correctly.

### Incorrect
- The old KiCad 5 gerbers lack X2 aperture function attributes, so smd_source='x2_aperture_function' yields 0 SMD apertures. The PCB has 12 SMD parts (U1, D1, D2, C1-C6, R1-R4). The analyzer should fall back to diameter heuristics for SMD detection when X2 data is absent.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001302: PCB correctly parsed: 20 footprints, 2-layer, 19.8x40.1mm, routing complete with 52 vias; same_layer_foreign_zones reports C5/C6/R3 pads near GND zone as potential issue, but these are Vout capacit...

- **Status**: promoted
- **Analyzer**: pcb
- **Source**: STEPUPDC01A.kicad_pcb
- **Created**: 2026-03-24

### Correct
- Statistics match the design (step-up converter on a narrow card-edge form factor). via_count=52 is high for a small board but consistent with the dense routing shown in the net_lengths.

### Incorrect
- C5=100nF, C6=1uF/50V, and R3=6k49 pad 1 (FB node) are flagged as having foreign GND zones nearby. For a step-up converter, output caps and feedback resistors intentionally have their negative pin on GND — this is correct design practice, not a problem.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---
