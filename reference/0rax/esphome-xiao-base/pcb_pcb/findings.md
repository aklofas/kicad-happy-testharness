# Findings: esphome-xiao-base / pcb_pcb

## FND-00002060: test_coverage reports SDA, SCL, SPI, UART, and power nets as uncovered even though they are all exposed by J2 (a 2x6 debug breakout connector); J2 debug connector classified solely as 'uart' interf...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: schematic_esphome-xiao-base_pcb_pcb.kicad_sch.json
- **Created**: 2026-03-24

### Correct
- The analyzer detects the I2C bus on SDA and SCL nets routed through J1 (OLED header) and J2. It correctly notes has_pull_up=false for both lines and flags them in design_observations, since the schematic contains no pull-up resistors on SDA or SCL. The XIAO-ESP32 module's internal pull-ups are relied upon here.

### Incorrect
- The test_coverage section lists J2 (Conn_02x06_Odd_Even) in debug_connectors with connected_nets=['+3.3V', '+5V', 'GND', 'GND', 'SDA', 'SCL', 'CSn', 'TX', 'MOSI', 'MISO', 'SCK', 'RX']. Despite this, covered_nets=[] and uncovered_key_nets includes SDA, SCL, TX, MOSI, MISO, SCK, RX, +3.3V, +5V — all of which are present in J2's connected_nets. The algorithm populates debug_connectors correctly but fails to update covered_nets from the connector's exposed nets, making the coverage report entirely misleading.
  (test_coverage)
- The test_coverage debug_connectors entry for J2 shows interface='uart'. The connector's 12 pins expose: SDA, SCL (I2C), MOSI, MISO, SCK, CSn (SPI), TX, RX (UART), +3.3V, +5V, and two GND pins. It is a general-purpose breakout header, not a dedicated UART connector. The single-interface classification likely picks the first matching protocol and stops, losing the multi-protocol nature of the connector.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---
