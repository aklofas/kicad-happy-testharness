# Findings: HadesFCS / Hardware_HadesNT_HadesNT

## FND-00000082: HadesNT flight controller - 102 components, zero signals due to KH-016; rich component set suggests many missed detections

- **Status**: promoted
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
