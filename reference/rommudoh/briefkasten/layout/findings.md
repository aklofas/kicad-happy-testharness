# Findings: briefkasten / layout_layout

## FND-00002292: RC filter false positive: R4/C2 flagged with ground_net='+3V3'; Decoupling observation incorrectly flags U1 (ESP-01S) as lacking decoupling caps on +3V3; Transistor switch circuit (Q1 NPN) has no b...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: schematic_briefkasten_layout_layout.kicad_sch.json
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
- The analyzer detects two RC filters. The second one (R4=1kΩ, C2=1000µF) sets ground_net to '+3V3', which is wrong. C2's positive pin connects to +3V3 and negative pin connects to IO0. This means the analyzer is treating +3V3 as the 'ground' side of the RC because C2 bridges +3V3 and IO0. The combination is actually a bulk decoupling capacitor for the +3V3 rail, not an RC filter at all. The 0.16 Hz cutoff frequency is also implausibly low for a signal filter.
  (signal_analysis)
- design_observations reports U1 (ESP-01S) as having 'rails_without_caps: ["+3V3"]'. However, both C1 (10µF) and C2 (1000µF) are connected to the +3V3 rail in the schematic. The ic_pin_analysis for U1 confirms decoupling caps exist (has_decoupling_cap: true with C2 listed on the VCC and CH_PD pins). The design_observations decoupling checker appears to be producing a contradictory result.
  (signal_analysis)

### Missed
- The transistor_circuits entry for Q1 shows base_resistors=[] and load_type='other'. Q1's base net (__unnamed_1) connects directly to SW2 (reed switch). While R4 (1kΩ) is not directly in the base net, the design uses Q1 as a switch triggered by the reed contact: the load on collector is R1 (1MΩ pull-up to RST). The load_type='other' is acceptable, but the design topology of this reed switch → NPN → ESP reset circuit is not described in design_observations, which could note the switchable reset topology.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00002293: Courtyard overlaps correctly detected for J1/SW3 and Q1/R1 component pairs

- **Status**: new
- **Analyzer**: pcb
- **Source**: pcb_briefkasten_layout_layout.kicad_pcb.json
- **Created**: 2026-03-24

### Correct
- The PCB analyzer correctly identifies two courtyard overlaps: J1 (BATT+ single-pin header) overlaps with SW3 (power switch 3-pin header) by 12.85 mm², and Q1 (TO-92L transistor) overlaps with R1 (axial resistor) by 9.576 mm². These are real layout issues in the PCB — the components are placed too closely. The 13-footprint all-THT 70×50mm board is correctly parsed with routing_complete=true.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
