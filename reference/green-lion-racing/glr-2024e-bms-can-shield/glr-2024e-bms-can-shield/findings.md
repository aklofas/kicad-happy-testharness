# Findings: glr-2024e-bms-can-shield / glr-2024e-bms-can-shield

## FND-00002103: CAN bus not detected in bus_analysis despite two TLE6250 CAN transceivers with CANH/CANL pins; design_observations incorrectly reports +5V as rails_without_caps for IC1/IC2, contradicting pin-level...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: schematic_glr-2024e-bms-can-shield_glr-2024e-bms-can-shield.kicad_sch.json.json
- **Created**: 2026-03-24

### Correct
- The analyzer correctly: identifies D1/D2 as ESDCAN01-2BLY ESD ICs protecting CAN H/L nets; builds subcircuit neighborhoods around IC1 and IC2 capturing the correct neighbor components (D1/D2, R1-R4, connectors); categorizes K1 as a relay (Omron G5V-2 DPDT); correctly classifies Q1 and Q2 as NPN transistors with correct base/collector/emitter net assignments; and identifies 4 power rails (+3V3, +5V, +12V, GND).

### Incorrect
- The signal_analysis.design_observations entries for IC1 and IC2 (TLE6250GV33XUMA1) both report rails_without_caps: ['+5V', '+3V3'] and rails_with_caps: []. However, the ic_pin_analysis for IC1 shows pin 3 (VCC, +5V) has has_decoupling_cap: true with decoupling_caps: [{C1, 0.1uF}, {C2, 0.1uF}]. The pin-level analysis correctly finds C1 and C2 on the +5V rail, but the design_observations aggregator contradicts this. Additionally signal_analysis.decoupling_analysis is an empty list when it should contain entries for the +5V rail capacitors.
  (signal_analysis)

### Missed
- The schematic has two TLE6250GV33XUMA1 CAN transceivers (IC1, IC2) with pins explicitly named CANH and CANL connected to nets 'CAN 1 H', 'CAN 1 L', 'CAN 2 H', 'CAN 2 L'. ESD protection diodes ESDCAN01-2BLY are on those nets. The subcircuits section correctly identifies IC1/IC2 as 'CAN Interface IC', and protection_devices correctly identifies D1/D2 as CAN ESD protection. However, design_analysis.bus_analysis.can is an empty list. The analyzer has enough information (CANH/CANL pin names on the ICs plus the CAN-named nets) to populate this but does not.
  (design_analysis)

### Suggestions
(none)

---
