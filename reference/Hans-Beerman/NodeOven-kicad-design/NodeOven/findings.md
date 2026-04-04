# Findings: NodeOven-kicad-design / NodeOven

## FND-00000988: Q1/Q2/Q3 NPN transistor circuits show collector_net=GND which is topologically backward for NPN switch; Relay K1 (SANYOU SRD Form C) and flyback diodes D1/D2 (1N4004) correctly identified; No relay...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: NodeOven.sch.json
- **Created**: 2026-03-23

### Correct
- Component classification correctly identifies K1 as relay type with THT footprint. D1/D2 as 1N4004 diodes correctly typed. 3 NPN transistors (BC547) correctly identified. Power rails +12V, +3.3V, +5V, GND all correctly extracted.

### Incorrect
- BC547 NPN transistors (Q1, Q2, Q3) are all reported with collector_net=GND and emitter_is_ground=false. Verified in the net data: Q1 pin 1 (C) is indeed wired to GND and pin 3 (E) drives connectors J7/J8. This is an unusual topology — either the schematic has an error (NPN with collector to GND is not a standard switch) or the device is being used in a non-standard way. The analyzer correctly extracts the pin connections as drawn, but collector_is_power=true is wrong since GND is ground not a power rail. The load_type='connector' is correct.
  (signal_analysis)

### Missed
- The design has 3x BC547 NPN transistors each driving what appears to be relay-related loads, with 1N4004 flyback diodes (D1/D2) for inductive protection. signal_analysis.protection_devices is empty and snubbers is empty. The relay K1 is not identified in a relay_driver_circuits section. A relay driver detector or inductive protection detector would surface this pattern.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00000989: Board dimensions null correctly reported when no Edge.Cuts outline found; Copper presence warning correctly issued for unfilled zones; +12V net routed at 1.0mm width appropriate for higher current ...

- **Status**: new
- **Analyzer**: pcb
- **Source**: NodeOven.kicad_pcb.json
- **Created**: 2026-03-23

### Correct
- board_outline.edge_count=0 and board_width_mm=null. The KiCad 5 PCB file lacks a board outline in Edge.Cuts, so the analyzer correctly reports null dimensions rather than guessing.
- NodeOven PCB has zone_count=0 (no filled zones), and copper_presence reports a warning about no filled polygon data. This is accurate — the design appears to have zones defined but not filled in the saved file.
- power_net_routing shows +12V and +3V3 nets both at 1.0mm track width consistently, while +5V and GND use 0.25-1.0mm. The 1.0mm width for 12V relay supply is appropriate design practice.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
