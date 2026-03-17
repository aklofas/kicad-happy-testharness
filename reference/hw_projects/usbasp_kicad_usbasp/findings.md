# Findings: hw_projects / usbasp_kicad_usbasp

## FND-00000189: USBasp programmer (35 components). Correct: crystal 12MHz, BS170F MOSFET level shifters, ATmega8A, USB-C CC check (correctly fails for 1.5k). Incorrect: gate_resistors lists all VCC pullups for each transistor. Missed: SPI/ISP bus, D4/D5 3V6 Zener USB clamps not in protection devices.

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: usbasp_kicad_usbasp.kicad_sch.json
- **Related**: KH-082
- **Created**: 2026-03-15

### Correct
- Crystal Y1 12MHz with 22pF load caps detected
- Q1-Q4 BS170F MOSFET level shifters detected

### Incorrect
- Each transistor lists all 4 VCC pullup resistors as gate_resistors
  (signal_analysis.transistor_circuits)

### Missed
- SPI/ISP bus not detected (hierarchical labels obscure SPI function)
  (design_analysis.bus_analysis.spi)
- D4/D5 3V6 Zener USB clamps not detected as protection
  (signal_analysis.protection_devices)

### Suggestions
- Skip gate_resistors when gate is on power rail
- Detect SPI from ISP connector pin names
- Detect Zener clamps with anode on GND as protection

---
