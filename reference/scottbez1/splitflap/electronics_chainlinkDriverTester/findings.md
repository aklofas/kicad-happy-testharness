# Findings: scottbez1/splitflap / electronics_chainlinkDriverTester

## FND-00000076: Legacy KiCad 5 schematic with 141 components. Components, nets, and BOM extracted correctly. 0 signals detected due to KH-016 (legacy wire-to-pin connectivity limitation). Design has voltage regulators (AP7361C-33E, LM7805, buck converter), I2C devices (MCP23017, INA219), motor driver (VN7007ALH), ESP32 module, and shift registers which should yield multiple signal detections once KH-016 is resolved.

- **Status**: confirmed
- **Analyzer**: schematic
- **Source**: repos/splitflap/electronics/chainlinkDriverTester/chainlinkDriverTester.sch
- **Related**: KH-016
- **Created**: 2026-03-14

### Correct
- All 141 components extracted with correct references, values, and lib_ids
- Component type classification correct: 7 ICs, 22 connectors, 13 resistors, 8 capacitors, 65 test points, LEDs, fuse, buzzer, switch
- Power rails correctly identified: +12V, +3.3V, +3V3, +5V, GND
- 179 nets extracted with 80 named nets and proper pin associations
- BOM has 44 unique parts with correct footprint assignments
- 7 subcircuits identified around ICs with neighbor components

### Incorrect
(none)

### Missed
- No signal analysis detected (0 signals) - voltage regulators (AP7361C-33E 3.3V LDO, LM7805 5V, buck converter), I2C bus (MCP23017 + INA219), motor driver circuit (VN7007ALH), and buzzer circuit should all be detectable
  (signal_analysis)
- +3.3V and +3V3 are likely the same rail but listed separately - could note this as a design observation
  (design_analysis)

### Suggestions
- Resolving KH-016 would enable signal detection for this component-rich design
- Could flag +3.3V vs +3V3 duplicate rail naming as a design observation

---
