# Findings: VinnyCordeiro/BT_DC_motor_board / BoxTurtle_DC_motors_RPiPico

## FND-00000399: SW1–SW12 classified as 'switch' instead of 'connector'; Connector count understated due to SW1–SW12 misclassification; CAN bus interface not detected in bus_analysis; bus_topology.detected_bus_sign...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: BoxTurtle_DC_motors_RPiPico.kicad_sch.json
- **Created**: 2026-03-23

### Correct
(none)

### Incorrect
- SW1–SW12 use lib_id Connector_Generic:Conn_01x03 (3-pin JST connectors) but are classified as type 'switch' solely because their reference designators begin with 'SW'. The only real switch in the design is SW13 (lib_id Switch:SW_SPDT, value K3-1204D). This inflates the switch count from 1 to 13 and deflates the connector count from 27 to 15 in statistics.component_types.
  (statistics)
- Because SW1–SW12 (Connector_Generic:Conn_01x03) are typed as 'switch', the connector count is reported as 15 instead of the correct 27. There are 15 connectors with 'J' references plus 12 connectors with 'SW' references (SW1–SW12).
  (statistics)
- The 'width' field in detected_bus_signals reports the total number of label placements rather than the number of unique signal lines in the bus. SLP_1..SLP_4 has 4 unique nets but 12 label placements (each net appears 3 times), so width=12 is reported instead of 4. SW1..SW12 has 12 unique nets but 36 label placements (each net appears 3 times), so width=36 is reported instead of 12.
  (bus_topology)

### Missed
- The design has a well-defined CAN interface: global labels CAN-TX and CAN-RX connecting U1 (RPi Pico), U2 (STM32F401), and J15 (a 4-pin connector explicitly valued 'CAN'), with R1 (120Ω) as a termination resistor and JP1 (jumper) to enable/disable it. Despite this, design_analysis.bus_analysis.can is an empty list. The test_coverage section does identify CAN-TX and CAN-RX but mislabels them as 'uart' category.
  (design_analysis)
- J5 is a 3-pin connector (value 'AMS1117 module') that interfaces an AMS1117 3.3V LDO regulator module: pin 1 connects to +5V (input), pin 2 connects to +3.3V (output), pin 3 connects to GND. This is a 5V→3.3V regulator path and should appear in signal_analysis.power_regulators, but the list is empty.
  (signal_analysis)
- D1 (BAT85 Schottky diode) has its cathode on the +5V rail and its anode connected to pin 3 (common) of SW13 (SPDT switch K3-1204D). This is a steering/ORing diode that routes the SW13 selected output to the +5V rail. D2 is correctly detected as a protection device (reverse_polarity), but D1 is entirely absent from signal_analysis.protection_devices. Both diodes play analogous roles in the power steering topology and D1 should also appear there.
  (signal_analysis)

### Suggestions
- Fix: SW1–SW12 classified as 'switch' instead of 'connector'
- Fix: Connector count understated due to SW1–SW12 misclassification

---
