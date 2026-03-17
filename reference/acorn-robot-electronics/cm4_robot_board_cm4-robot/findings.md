# Findings: acorn-robot-electronics / cm4_robot_board_cm4-robot

## FND-00000272: CM4 robot board (246 components). TPS61040 boost output_rail wrong (+5V instead of +12V). 7 SPDT config switches falsely detected as keyboard matrix. Ethernet interface, CAN isolation barriers, SPI and I2C buses missed.

- **Status**: confirmed
- **Analyzer**: schematic
- **Source**: cm4_robot_board_cm4-robot.kicad_sch.json
- **Created**: 2026-03-16

### Correct
- LDO TLV1117LV33 and buck LM2576HVS-5 correctly identified
- 10 MOSFET circuits correctly identified with gate drivers
- 8 protection devices (CDSOT23-SM712 TVS, polyfuses, USBLC6, TPD4E1U06) correctly detected
- VMOT battery voltage sensing divider correctly identified with ADS1115 load
- WS2812B LED chain of 7 LEDs correctly detected
- 4 crystal circuits with load cap calculations correct

### Incorrect
- TPS61040DBVR (U12) output_rail='+5V' but actual boost output is +12V — Schottky D11 cathode connects to +12V rail
  (signal_analysis.power_regulators)
- False key_matrix — 7 independent SPDT config switches (SW2-SW7) with per-switch diodes resemble matrix topology; row nets are CAN/enable signals, not keyboard rows
  (signal_analysis.key_matrices)

### Missed
- Ethernet interface not detected — CM4 pairs through TPD4E1U06 ESD to G2401CG transformer to RJ45
  (signal_analysis.ethernet_interfaces)
- ISO1050DUB isolated CAN transceivers (U10/U11) not detected as isolation barriers — separate VCC1/VCC2 power domains
  (signal_analysis.isolation_barriers)
- SPI bus not detected — MCP2515 x2 + SC16IS752 x2 sharing SERIAL_CLK/COPI/CIPO
  (design_analysis.bus_analysis.spi)
- I2C bus not detected — SCL6/SDA6 with ADS1115, LIS3MDL, PCA9536, LSM6DS3
  (design_analysis.bus_analysis.i2c)

### Suggestions
- Boost converter output_rail: trace inductor SW → Schottky cathode to find actual output net
- Key matrix: reject row/col nets that are protocol signals (CAN, EN, nRESET)
- Add Ethernet transformer detection via known part patterns
- Detect ISO1050/ISO1042 as isolation barriers by part value/lib_id

---
