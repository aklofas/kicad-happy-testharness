# Findings: ESP32-SBC-FabGL / HARDWARE_Hardware-revision-A_ESP32-SBC-FabGL_Rev_A

## FND-00000182: OLIMEX ESP32-SBC-FabGL (118 components). Correct: 118 components, CH340X USB-UART, transistors, fiducials, RC/LC filters, ESD protection, USB pair. Incorrect: VGA1 DB-15 connector as varistor, AUDIO1 audio jack as IC, U5 SY8089 input_rail=GND, U7 MT3608 fb_net=GND. Missed: battery sensing voltage divider R17/R18, R-2R VGA DAC, PS/2 interfaces, SPI bus.

- **Status**: confirmed
- **Analyzer**: schematic
- **Source**: HARDWARE_Hardware-revision-A_ESP32-SBC-FabGL_Rev_A.sch.json
- **Related**: KH-087
- **Created**: 2026-03-15

### Correct
- 118 components correctly extracted
- ESP32-WROVER-IE correctly identified
- USBLC6-2P6 ESD protection detected

### Incorrect
(none)

### Missed
- Voltage divider R17(470k)/R18(150k) for battery sensing not detected
  (signal_analysis.voltage_dividers)

### Suggestions
- Recognize VGA/audio connectors by footprint library
- Fix switching regulator input_rail/fb_net detection (KH-087)

---
