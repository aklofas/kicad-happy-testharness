# Findings: cnlohr/cnhardware / ch32v30x_ch32v305-currentmonitor

## FND-00000161: Current monitoring board with AK5534 ADC and CH32V305. Current sense resistors R1=0.1ohm, R2=1ohm not detected on a board literally named 'currentmonitor'. I2S bus not detected; SCL/SDA falsely detected as I2C.

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: ch32v30x_ch32v305-currentmonitor_ch32v305-currentmonitor.kicad_sch.json
- **Related**: KH-086
- **Created**: 2026-03-15

### Correct
- All 13 MOSFETs correctly mapped as transistor circuits

### Incorrect
- SCL/SDA nets from AK5534 clock-select pins falsely detected as I2C -- these are actually clock-select pins named SCL/SDA by the designer, not I2C
  (signal_analysis.design_observations)

### Missed
- R1 (0.1 ohm), R2 (1 ohm) current sense resistors not detected on a board named 'currentmonitor'
  (signal_analysis.current_sense)

### Suggestions
- Low-value resistors (<1 ohm) should be detected as current sense candidates
- Add I2S bus detection (I2SCK/BCLK, I2SWS/LRCK, I2SD/SDIN/SDOUT patterns)

---
