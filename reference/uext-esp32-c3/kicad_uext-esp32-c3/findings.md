# Findings: uext-esp32-c3 / kicad_uext-esp32-c3

## FND-00000145: Clean UEXT ESP32-C3 board (16 components) with AP2210 LDO and NUP4202 USB ESD. Best analysis quality among UEXT boards. LDO, USB ESD, decoupling, UART all correctly detected. Reset RC filter properly identified. Minor false positive on SPI bus from UEXT connector pins.

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: repos/uext-esp32-c3/kicad/uext-esp32-c3.kicad_sch
- **Created**: 2026-03-14

### Correct
- AP2210-3.3 LDO correctly identified with +5V input and +3V3 output
- NUP4202 USB ESD protection correctly detected on both USB_D+ and USB_D-
- RC filter on reset pin (R2 10k + C3 1uF, fc=15.92Hz) correctly detected
- Decoupling analysis shows +3V3 has 3 caps/12.3uF (bulk+bypass), +5V has 1 cap/2.2uF
- UART TX/RX (UEXT_TX/UEXT_RX) correctly detected with ESP32-C3
- Power domains correctly map all 3 ICs (U3 ESP32-C3 on +3V3, U1 AP2210 on +3V3/+5V, U2 NUP4202 on +5V)
- ERC warning for reset net is valid - driven by passive RC only

### Incorrect
- False positive SPI bus detected from UEXT connector pin names (MISO/MOSI/SCK) - these are connector pins, not an active SPI bus on this board
  (design_analysis.bus_analysis.spi)
- I2C bus detected on unnamed nets with no devices - unconnected UEXT I2C pins
  (design_analysis.bus_analysis.i2c)
- Subcircuit neighbors are identical for all 3 ICs - listing all 5 caps for each IC regardless of actual connectivity
  (subcircuits)

### Missed
- USB Micro-B connector (J1) present but USB data path to ESP32-C3 native USB not fully analyzed
  (signal_analysis.design_observations)
- LED1 with R1 (1k) current limiting resistor not analyzed as LED circuit
  (signal_analysis)
- UEXT connector standard not identified
  (signal_analysis)

### Suggestions
- Filter SPI/I2C false positives from connector pins when no devices are on the bus
- Fix subcircuit neighbor detection
- Detect LED + current limiting resistor as a basic circuit pattern

---
