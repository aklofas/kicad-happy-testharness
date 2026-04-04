# Findings: avdisplay-cape / avdisplay-cape

## FND-00001847: Crystal circuit correctly detected with Y101 16 MHz and 30pF load capacitors C103/C104; I2C bus correctly detected on I2C2_SCL/SDA with 5.6K pull-ups and CAT24C256 EEPROM; CAN bus correctly detecte...

- **Status**: new
- **Analyzer**: schematic
- **Source**: avdisplay-cape.kicad_sch.json.json
- **Created**: 2026-03-24

### Correct
- The MCP2515 CAN controller uses a 16 MHz crystal Y101 with two 30pF load capacitors (C103 and C104). The analyzer correctly identifies the crystal circuit, reports effective load capacitance of 18pF (series combination plus stray), and flags it in both signal_analysis.crystal_circuits and design_observations.
- The I2C bus (I2C2_SCL and I2C2_SDA) to the CAT24C256 EEPROM (U102) has 5.6K pull-up resistors (R105 and R106) to the +3.3V rail. The bus_analysis.i2c correctly identifies both lines with pull-ups and the connected device.
- The design has a full CAN implementation: MCP2515 SPI-to-CAN controller (U101), two MCP2551 transceivers (U104 and U106), level translator TXB0104PW (U105), CAN termination resistors (R109, R112), switchable terminators (SW102), and TVS protection diodes (D101, D102). The bus_analysis.can correctly identifies MCP_CAN_TX and MCP_CAN_RX nets.
- The schematic reports 46 total_components across all types (13 resistors, 12 capacitors, 6 ICs, 6 connectors, 2 transistors, 2 diodes, 2 switches, 1 LED, 1 crystal, 1 jumper). The PCB reports 46 footprints and 126 nets, both matching the schematic exactly.

### Incorrect
- The transistor_circuits output for Q101 and Q102 (PSMN4R3-30BL power MOSFETs in an LTC4370 OR-controller circuit) both contain a 'led_driver' field associating them with D103 (status LED) via R110 and R111 (2.5mΩ sense resistors). This is incorrect: R110 and R111 are current-sense resistors for the LTC4370 power OR controller, not current-limiting resistors for D103. D103's anode is on VDD_5V and its cathode connects to R113 (680Ω) to GND — Q101 and Q102 do not control D103. The false association occurs because R110/R111 share VDD_5V with D103's anode net.
  (signal_analysis)

### Missed
- U103 (LTC4370xMS) is an OR-controller and current-sharing IC that controls two N-channel MOSFETs (Q101, Q102) for dual-input power ORing. It is a power management IC and could reasonably appear in signal_analysis.power_regulators. The analyzer's power_regulators list is empty for this design, missing the LTC4370 circuit. The subcircuits section does correctly detect U103 and its neighbors, but the regulator detector does not classify it.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00001848: 4-layer stackup correctly identified with In1.Cu and In2.Cu as power planes

- **Status**: new
- **Analyzer**: pcb
- **Source**: avdisplay-cape.kicad_pcb.json.json
- **Created**: 2026-03-24

### Correct
- The PCB is a 4-layer board with F.Cu and B.Cu as signal layers, and In1.Cu and In2.Cu correctly classified as 'power' type layers. This matches the KiCad layer definition in the source file where both inner layers are assigned type 'power'. The avdisplay-cape uses these planes for power distribution.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
