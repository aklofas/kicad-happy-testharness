# Findings: scottbez1/splitflap / electronics_chainlinkBase

## FND-00000079: Legacy KiCad 5 schematic for the chainlink base/controller board. 64 components, 116 nets extracted correctly. 0 signals detected due to KH-016. Design includes ESP32 (TTGO T-Display), RS-485 transceiver (SP485), level translators (SN74LV1T34DBV), I2C GPIO expander (MCP23017), current sensor (INA219), motor driver (VN7007ALH), and voltage regulators.

- **Status**: confirmed
- **Analyzer**: schematic
- **Source**: repos/splitflap/electronics/chainlinkBase/chainlinkBase.sch
- **Related**: KH-016
- **Created**: 2026-03-14

### Correct
- All 64 components extracted with correct references and values
- Component types correct: 10 ICs including ESP32 module, RS-485, level translators, I2C expander, current sensor, motor driver, voltage regulators
- Power rails +12V, +3.3V, +5V, GND correctly identified
- 16 capacitors, 10 resistors, 8 LEDs, 11 connectors correctly classified
- BOM has 32 unique parts with correct grouping (2x SN74LV1T34DBV grouped)
- 10 subcircuits identified around ICs

### Incorrect
- SP485 uses lib_id Interface_UART:MAX485E - value/lib mismatch (SP485 vs MAX485E). These are pin-compatible but different parts. Analyzer reports what is in schematic correctly but could flag this
  (components)
- TPL7407L uses lib_id Transistor_Array:ULN2003A - same value/lib mismatch as chainlinkDriver
  (components)

### Missed
- No signal analysis detected (0 signals) - RS-485 bus, I2C bus (MCP23017, INA219), SPI-like shift register interface, voltage regulators (AP7361C-33E, buck converter), level translation circuits, and motor driver should all be detectable
  (signal_analysis)
- RS-485 interface (SP485) not detected as a bus protocol
  (design_analysis.bus_analysis)

### Suggestions
- Resolving KH-016 would enable detection of RS-485, I2C, voltage regulators, and level translation
- RS-485 transceiver detection would be valuable for industrial/motor-control designs

---
