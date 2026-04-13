# Findings: jonathan-tooley/903 / KiCad_Real903_A-GA

## FND-00002519: Vintage 903 computer board with 6 custom LS_Gen ICs, DIN41612 connector, 560 mounting pads, 124 test points. Correct parsing overall. Issues: multi-unit IC pin_nets shows wrong-unit pins, 6v/Neg6v power rails classified as signal.

- **Status**: confirmed
- **Analyzer**: schematic
- **Source**: KiCad_Real903_A-GA_A-GA.sch.json
- **Created**: 2026-04-09

### Correct
- 693 components correct: 560 MH + 124 test points + 6 ICs + 2 caps + 1 connector
- J1 DIN41612 all 64 pins correctly mapped including letter-based pin numbers
- Signal analysis correctly empty for this passive backplane design

### Incorrect
- U1-U6 unit 1 pin_nets show unit 2 power pins (21/22/23) instead of unit 1 signal pins (1-6, 11-13). Multi-unit pin_nets merging bug.
  (components[U1-U6 unit 1].pin_nets)
- 6v and Neg6v classified as 'signal' but are +6V and -6V power rails supplying all ICs
  (design_analysis.net_classification)
- power_rails missing 6v and Neg6v — only lists GND
  (statistics.power_rails)

### Missed
- C1/C2 (6u8) decoupling caps between 6v/Neg6v and GND not detected
  (signal_analysis.decoupling_analysis)

### Suggestions
- Fix multi-unit pin_nets: each unit entry should show only its own pins
- Recognize voltage-pattern net names (6v, Neg6v, -6v, +5v) as power rails

---
