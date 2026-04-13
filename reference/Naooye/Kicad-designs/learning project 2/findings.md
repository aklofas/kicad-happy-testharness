# Findings: Naooye/Kicad-designs / learning project 2

## FND-00000796: I2C bus detected on A4/A5 (SDA/SCL) connecting Arduino Nano to MAX30102 and SSD1306; Schematic/PCB reference mismatch not flagged: schematic uses SW1/SW2/SW3 but PCB uses UP/DOWN/MENU; 14 component...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: learning project 2.kicad_sch.json
- **Created**: 2026-03-23

### Correct
- bus_analysis.i2c correctly identifies the shared I2C bus connecting Arduino A4/A5 to both U2 (MAX30102) and U3 (SSD1306). RC filter detection on button debounce networks (R+C pairs for SW1/SW2/SW3) is also correct.
- Component count, types, BOM grouping, and power rails (+5V, GND) all correct. Missing MPN flagged for all 14 components as expected for a student project.

### Incorrect
(none)

### Missed
- The schematic has SW1, SW2, SW3, D1 but the PCB footprints use references UP, DOWN, MENU, ALARM. The analyzer does not cross-reference schematic refs against PCB refs to detect this naming inconsistency.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00000797: Courtyard overlaps correctly detected for densely packed resistors R2/R3 and R1/R3

- **Status**: new
- **Analyzer**: pcb
- **Source**: learning project 2.kicad_pcb.json
- **Created**: 2026-03-23

### Correct
- Three courtyard overlaps reported: R3/R2 (14.94mm²), R1/R3 (7.588mm²), R4/C3 (3.03mm²). These are genuine DFM issues — resistors are placed 2-3mm apart with 9.6mm long courtyard outlines. GND copper zone correctly identified as filled on both F.Cu and B.Cu.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
