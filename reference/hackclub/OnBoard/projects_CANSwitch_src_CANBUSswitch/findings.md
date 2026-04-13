# Findings: hackclub/OnBoard / projects_CANSwitch_src_CANBUSswitch

## FND-00000097: Passive CAN bus switch using 4PDT mechanical switch with termination resistors. No active electronics. Analyzer output is reasonable for this passive-only design.

- **Status**: confirmed
- **Analyzer**: schematic
- **Source**: repos/OnBoard/projects/CANSwitch/src/CANBUSswitch.kicad_sch
- **Created**: 2026-03-14

### Correct
- 4PDT switch correctly identified as switch type
- 2 resistors and 2 connectors correctly classified
- No power rails detected, correct for a passive switching circuit
- No bus protocols detected, which is technically correct since this is just a mechanical switch, not an active CAN transceiver

### Incorrect
(none)

### Missed
- The two resistors are likely 120 ohm CAN bus termination resistors. No observation about CAN termination is generated despite the project being named CANBUSswitch.
  (signal_analysis.design_observations)

### Suggestions
- Could infer from component placement and typical 120 ohm values that this is a CAN bus termination/switching board, though without labeled nets or a CAN transceiver the analyzer has limited information

---
