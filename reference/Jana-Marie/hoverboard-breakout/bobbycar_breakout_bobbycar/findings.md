# Findings: hoverboard-breakout / bobbycar_breakout_bobbycar

## FND-00002130: I2C bus not detected despite SCL/SDA nets and pull-up resistors present; R2/R3 + C1/C2 detected as RC low-pass filters instead of I2C pull-up resistors with bypass caps

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: schematic_hoverboard-breakout_nunchuk_breakout_nunchuk_breakout.sch.json
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
- The analyzer identified two 4.82 MHz RC low-pass filters (R3+C2 on SCL, R2+C1 on SDA, each 3k3+10p). While the RC topology is geometrically valid, these components are I2C pull-up resistors (R top to VCC, line out to SCL/SDA) with small bypass capacitors to GND — a standard I2C bus filter. Classifying them as low-pass filters without contextual I2C role is misleading. The 'input_net' is VCC for both, which is characteristic of pull-up configurations, not signal filter inputs.
  (signal_analysis)

### Missed
- The schematic has SCL and SDA nets, a Wii Nunchuk connector (CONN_WII, P1) with pins named SCL and SDA, and two 3k3 pull-up resistors (R2, R3) connecting VCC to SDA/SCL respectively. Despite these clear I2C indicators, bus_analysis.i2c is empty. The nets are named 'SCL' and 'SDA' in the labels array. The analyzer correctly identified SCL as 'clock' and SDA as 'data' in net_classification, but the I2C bus assembly step did not fire.
  (design_analysis)

### Suggestions
(none)

---

## FND-00002131: UART bus correctly detected with TX/RX/TX.1/RX.1 nets and UART1 connector

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: schematic_hoverboard-breakout_bobbycar_breakout_bobbycar.kicad_sch.json
- **Created**: 2026-03-24

### Correct
- The bobbycar board routes two UART channels (TX/RX and TX.1/RX.1) to multiple connectors, and the analyzer correctly identified all four UART nets in bus_analysis.uart. The UART1 connector is correctly recognized as a UART interface device. The L7805 5V regulator (U1) was correctly identified as an LDO power regulator with VDD input and VCC output.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
