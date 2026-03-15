# Findings: uext-esp32 / UEXT_ESP32

## FND-00000142: Very simple UEXT expansion board with ESP32-WROOM-32D (10 components). Minimal but mostly correct analysis. False positive SPI bus detection from UEXT connector pin names. Auto-program transistors correctly detected.

- **Status**: confirmed
- **Analyzer**: schematic
- **Source**: repos/uext-esp32/UEXT_ESP32.sch
- **Created**: 2026-03-14

### Correct
- ESP32-WROOM-32D correctly identified as sole IC on +3V3 rail
- UART TX/RX (UEXT_TX/UEXT_RX and FTDI_TX/FTDI_RX) correctly detected
- Two MMBT3904 auto-program transistors (Q1/Q2) correctly detected with collector/emitter nets
- Decoupling: single 10uF cap on +3V3 correctly identified as bulk-only (no bypass)
- Single pin net warning for FTDI_RX/FTDI_TX is valid - these connect only to ESP32 pins

### Incorrect
- False positive SPI bus detected - UEXT connector has SPI pins but they are UART signals (MOSI mapped to UEXT_RX, SCK to UEXT_TX)
  (design_analysis.bus_analysis.spi)
- I2C bus detected on unnamed nets with no devices - these are unconnected UEXT I2C pins, not an active bus
  (design_analysis.bus_analysis.i2c)
- GND listed in power domain domain_groups for U1 - GND is ground reference not a power domain
  (design_analysis.power_domains)
- ERC warning for GPIO2 net - pin IO34 is input-only on ESP32 and is correctly connected to UEXT RXD through J1
  (design_analysis.erc_warnings)

### Missed
- UEXT connector standard (10-pin connector with 3.3V, GND, TXD, RXD, SCL, SDA, MISO, MOSI, SCK, CS) not identified
  (signal_analysis)
- Auto-program function of Q1/Q2 (DTR->GPIO0, RTS->RESET) not identified as boot/flash circuit
  (signal_analysis.transistor_circuits)
- No power regulator detected - board is powered from UEXT 3.3V or FTDI connector
  (signal_analysis.power_regulators)
- Logo/graphic components (LOGO1, LOGO2) classified as type graphic which is fine but 2 of 10 components are non-functional
  (statistics)

### Suggestions
- Filter SPI false positives when pins map to UART signals on the actual IC
- Filter I2C false positives when nets have no connected devices
- Exclude GND from power domain groups
- Detect ESP32 auto-program circuit pattern (DTR/RTS via BJTs to GPIO0/EN)

---
