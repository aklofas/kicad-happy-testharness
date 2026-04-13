# Findings: azonenberg/starshipraider / boards_MAXWELL_maxwell-main

## FND-00002521: 18-sheet FPGA test instrument (MAXWELL) with dual Xilinx FPGAs, DDR3 SODIMM, QSFP+, LMK04806B clocking, 24 INA233 power monitors. Major issues: STM32F777 falsely classified as switching regulator, 14 power conversion ICs missed entirely, INA233 monitors misclassified as opamps, power rails classified as signals.

- **Status**: confirmed
- **Analyzer**: schematic
- **Source**: boards_MAXWELL_maxwell-main_maxwell-main.sch.json
- **Created**: 2026-04-09

### Correct
- All 18 sheets correctly parsed, 993 components
- Y1 crystal and U47 oscillator correctly identified
- LMK04806B correctly detected as clock_generator
- 160 differential pairs including Ethernet, DDR3, QSFP, GTX SERDES
- 3 I2C buses with INA233 device lists correct
- Q1-Q4 power sequencing MOSFETs correctly identified

### Incorrect
- U1 STM32F777 falsely classified as switching regulator — MCU, not a PSU
  (signal_analysis.power_regulators)
- All 24 opamp_circuits are INA233 power monitors misclassified as comparator_or_open_loop
  (signal_analysis.opamp_circuits)
- LEDs D26-D28 falsely flagged as no current limiter — R222-R224 (1K) exist
  (signal_analysis.led_audit)
- PHY strap resistors (R38-R40 + R45-R47) falsely detected as voltage dividers
  (signal_analysis.voltage_dividers)
- Power rails 12V0, 3V3, 5V0, 1V5, 1V8, 1V2 all classified as 'signal'
  (design_analysis.net_classification)
- 75 false UART bus detections including power nets and SERDES pairs
  (design_analysis.bus_analysis.uart)

### Missed
- 14 power conversion ICs missed: DC-DC brick, 3x POL, 6x POL modules, 2x sync buck, 1x LDO
  (signal_analysis.power_regulators)
- DDR3 SODIMM not detected in memory_interfaces
  (signal_analysis.memory_interfaces)
- 3 SPI buses (FPGA config, PLL programming) not detected
  (design_analysis.bus_analysis.spi)
- ADCMP582/LMH7322 high-speed comparators not detected
  (signal_analysis.opamp_circuits)

### Suggestions
- Use lib_id as strong signal for power IC identification
- Classify INA233/INA226 as current_sense/power_monitor, not opamp
- Recognize voltage-named nets (12V0, 3V3, 5V0) as power rails
- Filter UART false positives: require actual UART IC connections

---
