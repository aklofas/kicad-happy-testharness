# Findings: ISS-PCB / boards_TARS-MK4_TARS-MK4-FCB-revC_TARS-MK4-FCB

## FND-00000154: Flight computer with Teensy 4.1 and 7 motion/environmental sensors. SPI nets falsely detected as I2C buses due to pin-name fallback not excluding SPI nets.

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: boards_TARS-MK4_TARS-MK4-FCB-revC_TARS-MK4-FCB.kicad_sch.json
- **Related**: KH-086
- **Created**: 2026-03-15

### Correct
- Crystal Y101 32.768kHz with load caps correctly detected
- SPI bus detection correctly groups SPI signals

### Incorrect
- SPI nets SNS_SPI_SCK, SNS_SPI_MOSI, SNS_SPI_MISO falsely detected as I2C SCL/SDA -- pin-name fallback doesn't exclude nets already identified as SPI
  (signal_analysis.design_observations)
- BME688_CS net reported as I2C SDA because Teensy pin 39 has multi-function name '17_A3_TX4_SDA1'
  (signal_analysis.design_observations)

### Missed
- INA745x current/power monitors (U101, U201) not detected -- current_sense array empty despite dedicated current sensing ICs
  (signal_analysis.current_sense)

### Suggestions
- Pin-name I2C fallback should exclude nets already in SPI results or containing SPI keywords
- Add INA7xx to current sensing IC detection

---
