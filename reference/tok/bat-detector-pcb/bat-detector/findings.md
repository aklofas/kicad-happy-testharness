# Findings: tok/bat-detector-pcb / bat-detector

## FND-00001963: MK1 (Microphone_Ultrasound) classified as 'fiducial' instead of 'microphone'; opamp_circuits is empty despite two TL072 op-amp units (U2) being present; RC filters correctly detected with 7 entries...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: bat-detector.sch.json
- **Created**: 2026-03-24

### Correct
- Seven RC filters are detected covering frequencies from 102 Hz (R10/C4) to 116 kHz (R1/C1). These correspond to the NE555 timing network, microphone pre-amp filter caps, and the heterodyne mixing stage filters — all appropriate for a bat detector operating in the 40–100 kHz range. Filter types (low-pass and RC-network) and cutoff frequencies appear correct based on component values from the schematic.
- Both BC548 NPN transistors are detected with correct topologies. Q1 collector is at GND net (common-emitter with inverted orientation), emitter connects to signal node. Q2 base is driven by the square_wave_1 net from the NE555, consistent with a switching/mixing transistor. Two transistor circuits reported matching two physical transistors.
- LS1 (value='Speaker') is detected in buzzer_speaker_circuits with type='speaker'. The has_transistor_driver=false is reasonable since the speaker is driven by LM386 (U3) audio amplifier output, not a discrete transistor.
- design_observations correctly flags U1 (NE555), U2 (TL072), and U3 (LM386) as having VCC without nearby decoupling capacitors. The schematic indeed has no bypass caps on the VCC rails for these ICs, which is a real design concern for this ultrasound frequency design.
- total_components=26, total_nets=26, total_no_connects=11 with 7 capacitors, 12 resistors, 3 ICs, 2 transistors, 1 speaker all correctly extracted from the KiCad 5 legacy .sch format. The dual-unit TL072 is correctly de-duplicated into one BOM entry.

### Incorrect
- MK1 uses lib_id 'Device:Microphone_Ultrasound' which is clearly a microphone, but the component type classification in both bom and components list shows type='fiducial'. The word 'Microphone' appears in the lib_id and value field. The microphone is the sensor input for this bat detector design. This misclassification also causes the component_types dictionary to show 'fiducial: 1' instead of a microphone category, and means the statistics miss the sensor.
  (statistics)

### Missed
- U2 is a TL072 dual op-amp (lib_id Amplifier_Operational:TL072) with two active amplifier units (unit 1 and unit 2, each having +/- inputs and output pin). The signal_analysis.opamp_circuits list is empty. The TL072 units form amplifier stages in the heterodyne bat detector circuit. The analyzer should detect these as op-amp configurations. LM386 (U3, lib_id Amplifier_Audio:LM386) is also not detected in opamp_circuits, though it is an audio amplifier.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00001964: Empty/stub KiCad v4 PCB file correctly produces zeroed output

- **Status**: new
- **Analyzer**: pcb
- **Source**: bat-detector.kicad_pcb.json
- **Created**: 2026-03-24

### Correct
- The bat-detector.kicad_pcb file contains only '(kicad_pcb (version 4) (host kicad "dummy file"))' — a placeholder stub, not a real PCB layout. The analyzer correctly outputs all-zero statistics (footprint_count=0, track_segments=0, etc.) with file_version='4'. This is the appropriate behavior for an unpopulated stub PCB.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
