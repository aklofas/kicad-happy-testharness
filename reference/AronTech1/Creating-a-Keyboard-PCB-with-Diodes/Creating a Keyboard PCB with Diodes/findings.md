# Findings: Creating-a-Keyboard-PCB-with-Diodes / Creating a Keyboard PCB with Diodes

## FND-00000432: connectivity_issues.single_pin_nets is empty but 9 single-pin nets exist; MX_stab stabilizer components (S1, S2, S3) are classified as type 'switch'

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: Creating a Keyboard PCB with Diodes.kicad_sch.json
- **Created**: 2026-03-23

### Correct
(none)

### Incorrect
- The three Cherry MX-style stabilizers (S1=STAB_MX_P_2u, S2=STAB_MX_P_2.25u, S3=STAB_MX_P_6.25u) are purely mechanical components with no electrical pins (pin_uuids is empty for all three). They are classified as type='switch' and counted in statistics.component_types.switch (contributing to the total of 44, inflating the switch count by 3 relative to actual key switches). Stabilizers should not be classified as switches; a distinct 'mechanical' or 'stabilizer' type would be more accurate, or they should be excluded from the switch count.
  (statistics)

### Missed
- Nine nets each contain exactly one pin: __unnamed_20 (U1 D3/bidirectional), __unnamed_21 (U1 B0/bidirectional), __unnamed_22 (U1 VCC/power_out), __unnamed_23 (U1 GND/power_out), __unnamed_24 (U1 RST/bidirectional), __unnamed_25 (U1 GND/power_out), __unnamed_26 (U1 GND/power_out), __unnamed_27 (U1 D0/bidirectional), __unnamed_28 (U1 D4/bidirectional). Three are unconnected power pins (VCC and three GND on the ProMicro), which represent a real design concern. The analyzer reports connectivity_issues.single_pin_nets as [] instead of listing these 9 nets.
  (connectivity_issues)

### Suggestions
- Fix: MX_stab stabilizer components (S1, S2, S3) are classified as type 'switch'

---
