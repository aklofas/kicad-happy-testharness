# Findings: OpenMower / Hardware_OpenMowerMainboard_OpenMowerMainboard

## FND-00000002: MAX20405AFOF_VY+T (synchronous buck converter) classified as LDO in dcdc.kicad_sch

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: Hardware_OpenMowerMainboard_dcdc.kicad_sch.json
- **Related**: KH-008
- **Created**: 2026-03-13

### Correct
- IC3 (MAX20405) correctly identified as a power regulator with +5V output

### Incorrect
- MAX20405 classified with topology=LDO but is actually a synchronous buck converter. Has inductor L1 + bootstrap cap C15 which are hallmarks of switching topology.
  (signal_analysis.power_regulators)

### Missed
(none)

### Suggestions
- Check for inductor on output (buck indicator), BST/BOOT pins (bootstrap = switching), and IC keywords like buck/switching/step-down

---

## FND-00000004: pwr_flag_warnings generated for sub-sheets where power rail source is on a different sheet (29 warnings across OpenMower, 37 in cynthion, 9 in education_tools, 6 in glasgow)

- **Status**: confirmed
- **Analyzer**: schematic
- **Source**: Hardware_OpenMowerMainboard_OpenMowerMainboard.kicad_sch.json
- **Related**: KH-010
- **Created**: 2026-03-13

### Correct
- Technically correct: each sub-sheet individually lacks power_out or PWR_FLAG on those rails

### Incorrect
(none)

### Missed
(none)

### Suggestions
- Cross-reference hierarchically: if a power net has power_out/PWR_FLAG on ANY sheet in the design, suppress the warning on other sheets. Or mark these as informational rather than warnings.

---

## FND-00000005: OpenMower uses property name "Digikey" (capital D, lowercase k) with 200 occurrences. get_property() does exact case match so "DigiKey" in the fallback chain misses "Digikey".

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: Hardware_OpenMowerMainboard_dcdc.kicad_sch.json
- **Related**: KH-011
- **Created**: 2026-03-13

### Correct
(none)

### Incorrect
(none)

### Missed
- digikey field is empty for all OpenMower components despite source having "Digikey" property with valid PNs (e.g. "1276-1935-1-ND")
  (components[*].digikey)

### Suggestions
- Add "Digikey" (exact case) to the fallback chain in analyze_schematic.py line 372-376, or make get_property() case-insensitive for distributor fields

---

## FND-00000009: R5/R4 ratio=0.985 on RASPI_FAN_ON detected as voltage divider — this is a pull-up/pull-down on a digital GPIO signal, not a sensing divider

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: Hardware_OpenMowerMainboard_RaspberryPi.kicad_sch.json
- **Related**: KH-012
- **Created**: 2026-03-13

### Correct
(none)

### Incorrect
- R5/R4 with ratio=0.985 on RASPI_FAN_ON. The near-unity ratio and digital signal name indicate pull-up/pull-down, not a voltage divider for sensing.
  (signal_analysis.voltage_dividers)

### Missed
(none)

### Suggestions
- Ratios very close to 0 or 1 (e.g. >0.95) often indicate pull-up/pull-down pairs, not dividers

---

## FND-00000010: Unused opamp units 3 and 4 of U2 (MCP604) incorrectly assigned input_resistor R49

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: Hardware_OpenMowerMainboard_opamps.kicad_sch.json
- **Created**: 2026-03-13

### Correct
- U2 units 3 and 4 correctly identified as comparator_or_open_loop with both inputs at GND

### Incorrect
- Units 3 and 4 have input_resistor={ref:R49, ohms:4700}. R49 is part of the R48/R49 voltage divider feeding unit 2's inverting input. The analyzer erroneously associates R49 as an input resistor for these unused units because R49 has one terminal on GND, which is the same net as these units' inputs.
  (signal_analysis.opamp_circuits)

### Missed
(none)

### Suggestions
- When an opamp's inputs are tied directly to GND/VCC (unused unit), do not search for input resistors on those power nets

---

## FND-00000012: R11/R12 feedback network for MAX20405 buck converter classified as voltage_divider but missed as feedback_network

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: Hardware_OpenMowerMainboard_dcdc.kicad_sch.json
- **Created**: 2026-03-13

### Correct
- R11 (53k6) / R12 (10k) correctly identified as a voltage divider with ratio 0.157 from +5V to GND, midpoint to JP5

### Incorrect
(none)

### Missed
- R11/R12 form the output voltage feedback divider for IC3 (MAX20405 buck converter). The midpoint connects through JP5 to the FB pin of IC3. This should be detected as a feedback_network in addition to being a voltage_divider.
  (signal_analysis.feedback_networks)

### Suggestions
- When a voltage divider's midpoint connects to a regulator IC's feedback pin (FB, VSEN, ADJ), also classify it as a feedback_network

---

## FND-00000014: BSS138 level shifters Q13-Q16 not recognized as level_shifter topology

- **Status**: confirmed
- **Analyzer**: schematic
- **Source**: Hardware_OpenMowerMainboard_RobotConnectors.kicad_sch.json
- **Created**: 2026-03-13

### Correct
- Q13-Q16 correctly identified as NMOS transistor circuits with gate=+3V3, drain=SIGNAL_HV, source=SIGNAL_LV

### Incorrect
(none)

### Missed
(none)

### Suggestions
- Add level_shifter detection: NMOS with gate=power_rail, source on one signal domain, drain on another, with pull-up resistors on both sides

---
