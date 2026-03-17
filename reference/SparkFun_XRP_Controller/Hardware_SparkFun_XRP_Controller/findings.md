# Findings: SparkFun_XRP_Controller / Hardware_SparkFun_XRP_Controller

## FND-00000168: SparkFun XRP robot controller with RP2350B. AP63357 reference voltage wrong, bus widths inflated, QSPI interface missed.

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: Hardware_SparkFun_XRP_Controller.kicad_sch.json
- **Created**: 2026-03-15

### Correct
- RP2350B microcontroller correctly identified with proper pin count
- DRV8411A dual motor drivers correctly identified

### Incorrect
- AP63357 buck converter Vref reported as 0.6V but datasheet specifies 0.765V reference
  (signal_analysis.power_regulators)

### Missed
- QSPI flash memory interface to W25Q128 not detected as memory bus
  (signal_analysis.bus_interfaces)

### Suggestions
- Use correct Vref of 0.765V for AP63357 (check datasheet feedback divider reference)
- Count unique data signals in bus, not total net segments, to avoid inflated bus widths
- Detect QSPI memory interfaces from CS/CLK/D0-D3 net patterns to flash ICs

---

## FND-00000174: SparkFun XRP Controller (RP2350B robotics board). Correct: 184 components, DRV8411A motor drivers, LSM6DSOX IMU, crystal, USB compliance, WS2812B, power OR-ing. Incorrect: AP63357 Vref wrong (0.6V vs 0.765V giving 3.87V vs actual 5V), bus widths inflated by counting label instances across sheets. Missed: QSPI memory interface, SPI to radio module, I2C bus to IMU.

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: Hardware_SparkFun_XRP_Controller.kicad_sch.json
- **Created**: 2026-03-15

### Correct
- U1 RP2350B correctly identified with 81 pins
- U7/U8 DRV8411A motor drivers correctly identified
- Crystal Y1 12MHz with 15pF load caps correctly detected
- USB-C compliance with 5.1k CC pulldowns pass
- D4 WS2812B addressable LED chain detected

### Incorrect
- AP63357 output voltage calculated as 3.873V using wrong Vref=0.6V (correct Vref=0.765V gives 4.94V matching 5V rail)
  (signal_analysis.design_observations)
- Bus signal widths inflated: QSPI_D width=12 (actual 4), IMU_INT width=4 (actual 2)
  (bus_topology.detected_bus_signals)

### Missed
- QSPI memory interface between RP2350B and W25Q128/APS6404L not detected
  (signal_analysis.memory_interfaces)
- SPI interface to RM2 radio module not detected
  (design_analysis.bus_analysis.spi)

### Suggestions
- Add AP63357 Vref=0.765V to lookup table
- Fix bus width to count unique signal names not label instances
- Add QSPI bus detection

---
