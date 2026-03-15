# Findings: slab-pcb / interchange-pcb-right_interchange-pcb-right

## FND-00000184: Keyboard/macro pad with RP2040, PCA9555 I/O expanders, TCA4307 I2C buffer, ADS1110 ADC, SK6812 LEDs (139 components). Correct: I2C buses with pullups, PCA9555 address pins, level shifter topology, component counts. Incorrect: I2C1_RDY (status output) falsely listed as I2C SCL line. Missed: level-shifting topology, TCA4307 I2C buffer topology, hierarchical sheet pin net resolution.

- **Status**: confirmed
- **Analyzer**: schematic
- **Source**: interchange-pcb-right_interchange-pcb-right.kicad_sch.json
- **Created**: 2026-03-15

### Correct
- Six I2C bus segments correctly detected with pullup resistors
- 139 components with correct type breakdown
- U5 SN74AHCT125 channel usage correctly analyzed

### Incorrect
- I2C1_RDY (TCA4307 status output) incorrectly listed as I2C SCL line
  (design_analysis.bus_analysis.i2c)

### Missed
- Level-shifting topology (3.3V RP2040 through 5V AHCT buffer to WS2812) not detected
  (signal_analysis)
- TCA4307 I2C buffer/isolator topology not detected
  (subcircuits)

### Suggestions
- Exclude non-I2C nets (RDY/READY) from I2C detection
- Add I2C buffer/isolator topology detection

---
