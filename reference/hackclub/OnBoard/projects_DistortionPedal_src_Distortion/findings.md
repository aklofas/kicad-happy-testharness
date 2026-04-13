# Findings: hackclub/OnBoard / projects_DistortionPedal_src_Distortion

## FND-00000092: Guitar distortion pedal with NJM4558 dual opamp, 3 BJT stages, and extensive RC filtering. Good signal analysis overall but missed bias voltage divider and potentiometers classified as other.

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: repos/OnBoard/projects/DistortionPedal/src/Distortion.kicad_sch
- **Created**: 2026-03-14

### Correct
- NJM4558 dual opamp correctly identified with unit 1 as buffer and unit 2 as transimpedance/feedback config
- 3 BJT transistor stages (Q1/Q2/Q3, 2SC2240) correctly detected with base biasing and emitter resistors
- 19 RC filters detected, appropriate for an analog audio effects circuit with extensive filtering
- 4 diodes (1N4148 clipping + 1N4004 protection) correctly classified
- 6 test points correctly identified from Connector:TestPoint symbols
- Power rails +9V, +4.5V, GND correctly detected

### Incorrect
- Potentiometers VR1/VR2/VR3 (Device:R_Potentiometer_US) classified as type other instead of potentiometer
  (statistics.component_types)

### Missed
- Bias voltage divider R24 (10K from +9V) / R25 (10K to GND) creating +4.5V mid-rail bias not detected as voltage_divider. C15 (47uF) and C12 (0.1uF) bypass this node.
  (signal_analysis.voltage_dividers)

### Suggestions
- R_Potentiometer_US should map to a potentiometer component type rather than other
- Voltage divider detector should find R24/R25 creating the +4.5V bias rail from +9V

---
