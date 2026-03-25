# Findings: hat-design / hat-design

## FND-00002119: I2C bus correctly detected with AT24CS32 EEPROM and pull-up resistors; I2C line names swapped relative to Pi HAT specification naming convention

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: schematic_hat-design_hat-design.sch.json.json
- **Created**: 2026-03-24

### Correct
- The analyzer identified the I2C bus on ID_SD/ID_SC nets, found both 3.9K pull-up resistors (R9 on ID_SD, R10 on ID_SC) tied to +3.3V, and correctly associated IC1 (AT24CS32 EEPROM). The design is a Raspberry Pi HAT with an ID EEPROM, and the bus detection is accurate. The analyzer uses IC pin names (SDA/SCL) to classify lines rather than net names, which is the correct approach.

### Incorrect
(none)

### Missed
- The Raspberry Pi HAT specification defines ID_SD as SDA (data) and ID_SC as SCL (clock). However, the schematic routes ID_SD to IC1 pin 6 (SCL) and ID_SC to IC1 pin 5 (SDA). The analyzer correctly reports the IC pin names seen on each net (ID_SD -> SCL, ID_SC -> SDA), but does not emit any warning about this mismatch between the HAT connector signal names and the EEPROM pin assignments. An ERC warning about the potential design issue (net named ID_SD connected to an SCL pin) would be useful.
  (signal_analysis)

### Suggestions
(none)

---
