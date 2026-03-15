# Findings: iMX8MP-SOM-EVB / HARDWARE_iMX8MP-SOM-EVB-rev.b_iMX8MPLUS-SOM-EVB_Rev_B

## FND-00000173: 329-component OLIMEX iMX8M Plus EVB. Correct: Ethernet PHYs, crystals, HDMI, ESD protection, SPI buses, USB pairs. Incorrect: U5/U10 MCP2562 CAN transceivers have completely scrambled pin-to-net mapping, VR1/VR2 AMS1117 as varistors, Flash_Con1 as fuse, T1/T2 digital transistors as transformers, false three-phase bridge from PHY strap FETs. Missed: AMS1117 LDOs not in power_regulators, USB power switches, several component type misclassifications.

- **Status**: confirmed
- **Analyzer**: schematic
- **Source**: iMX8MPLUS-SOM-EVB_Rev_B.sch.json
- **Created**: 2026-03-15

### Correct
- 329 components correctly counted
- Dual KSZ9031 Ethernet PHYs detected
- 25MHz crystals with 33pF load caps detected
- ESDS314DBVR ESD ICs correctly detected

### Incorrect
- U5/U10 MCP2562 CAN transceivers have completely scrambled pin-to-net mapping (GND mapped to CAN1H, VDD to CAN1L, etc)
  (nets)
- VR1/VR2 AMS1117-1.2 LDO regulators classified as varistor
  (statistics.component_types)
- Flash_Con1 (40-pin board-to-board connector) classified as fuse
  (statistics.component_types)
- T1/T2 LMUN2211/2235 digital transistors classified as transformers (T prefix)
  (statistics.component_types)
- False three-phase bridge circuit from PHY address strap FETs
  (signal_analysis.bridge_circuits)

### Missed
- VR1/VR2 AMS1117-1.2 LDOs not detected as power regulators
  (signal_analysis.power_regulators)
- MICRO_SD1, MICROPHONE1 classified as other instead of connector
  (statistics.component_types)

### Suggestions
- Fix pin-to-net mapping for multi-pin ICs in legacy KiCad 5 format
- Add AMS1117/VR prefix to regulator classifier
- Recognize T-prefix components with transistor lib_id as transistors

---
