# Findings: Duplicanator-Scart-Duplicator / KiCAD_scart_duplicator_scart_duplicator

## FND-00000185: SCART video duplicator with THS7374 4-channel video amp (41 components). Correct: THS7374 pin mapping, SCART connectors pin assignments, audio passthrough, D1 switching voltage protection, USB-C power. Incorrect: CSYNC nets classified as chip_select, RC filter false positives on video termination/bias networks (75-ohm termination and 5.36M DC bias). Missed: video amplifier/buffer topology, 1-to-2 signal splitter pattern.

- **Status**: confirmed
- **Analyzer**: schematic
- **Source**: KiCAD_scart_duplicator_scart_duplicator.kicad_sch.json
- **Created**: 2026-03-15

### Correct
- U1 THS7374 all 14 pins correctly mapped
- SCART J1 input and J3/J4 output pin assignments correct
- Audio passthrough correctly traced

### Incorrect
- CSYNC_IN/OUT1/OUT2 classified as chip_select (is composite sync)
  (design_analysis.net_classification)
- R5-R8 5.36M DC bias networks detected as filters
  (signal_analysis.rc_filters)
- R1-R4 75-ohm video termination detected as high-pass filters
  (signal_analysis.rc_filters)

### Missed
- Video amplifier/buffer topology not recognized
  (signal_analysis)
- 1-to-2 SCART signal splitter pattern not detected
  (subcircuits)

### Suggestions
- Avoid matching CS substring in CSYNC/HSYNC/VSYNC names
- Recognize 75-ohm resistor to ground at video amplifier input as termination

---
