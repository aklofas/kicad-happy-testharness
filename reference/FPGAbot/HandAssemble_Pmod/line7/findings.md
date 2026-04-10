# Findings: FPGAbot/HandAssemble_Pmod / line7_line7

## FND-00002547: Hand-assembled 7-channel phototransistor line sensor Pmod board with TEPT5600 photo-NPN transistors, LED indicators driven by 2N3904 BJT, and RC filtering on sensor outputs. Analyzer correctly identifies the core signal conditioning topology.

- **Status**: confirmed
- **Analyzer**: schematic
- **Source**: line7_line7.kicad_sch.json

### Correct
- 7 phototransistors (Q1-Q7, TEPT5600) correctly classified as BJT type with base_net=null (photo-sensitive, no base drive), collector_is_power=false, emitter_is_ground=true
- Q8 (2N3904) correctly detected as LED driver BJT with emitter to GND, base resistor R8 (1K), and load_type=led
- Seven RC-network filters (R1/C1, R2/C2, R3/C3, R4/C4, R5/C5, R6/C6, R7/C7, all 330ohm/2.2nF) correctly detected at 219.22 kHz cutoff, forming sensor output conditioning on each channel
- VCC rail decoupling with C8 (1.0uF) correctly identified
- 42 total components correctly counted: 16 resistors, 8 capacitors, 8 LEDs, 8 transistors, 2 connectors
- 8 LEDs (D1-D8) correctly classified as type led, 8 current-limiting resistors (R9-R16, 100 ohm) correctly classified
- J1 (Pmod-8 connector) and J2 (Conn_01x02 power) correctly classified as connectors

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
