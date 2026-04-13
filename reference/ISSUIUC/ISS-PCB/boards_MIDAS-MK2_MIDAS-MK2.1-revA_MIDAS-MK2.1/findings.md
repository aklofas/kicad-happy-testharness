# Findings: ISSUIUC/ISS-PCB / boards_MIDAS-MK2_MIDAS-MK2.1-revA_MIDAS-MK2.1

## FND-00000155: Data acquisition board with ESP32-S3, motion sensors, pyro channels, CAN, LoRa. Good voltage divider and feedback detection. Switching regulators missing output_rail; isolation components not linked.

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: boards_MIDAS-MK2_MIDAS-MK2.1-revA_MIDAS-MK2.1.kicad_sch.json
- **Related**: KH-086, KH-087
- **Created**: 2026-03-15

### Correct
- Voltage dividers correctly identified for pyro sense (100k/30k) and feedback dividers
- TPS566242 feedback (135k/30k -> 3.3V) and TPS564247 feedback (155k/30k -> 3.7V) correct with accurate Vout
- Switching regulator topology correctly identifies TPS566242 and TPS564247 with inductor references

### Incorrect
- Switching regulators TPS566242 (U303) and TPS564247 (U105) report input_rail and fb_net but no output_rail -- LDOs do have output_rail
  (signal_analysis.power_regulators)

### Missed
(none)

### Suggestions
- Switching regulators should trace output rail from inductor/output cap connections
- ISOW77xx and ISO16xx should be recognized as isolation components

---
