# Findings: gpgreen/fuel_capacity_sensor / fuel_capacity_sensor

## FND-00002076: CAN bus detection lists only U6 (MCP2551 transceiver), omitting U7 (AT90CAN64-16AU MCU) from devices; Correctly identified multi-ground isolation design with ADuM1201CR digital isolator and four di...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: schematic_fuel_capacity_sensor_fuel_capacity_sensor.sch.json.json
- **Created**: 2026-03-24

### Correct
- The isolation_barriers detector correctly identified GND, GNDA, CAN-GND, and GNDS as four separate ground domains, and listed U3 (ADuM1201CR) as the isolation component. This is accurate: the design galvanically isolates the capacitive sensor measurement side (GNDS), the analog section (GNDA), the CAN bus side (CAN-GND), and the main digital section (GND).

### Incorrect
- The bus_analysis.can entry identifies the CAN network with U6 as both transceiver and the sole device. However U7 (AT90CAN64-16AU) is the CAN controller MCU that drives TXCAN/RXCAN through U3 (ADuM1201CR digital isolator) to U6. U7 should appear in the devices list as the CAN controller. The net-level cross_domain_signals section does correctly show TXCAN and RXCAN connecting U3 and U7, but the bus_analysis.can aggregation does not include U7 as a participant.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00002077: Correctly reported unrouted PCB — zero track segments and 54 unrouted nets on a KiCad 4 early-stage layout

- **Status**: promoted
- **Analyzer**: pcb
- **Source**: pcb_fuel_capacity_sensor_fuel_capacity_sensor.kicad_pcb.json.json
- **Created**: 2026-03-24

### Correct
- The PCB file (KiCad 4, version 4) is an unfinished layout — the source file header confirms tracks=0. The analyzer correctly reports track_segments=0, via_count=0, copper_layers_used=0, routing_complete=false, and unrouted_net_count=54. The footprint_count of 87 matches the source file's modules=87 exactly.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
