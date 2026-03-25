# Findings: RUST_Hardware / Motherboard_RUST_Motherboard

## ?: ATmega1280+ATmega16U2 motherboard: good component/crystal/regulator detection, but OLED SPI clock misclassified as I2C SCL, MCP1661 boost converter output rail wrong (+3V8 vs +12V), ceramic resonators correctly flagged as no load caps

- **Status**: new
- **Analyzer**: schematic
- **Source**: Motherboard_RUST_Motherboard.kicad_sch.json
- **Created**: 2026-03-23

### Correct
- 271 components correctly counted
- Crystal/resonator circuits Y1 and Y2 (16MHz AWSCR ceramic resonators) detected
- Ceramic resonators correctly noted as having no external load caps (built-in)
- Power regulators detected including LDOs
- SPI buses correctly detected

### Incorrect
- OLED_SCL_3V3 net classified as I2C SCL but it is actually SPI clock for OLED display - 'SCL' substring triggered false I2C classification
  (design_analysis.bus_analysis.i2c)
- MCP1661 (U7) boost converter output_rail listed as +3V8 (which is the input rail VIN). Actual output is +12V via SW->L2->D23 boost topology
  (signal_analysis.power_regulators)

### Missed
- Boost converter topology (U7 MCP1661: +3V8->SW->L2->D23->+12V) not fully traced through inductor-diode chain
  (signal_analysis.power_regulators)

### Suggestions
- SPI clock nets (SCK, SCLK, SCL in SPI context) should not be classified as I2C when other SPI signals (MOSI, MISO, CS) are on the same IC
- Boost converter output rail detection should trace through the SW->inductor->diode chain to find the actual output rail, not just use VIN/VOUT pin names

---
