# Findings: ESP32-EVB / HARDWARE_REV-L_ESP32-EVB_Rev_L

## FND-00000111: CAN bus interface detected in bus_analysis but CAN transceiver (U6 SN65HVD230) not analyzed as subcircuit with neighbor components; Ethernet PHY magnetics and connector not linked to PHY

- **Status**: confirmed
- **Analyzer**: schematic
- **Source**: repos/ESP32-EVB/HARDWARE/REV-L/ESP32-EVB_Rev_L.kicad_sch
- **Related**: KH-016
- **Created**: 2026-03-14

### Correct
- CAN bus nets CANH/CANL correctly identified in bus_analysis
- Ethernet PHY (U4 LAN8710A) correctly identified with ethernet_interfaces detector
- TPS62A02 switching regulator correctly identified with feedback divider ratio 0.183 giving ~3.3V output
- TVS1 (ESDS314DBVR) correctly identified as ESD protection on Ethernet differential pairs RXN-/RXP+/TXN-/TXP+
- SMBJ6.0A TVS diode on +5V rail correctly detected as protection device
- Voltage divider R9/R10 (470k/470k) for battery sensing correctly found with 0.5 ratio
- CAN bus voltage divider R13/R15 (330R/680R) correctly identified connecting to GPI35/CAN-RX

### Incorrect
- Ethernet RMII signals (GPIO19/TXD0, GPIO22/TXD1, etc.) misclassified as UART in bus_analysis instead of being recognized as Ethernet RMII bus signals
  (design_analysis.bus_analysis.uart)
- Only 1 power regulator detected (TPS62A02 for 3.3V) but board has additional regulators - the SY8089 buck converter and battery charger circuit are not identified
  (signal_analysis.power_regulators)

### Missed
- CAN transceiver SN65HVD230 (U6) not detected as a bus transceiver subcircuit - should identify CAN-TX/CAN-RX connections to ESP32 and CANH/CANL bus lines
  (signal_analysis.ethernet_interfaces)
- Ethernet magnetics (transformer/common-mode choke between PHY and RJ45 connector) not linked to Ethernet PHY in ethernet_interfaces
  (signal_analysis.ethernet_interfaces)
- No crystal circuit detected despite ESP32-WROOM module likely having internal crystal; the 50MHz crystal for the LAN8710A PHY is also not identified
  (signal_analysis.crystal_circuits)
- Relay driver circuits (Q1/Q2 driving REL1/REL2 with flyback diodes D1/D3) not identified as transistor switch circuits
  (signal_analysis.transistor_circuits)
- USB-UART bridge (likely CH340 or similar) not identified as a subcircuit with its USB data lines
  (subcircuits)

### Suggestions
- Add CAN bus transceiver detection to identify standard CAN PHY chips (SN65HVD230, MCP2551, TJA1050) and link TX/RX to controller and CANH/CANL to bus
- Improve Ethernet interface detection to link PHY to magnetics and RJ45 connector via differential pairs
- Detect relay driver circuits (BJT/MOSFET + flyback diode + relay coil) as a standard subcircuit pattern
- RMII signals should not be classified as UART - the net names contain EMAC/RMII hints that should override UART classification

---
