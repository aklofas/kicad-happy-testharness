# Findings: InverseInductor/C-Beeper / C-Beeper

## FND-00000417: LS1 (Device:Speaker_Crystal) classified as 'crystal' instead of speaker/transducer; buzzer_speaker_circuits detector returned empty despite a speaker (LS1) being present; transistor_circuits detect...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: C-Beeper.sch.json
- **Created**: 2026-03-23

### Correct
(none)

### Incorrect
- LS1 uses lib_id 'Device:Speaker_Crystal' and footprint 'PinHeader_1x02' — it is a piezoelectric speaker driven by the oscillator circuit. The analyzer assigns type='crystal' and counts it under component_types.crystal=1. It should be typed as a speaker or transducer. As a consequence, buzzer_speaker_circuits is empty and crystal_circuits is also empty, even though a speaker is present.
  (statistics)
- The GND net lists only 3 pins: R3/pin1, R5/pin1, C2/pin1. However there are 9 GND power symbols in the schematic, and components Q1, Q2, Q3, D1, LS1, BT1, and J1 all have 'pins': [] (empty) so their GND/VCC connections are not resolved into nets. The GND net point_count=9 suggests the wire tracing found the junctions, but the pin membership is incomplete.
  (nets)

### Missed
- LS1 is a Device:Speaker_Crystal (piezo speaker) driven by a BJT oscillator. The buzzer_speaker_circuits array is empty. The circuit has all the hallmarks of a buzzer circuit: BJT driver transistors (Q1 BC859 PNP, Q2 BC849 NPN, Q3 BC859 PNP), biasing resistors, and LS1 as the load. This is a false negative in the speaker/buzzer detector.
  (signal_analysis)
- The design contains Q1 (BC859, PNP SOT-23), Q2 (BC849, NPN SOT-23), and Q3 (BC859, PNP SOT-23) forming a relaxation oscillator that drives the piezo speaker LS1. The signal_analysis.transistor_circuits array is empty — no BJT switch, amplifier, or oscillator circuits were detected.
  (signal_analysis)
- Only one voltage divider is reported (R2=2.2M top, R3=5.6M bottom). R4 (2.2M) and R5 (1.5M) form a second voltage divider from VCC through R4, then R5 to GND, with the midpoint connected to Q1's base network. This second divider is missed; voltage_dividers has only 1 entry.
  (signal_analysis)
- R8 (270Ω) is a current-limiting resistor in series with D2 (LED). This is a textbook LED driver. The design has no dedicated LED driver detector output and no mention of this subcircuit in signal_analysis. The net __unnamed_7 correctly connects R8 pin 1 to D2 cathode (K), but no LED driver detection fired.
  (signal_analysis)

### Suggestions
- Fix: LS1 (Device:Speaker_Crystal) classified as 'crystal' instead of speaker/transducer

---
