# Findings: diode-rom / diode-rom-16_diode-rom-16

## FND-00002329: bus_topology 'width' field reports bus entry count (84 total) instead of signal count per bus; False positive pwr_flag_warnings: PWR_FLAG symbols are present but analyzer fails to resolve their net...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: schematic_diode-rom_diode-rom-16_diode-rom-16.kicad_sch.json
- **Created**: 2026-03-24

### Correct
- The design implements a 16-byte diode ROM (128 positions in an 8x16 grid) using 1N4148 diodes placed but marked DNP (do not populate). The analyzer correctly reports 128 DNP diodes and 5 non-DNP components (U1/U2 74HC238 3-to-8 decoders, U3 74HC245 bus transceiver, J1 14-pin connector, RN1 resistor network). The BOM correctly groups all 128 1N4148 diodes with dnp=true.
- The design_observations section correctly identifies that U1 (74HC238), U2 (74HC238), and U3 (74HC245) all lack bypass capacitors on the +5V rail. There are no capacitor components anywhere in the schematic BOM (no C* references), confirming the observation is accurate. This is a genuine design oversight in the diode ROM schematic.

### Incorrect
- The detected_bus_signals reports A: width=12 (range A0..A3), B: width=32 (range B0..B15), C: width=24 (range C0..C7), D: width=16 (range D0..D7). Summing these widths gives 84 which equals bus_entry_count=84. The actual signal widths are A=4, B=16, C=8, D=8. The 'width' field is counting how many bus wire entries connect to the bus, not the number of unique signals — this is a misleading and incorrect metric. A 16-wide bus with 2 entry points per signal gets reported as width=32.
  (bus_topology)
- pwr_flag_warnings fires for both +5V and GND claiming no PWR_FLAG is present. However, the schematic contains two power:PWR_FLAG instances (#FLG01 and #FLG02). Inspecting the source file confirms #FLG02 is placed at the same coordinate (55.88, 40.64) as a GND power symbol, and #FLG01 is placed on the +5V net. The PWR_FLAG net appears as an isolated net with no connected pins in the output, meaning the analyzer is failing to resolve the PWR_FLAG symbols onto their host nets. This is a net connectivity resolution bug.
  (pwr_flag_warnings)

### Missed
(none)

### Suggestions
(none)

---

## FND-00002330: False positive gerber alignment warning for copper layers being smaller than board outline

- **Status**: promoted
- **Analyzer**: gerber
- **Source**: gerber_diode-rom_diode-rom-16_gerber.json
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
- The alignment check reports 'aligned: false' because copper layers (F.Cu/B.Cu) span 58.42mm wide while Edge.Cuts spans 66.04mm, flagging a 7.6mm width variation as an issue. This is a normal PCB design pattern where component placement and routing do not extend to the board edge — the ~4mm margin on each side is standard design practice, not a manufacturing defect. The analyzer should not flag this as a misalignment; it should only flag cases where copper/features extend beyond the board outline.
  (alignment)

### Missed
(none)

### Suggestions
(none)

---
