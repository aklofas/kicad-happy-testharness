# Findings: cnlohr/cnhardware / ch32v307gigabittest_ch32v307gigabit

## FND-00000160: CH32V307 Gigabit Ethernet test board with RTL8211E PHY. Ethernet interface not detected; gigabit magnetics transformer U4 classified as IC despite 'Transformer' in lib_id; unannotated components silently dropped.

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: ch32v307gigabittest_ch32v307gigabit.kicad_sch.json
- **Related**: KH-079
- **Created**: 2026-03-15

### Correct
(none)

### Incorrect
- U4 with lib_id 'G2406S-Gigabit-Magnetics-Transformer' classified as IC -- 'Transformer' literally in lib_id but U prefix wins
  (statistics.component_types)

### Missed
- Ethernet interface not detected -- RTL8211E PHY + G2406S magnetics + 8P8C RJ45 with GMII bus nets all present
  (signal_analysis.ethernet_interfaces)

### Suggestions
- Lib_id keywords should have higher priority than ref prefix for classification
- Unannotated components should be included in output or flagged in annotation_issues

---
