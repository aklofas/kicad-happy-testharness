# Findings: mwrnd/OpenCAPI_Breakout / OpenCAPI_Breakout

## FND-00000084: KiCad 8 high-speed connector breakout board. 36 components (all connectors - 1 OpenCAPI host connector + 35 coaxial connectors). Differential pair detection is excellent (17/17 pairs found). UART bus detection is a false positive - Tx/Rx named nets are high-speed serial lanes, not UART.

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: repos/OpenCAPI_Breakout/OpenCAPI_Breakout.kicad_sch
- **Created**: 2026-03-14

### Correct
- All 36 components correctly extracted as connectors
- All 17 differential pairs correctly identified: 8x Tx, 8x Rx, 1x REFCLK
- GND power rail correctly identified
- I2C bus correctly detected (SCL/SDA nets present on OpenCAPI connector)
- Net classification mostly correct: 33 data nets, 1 ground, control and clock nets identified
- PRE_DETECT and INT_RST control signals correctly identified as named nets

### Incorrect
- 32 false positive UART detections - all Tx*/Rx* nets are OpenCAPI high-speed serial lanes (25 Gbps), not UART. The analyzer is matching on Tx/Rx naming convention without considering that these are differential pairs on a high-speed connector
  (design_analysis.bus_analysis.uart)
- ERC no_driver warnings on Rx nets are misleading - coaxial connectors have passive pins which is correct for a breakout board. The Rx pins on J1 are typed as input but the coax connector pins are passive, which is the expected topology
  (design_analysis.erc_warnings)
- All 36 unique_parts count is inflated - many coax connectors are identical parts with different net labels. BOM should consolidate identical Conn_Coaxial footprints
  (statistics)

### Missed
- No high-speed serial interface detection - this is an OpenCAPI breakout with 8 lanes of 25 Gbps differential pairs. Should be identified as a high-speed serial link topology
  (signal_analysis)
- Connector-only breakout board topology not recognized - this is purely passive routing from one connector to individual coax connectors for probing/testing
  (signal_analysis)

### Suggestions
- UART detection should not trigger when Tx/Rx nets are part of differential pairs
- Consider adding OpenCAPI/PCIe/high-speed serial lane detection based on differential pair count and connector types
- BOM consolidation should group identical connector symbols with different values
- ERC warnings should be suppressed or qualified for breakout board topologies where passive-to-input connections are intentional

---
