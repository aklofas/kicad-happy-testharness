# Findings: tkadams1/ArduinoShieldMCP4151 / KiCadCircuit_ArduinoDigitalPotShield

## FND-00000366: SPI bus to MCP4151 not detected; Resistor 5kohms1 classified as 'other' instead of 'resistor'

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: KiCadCircuit_ArduinoDigitalPotShield.kicad_sch.json
- **Created**: 2026-03-23

### Correct
(none)

### Incorrect
- Component 5kohms1 uses lib_id 'Device:R', value 'R', and keywords 'R res resistor' — it is a standard KiCad resistor. However, its type is reported as 'other' because the reference designator does not start with 'R'. This causes component_types.resistor to be reported as 2 instead of the correct 3, and the BOM entry for 5kohms1 has type 'other'. The classifier should use lib_id or keywords to identify resistors, not just the reference prefix.
  (statistics)

### Missed
- The MCP4151 digital potentiometer is connected to the Arduino shield via SPI: U2 pin 1 (~CS) → XA1.D10_CS, U2 pin 2 (SCK) → XA1.D13, U2 pin 3 (SDI/SDO) → XA1.D11. The bus_analysis.spi array is empty and no SPI detection appears anywhere in the output. The analyzer should detect at least one SPI bus involving U2 (MCP4151) with the Arduino shield XA1 as the controller.
  (design_analysis)

### Suggestions
(none)

---
