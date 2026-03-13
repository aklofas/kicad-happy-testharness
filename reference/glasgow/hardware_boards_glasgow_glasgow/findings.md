# Findings: glasgow / hardware_boards_glasgow_glasgow

## FND-00000001: current_sense detector produces 68 false positives in glasgow.kicad_sch by pairing R49 (0.15 ohm shunt) with every IC sharing GND net

- **Status**: confirmed
- **Analyzer**: schematic
- **Source**: hardware_boards_glasgow_glasgow.kicad_sch.json
- **Related**: KH-007
- **Created**: 2026-03-13

### Correct
- R49 (0R15) + INA233 current sense IC is correctly detected

### Incorrect
- 67 of 68 current_sense detections are false positives — R49 paired with unrelated ICs (SN74LVC1T45, CAT24M01X, etc.) that merely share GND net
  (signal_analysis.current_sense)

### Missed
(none)

### Suggestions
- Detector should require shunt resistor to be in series path (not shunt to GND) or check sense IC has current sense pins (INP/INM)

---

## FND-00000006: Voltage divider false positives: R30/R48 and R56/R48 on ISNS_H net are current sense network components, not dividers. R5/R4 on ~{CY_RESET} is a pull-up/pull-down pair, not a sensing divider.

- **Status**: confirmed
- **Analyzer**: schematic
- **Source**: hardware_boards_glasgow_glasgow.kicad_sch.json
- **Related**: KH-012
- **Created**: 2026-03-13

### Correct
- R33/R28 (49k9/59k) feedback divider for VDAC→VFB correctly detected with is_feedback=True
- R34/R35 on VIO→VFB also appears to be a legitimate feedback divider

### Incorrect
- R30 (4R7) / R48 (0R15) on ISNS_H → GND detected as divider but these are current sense shunt resistors
  (signal_analysis.voltage_dividers)
- R56 (0R33) / R48 (0R15) on ISNS_H → GND same issue — current sense, not divider
  (signal_analysis.voltage_dividers)
- R5/R4 (100k/100k) on ~{CY_RESET} → GND is a pull-up/pull-down pair on a digital reset line, not a voltage sensing divider
  (signal_analysis.voltage_dividers)

### Missed
(none)

### Suggestions
- Filter out sub-1-ohm resistor pairs (these are current sense). Filter out equal-value resistor pairs on digital signal names. Require mid-point connection to an analog input or feedback pin.

---

## FND-00000017: Glasgow has 52 power symbols resolved with net_name +3V3 but +3V3 does not appear in the nets dictionary. Power symbol names may not be propagating correctly to the net builder for this specific rail.

- **Status**: new
- **Analyzer**: schematic
- **Source**: hardware_boards_glasgow_glasgow.kicad_sch.json
- **Created**: 2026-03-13

### Correct
(none)

### Incorrect
(none)

### Missed
- +3V3 power rail with 52 power symbols not appearing in nets dict — net builder may not be consolidating power symbol nets correctly for all rails
  (nets)

### Suggestions
- Investigate why +3V3 power symbols are not creating/joining a net in build_net_map(). May be a coordinate matching issue or power symbol resolution problem.

---

## FND-00000018: CRITICAL: +3V3 power rail completely missing from nets dict despite 52 power symbols in main sheet + 33 in io_banks (85 total). GND (133 symbols), +5V (10), +1V2 (5) all work correctly. This means ALL +3V3 connections are invisible — signal analysis for anything on the 3.3V rail will fail.

- **Status**: confirmed
- **Analyzer**: schematic
- **Source**: hardware_boards_glasgow_glasgow.kicad_sch.json
- **Related**: NEW - not yet in issue tracker
- **Created**: 2026-03-13

### Correct
- GND, +5V, +1V2, VCCPLL0, VCCPLL1, GNDPLL0, GNDPLL1 all correctly appear in nets

### Incorrect
(none)

### Missed
- +3V3 power rail with 85 power symbols across 2 sheets not present in nets dict at all. Every component powered by +3V3 has a dangling power pin.
  (nets)

### Suggestions
- Debug build_net_map() for +3V3 specifically. May be a naming collision, coordinate issue, or power symbol lib_id resolution problem. Check if +3V3 power symbols have correct pin positions.

---

## FND-00000025: 73 capacitors with value "u1" (European notation for 0.1uF) have no parsed_value. Parser handles "4u7" but fails when unit prefix precedes digit.

- **Status**: confirmed
- **Analyzer**: schematic
- **Source**: hardware_boards_glasgow_glasgow.kicad_sch.json
- **Created**: 2026-03-13

### Correct
(none)

### Incorrect
(none)

### Missed
- "u1" = 0.1uF not parsed. Pattern: unit prefix before digit (u1, n47, p33). Parser only handles digit-first like "4u7".
  (components[*].parsed_value)

### Suggestions
- Add parsing for prefix-first notation: u1=0.1u, n47=0.47n, p33=0.33p

---
