# Findings: HadesFCS / Hardware_HadesNT_HadesNT

## FND-00000082: HadesNT flight controller - 102 components, zero signals due to KH-016; rich component set suggests many missed detections

- **Status**: confirmed
- **Analyzer**: schematic
- **Source**: repos/HadesFCS/Hardware/HadesNT/HadesNT.sch
- **Related**: KH-016
- **Created**: 2026-03-14

### Correct
- Component types well-classified: 7 ICs, 7 transistors, 32 caps, 25 resistors, 2 speakers, 1 crystal, 1 fuse
- Power rails identified: +3V3, +5V, GND, VBUS, VCC, VDD, VDDA, VS - comprehensive for a flight controller with analog domain
- 1 DNP part correctly identified
- 263 nets and 278 wires parsed, 35 no-connect markers counted

### Incorrect
(none)

### Missed
- Zero signal analysis on a board with 7 transistors, 1 crystal, 1 fuse, 2 inductors - all blocked by KH-016
  (signal_analysis)
- Crystal circuit not detected despite crystal component being enumerated
  (signal_analysis.crystal_circuits)
- 7 transistor circuits not analyzed - flight controllers use MOSFETs for motor outputs and power switching
  (signal_analysis.transistor_circuits)
- VDDA rail suggests analog domain (ADC reference) with dedicated filtering - not analyzed
  (signal_analysis)
- Speaker/buzzer circuits (2 speakers) not detected
  (signal_analysis.buzzer_speaker_circuits)
- Fuse as protection device not detected
  (signal_analysis.protection_devices)

### Suggestions
- Fix KH-016 to unlock signal analysis
- Good test case for transistor circuit and buzzer/speaker detection once wiring is fixed

---

## FND-00000302: Gerber review: 4-layer (80x50mm). False alignment failure from normal copper edge clearance

- **Status**: new
- **Analyzer**: gerber
- **Source**: Hardware/HadesNT/gerbers/
- **Related**: KH-177, KH-183, KH-184
- **Created**: 2026-03-18

### Correct
- 4.3mm mounting holes (4x) correctly classified -- M4 for vibration-resistant flight controller

### Incorrect
- Drill extent coordinates not normalized to mm -- values 1000x too large. Affects alignment.layer_extents for drill entries
  (alignment.layer_extents)
- pad_summary.smd_apertures=0 and smd_ratio=0.0 wrong -- F.Paste has hundreds of flashes
  (pad_summary)
- Combined PTH+NPTH drill file classified as 'unknown', has_pth_drill=false and has_npth_drill=false despite vias and press-fit holes
  (completeness)
- Alignment=false with 3.2mm height variance, but copper edge clearance ~1.6mm/side is normal design practice, not misalignment
  (alignment)

### Missed
(none)

### Suggestions
(none)

---
