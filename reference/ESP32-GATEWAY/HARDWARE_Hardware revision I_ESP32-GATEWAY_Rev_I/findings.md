# Findings: ESP32-GATEWAY / HARDWARE_Hardware revision I_ESP32-GATEWAY_Rev_I

## FND-00000120: Legacy KiCad 5 format - Ethernet PHY detected but signal analysis severely limited; RMII signals misclassified as UART; zero voltage dividers/RC filters/power regulators detected despite TPS62A02 and CH340 being present; all subcircuit neighbors empty

- **Status**: confirmed
- **Analyzer**: schematic
- **Source**: repos/ESP32-GATEWAY/HARDWARE/Hardware revision I/ESP32-GATEWAY_Rev_I.sch
- **Related**: KH-016
- **Created**: 2026-03-14

### Correct
- Ethernet PHY LAN8710A (U4) correctly identified in ethernet_interfaces
- Two BJT transistor circuits (Q4, Q5 BC817-40) detected in transistor_circuits
- CH340X USB-UART bridge (U5) correctly identified as subcircuit IC
- TPS62A02 (U1) correctly identified as subcircuit IC
- UART nets GPIO1/U0TXD and GPIO3/U0RXD correctly detected
- Power rails correctly enumerated: +3.3V, +3.3VLAN, +5V, +5V_EXT, +5V_USB

### Incorrect
- RMII Ethernet signals (GPIO19/EMAC_TXD0, GPIO22/EMAC_TXD1, GPIO25/EMAC_RXD0, GPIO26/EMAC_RXD1, GPIO27/EMAC_RX_CRS_DV, GPIO21/EMAC_TX_EN) misclassified as UART instead of Ethernet/RMII bus
  (design_analysis.bus_analysis.uart)
- Ethernet PHY detected but magnetics and RJ45 connector (LAN1) not linked to PHY
  (signal_analysis.ethernet_interfaces)
- BJT transistor circuits show collector_is_power: false and emitter_is_ground: false, with no base resistors detected - suggests the pin connectivity analysis is not working for legacy format
  (signal_analysis.transistor_circuits)
- All subcircuit neighbor_components lists are empty - no adjacent passives found for any IC
  (subcircuits)

### Missed
- Zero voltage dividers detected - TPS62A02 has a feedback divider that should be found
  (signal_analysis.voltage_dividers)
- Zero RC filters detected in the entire design
  (signal_analysis.rc_filters)
- Zero power regulators detected - TPS62A02 (U1) switching regulator completely missed
  (signal_analysis.power_regulators)
- Zero protection devices detected despite TVS diodes (TVS1-TVS4) and Schottky diode D6 present
  (signal_analysis.protection_devices)
- Zero decoupling analysis despite 21 capacitors on the board
  (signal_analysis.decoupling_analysis)
- CH340X USB-UART bridge not identified as USB interface
  (design_analysis.bus_analysis)
- Micro SD card interface (MICRO_SD1) not detected
  (signal_analysis.memory_interfaces)
- Separate +3.3VLAN power domain (dedicated Ethernet PHY supply) not analyzed for isolation from main +3.3V
  (design_analysis.power_domains)

### Suggestions
- Legacy KiCad 5 format has the same comprehensive signal analysis failure as ESP32-C6-EVB - confirms this is a systematic KH-016 issue
- RMII bus detection should be added: when net names contain EMAC/RMII/TXD/RXD with an Ethernet PHY present, classify as RMII instead of UART
- Net name pattern matching for bus classification should have priority: EMAC > UART when both patterns match
- Separate LAN power domain (+3.3VLAN) is a good design practice that the analyzer should note

---
