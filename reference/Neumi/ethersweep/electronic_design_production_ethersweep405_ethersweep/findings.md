# Findings: Neumi/ethersweep / electronic_design_production_ethersweep405_ethersweep

## FND-00000150: Stepper motor controller with W5500 Ethernet, TMC2209 driver, AS5600 encoder. Ethernet PHY, motor driver, I2C bus correctly detected. Major gaps in crystal load caps, decoupling, SPI bus, and current sense false positives.

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: electronic_design_production_ethersweep405_ethersweep.kicad_sch.json
- **Related**: KH-079, KH-080, KH-081
- **Created**: 2026-03-15

### Correct
- W5500 (U1) correctly identified as Ethernet PHY with RJ45 connector J10 HR911105A
- TMC2209-LA (U7) correctly identified as motor driver with 29 pins mapped
- I2C bus between STM32 (U3) and AS5600 (U5) with pull-ups R24, R27
- SPI signals CS/SCK/MISO/MOSI correctly classified as chip_select/clock/data
- Power rails +28V, +3.3V, +3.3VA, DD4012SA enumerated

### Incorrect
- R4, R5 (33 ohm) falsely detected as current sense shunts -- these are Ethernet differential pair series termination resistors between W5500 TX/RX and HR911105A RJ45
  (signal_analysis.current_sense)
- DD4012SA (U4, Diodes Inc buck converter) classified as power_symbol because lib_id is 'power:DD4012SA' with in_bom=yes -- excluded from components, ic_pin_analysis, and power_regulators entirely
  (signal_analysis.power_regulators)
- All 109 components have empty string classification field
  (components)

### Missed
- +28V motor power rail missing from power_budget despite 11 power symbol instances feeding TMC2209 via DD4012SA
  (signal_analysis.power_budget)

### Suggestions
- Check in_bom flag before classifying components as power symbols -- DD4012SA has in_bom=yes
- Add minimum resistance threshold for current_sense detection to avoid Ethernet termination resistors
- Crystal load cap detection should use connectivity data already in ic_pin_analysis

---
