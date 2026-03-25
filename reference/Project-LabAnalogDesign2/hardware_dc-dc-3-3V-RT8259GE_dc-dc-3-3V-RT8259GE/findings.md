# Findings: Project-LabAnalogDesign2 / hardware_dc-dc-3-3V-RT8259GE_dc-dc-3-3V-RT8259GE

## FND-00001121: RC filter false positive: R1/C2/C5 are feedback divider + output caps, not an RC filter; Legacy .sch pin-name mismatch: U1 'BOOT' pin appears on 'FB' net; U1 'FB' pin on unnamed net; Power regulato...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: dc-dc-3-3V-RT8259GE.sch
- **Created**: 2026-03-23

### Correct
- 25 components correctly enumerated (U1, C1-C5, R1-R3, L1, J1-J2, JP1-JP2, TP1-TP5, H1-H4, D1, G1). Component types (ic, capacitor, resistor, inductor, connector, test_point, jumper, mounting_hole, diode) all correctly classified.

### Incorrect
- The RC filter detector found R1 (62kΩ, FB net) with C2/C5 (22µF) on __unnamed_5 (the output Vout node) and flagged a 0.06 Hz low-pass filter. But R1 is the feedback divider top resistor for the RT8259GE, and C2/C5 are output bypass capacitors. The 'input_net=FB, output_net=__unnamed_5' structure is the regulator output path, not an RC filter. This is the same category of feedback-divider false positive seen in other switching regulator designs.
  (signal_analysis)
- In the net map, the 'FB' named net includes U1 pin 1 (name='BOOT') alongside R1/R2 feedback resistors. Meanwhile __unnamed_1 has U1 pin 3 (name='FB') with C3. The RT8259GE pin 1 is BOOT (soft-start), not FB. The KiCad 5 legacy parser appears to be mapping the net label 'FB' from the schematic wire label to U1 pin 1 incorrectly — this is a net-connectivity parsing issue in the legacy .sch parser affecting pin-to-net assignment.
  (signal_analysis)
- The RT8259GE is a step-down (buck) switching regulator. The analyzer detected it as topology='unknown' with input_rail='__unnamed_3' (an unnamed net), despite R1/R2 forming a complete feedback voltage divider. The unnamed input rail is because the VIN net lacks a named power rail symbol. This is consistent with known KH issues around unnamed nets preventing regulator classification.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001122: PCB stats, routing completeness, and DFM correctly reported for small 2-layer buck converter board

- **Status**: new
- **Analyzer**: pcb
- **Source**: dc-dc-3-3V-RT8259GE.kicad_pcb
- **Created**: 2026-03-23

### Correct
- 2-layer board, 40x38mm, 27 footprints, 8 nets, fully routed (0 unrouted). DFM: 0 violations, minimum track 0.381mm, minimum drill 0.7mm. GND zone stitching with 1 via correctly detected. 2 courtyard overlaps reported — these are for the OSHW logo (G1) and KiCad logo (REF**) board-only decorative footprints overlapping with real components, which is acceptable.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
