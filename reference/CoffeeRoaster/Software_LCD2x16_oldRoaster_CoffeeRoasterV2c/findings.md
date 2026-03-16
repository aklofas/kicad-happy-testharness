# Findings: CoffeeRoaster / Software_LCD2x16_oldRoaster_CoffeeRoasterV2c

## FND-00000217: CoffeeRoaster V2 board (22 components). False positive: 2 RC filters detected where R1/R2 and C1/C2 are not connected as RC networks (R1+R2 are part of a resistor junction, C1+C2 are switch debounce caps). False negative: voltage divider R3(18K)+R4(5.693K) on analog input A0 not detected. Schematic has duplicate R3 reference designator (design error).

- **Status**: confirmed
- **Analyzer**: schematic
- **Source**: Software_LCD2x16_oldRoaster_CoffeeRoasterV2.kicad_sch.json
- **Created**: 2026-03-16

### Correct
- Component counts and BOM values correctly extracted

### Incorrect
- 2 RC filters (R2+C2, R1+C1) detected as false positives - R1/R2 connect to a resistor junction at __unnamed_35, while C1/C2 are switch debounce capacitors. These components are not wired as RC filter networks.
  (signal_analysis.rc_filters)
- RC filter output and ground nodes reported as the same net (__unnamed_35), which is logically impossible for a filter
  (signal_analysis.rc_filters)

### Missed
- Voltage divider R3(18K) + R4(5.693K) on Arduino analog input A0 not detected, possibly due to duplicate R3 reference designator confusing component matching
  (signal_analysis.voltage_dividers)

### Suggestions
- RC filter detection should verify that R and C share a connected node and that output != ground
- Flag duplicate reference designators as schematic quality warning
- Voltage divider detection should handle schematics with duplicate reference designators

---
