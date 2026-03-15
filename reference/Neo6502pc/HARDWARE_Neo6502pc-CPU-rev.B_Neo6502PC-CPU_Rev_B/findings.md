# Findings: Neo6502pc / HARDWARE_Neo6502pc-CPU-rev.B_Neo6502PC-CPU_Rev_B

## FND-00000171: Neo6502 retro computer board with RP2040 + W65C02S. IDC cables as capacitors, buzzer as switch, expansion bus misclassified, SPI missed, false I2C on HDMI/GPIO.

- **Status**: confirmed
- **Analyzer**: schematic
- **Source**: HARDWARE_Neo6502pc-CPU-rev.B_Neo6502PC-CPU_Rev_B.kicad_sch.json
- **Created**: 2026-03-15

### Correct
- All 8 ICs correctly identified (RP2040, W65C02S, etc.)
- Power rails correctly identified
- I2C bus with pullup resistors correctly detected
- UART interface correctly detected
- HDMI differential pairs correctly identified
- USB compliance correctly analyzed

### Incorrect
- Cable-PWR1 and Cable-pUEXT1 IDC cable connectors classified as capacitor
  (components)
- SPK1 piezo buzzer classified as switch instead of transducer
  (components)
- BUS1 40-pin expansion bus connector classified as SWD debug connector
  (signal_analysis.bus_interfaces)
- HDMI and GPIO nets falsely detected as I2C interfaces
  (signal_analysis.bus_interfaces)

### Missed
- SPI bus between RP2040 and peripheral ICs not detected
  (signal_analysis.bus_interfaces)

### Suggestions
- Recognize Cable and IDC connector library symbols as connectors not capacitors
- Classify buzzer and speaker symbols as transducer not switch
- Do not classify generic expansion connectors as SWD based solely on pin count
- Validate I2C detection by requiring SCL+SDA net name patterns, not just any pair of signals on pullup resistors
- Detect SPI from MOSI/MISO/SCK/CS net name patterns

---

## FND-00000177: Neo6502 retro computer CPU board (122 components). Correct: all 8 ICs, power rails, I2C with pullups, UART, HDMI pairs, USB compliance, 7 DNP parts. Incorrect: Cable-PWR1/Cable-pUEXT1 as capacitor (are IDC cables), SPK1 buzzer as switch, BUS1 40-pin expansion as SWD debug connector, HDMI/GPIO nets falsely detected as I2C. Missed: SPI bus not detected, test points not in test_coverage.

- **Status**: confirmed
- **Analyzer**: schematic
- **Source**: HARDWARE_Neo6502pc-CPU-rev.B_Neo6502PC-CPU_Rev_B.kicad_sch.json
- **Created**: 2026-03-15

### Correct
- All 8 ICs correctly identified (RP2040, W65C02S, CH217K, CH334S, ZD25Q16B, 3x 74LVC245)
- I2C bus with 2.2k pullups correctly detected
- 4 HDMI differential pairs with 270R series resistors detected
- USB-C CC 5.1k pulldowns pass compliance

### Incorrect
- Cable-PWR1/Cable-pUEXT1 (IDC cables) misclassified as capacitor
  (components.type)
- SPK1 buzzer misclassified as switch
  (components.type)
- BUS1 40-pin expansion bus misidentified as SWD debug connector
  (test_coverage.debug_connectors)
- HDMI differential signals and GPIO control nets falsely detected as I2C
  (bus_analysis.i2c)

### Missed
- SPI bus (SPI1_RX/CSn/SCK/TX) not detected despite clear net names
  (bus_analysis.spi)
- 10 test points (TESTPAD) not in test_coverage despite being in component_types
  (test_coverage.test_points)

### Suggestions
- Add Cable/cable lib_id patterns as connector type
- Add Buzzer/Speaker patterns as speaker type
- Require majority debug pins for debug connector classification
- Filter I2C detection to exclude differential pair nets

---
