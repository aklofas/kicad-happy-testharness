# Findings: bitaxe / bitaxeUltra

## FND-00000033: Q1/Q2 CSD17311Q5 MOSFETs completely missing from all nets

- **Status**: new
- **Analyzer**: schematic
- **Source**: bitaxeUltra.kicad_sch.json
- **Created**: 2026-03-13

### Correct
(none)

### Incorrect
- Hidden pins (pins 1,2 marked hide) likely cause wire-to-pin matching failure. Zero net connections for both Q1 and Q2 CSD17311Q5 transistors.
  (nets)

### Missed
(none)

### Suggestions
- Ensure hidden pins are still matched to wires/nets during connectivity analysis

---

## FND-00000036: R4/C35 RC filter false positive (pull-up + decoupling caps)

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: bitaxeUltra.kicad_sch.json
- **Related**: KH-019
- **Created**: 2026-03-13

### Correct
(none)

### Incorrect
- R4 is PGOOD pull-up, C35/C44 are decoupling caps. Falsely detected as RC filter.
  (signal_analysis.rc_filters)

### Missed
(none)

### Suggestions
- Exclude pull-up resistors paired with decoupling caps from RC filter detection

---

## FND-00000039: R13/C45 RC filter wrong ground_net (reports VOUT)

- **Status**: new
- **Analyzer**: schematic
- **Source**: bitaxeUltra.kicad_sch.json
- **Related**: KH-019
- **Created**: 2026-03-13

### Correct
(none)

### Incorrect
- R13/C45 RC filter reports ground_net as VOUT instead of actual ground net.
  (signal_analysis.rc_filters)

### Missed
(none)

### Suggestions
- Verify ground_net assignment in RC filter detection logic

---

## FND-00000040: R4 pull-up classified as "series" resistor

- **Status**: new
- **Analyzer**: schematic
- **Source**: bitaxeUltra.kicad_sch.json
- **Created**: 2026-03-13

### Correct
(none)

### Incorrect
- R4 is a pull-up resistor on PGOOD but classified as series resistor.
  (signal_analysis)

### Missed
(none)

### Suggestions
- Distinguish pull-up/pull-down resistors from series resistors by checking if one terminal is on a power rail

---

## FND-00000298: Gerber review: 4-layer BGA ASIC miner. TD clearing bug, front/back count wrong, smd_apertures misleading

- **Status**: new
- **Analyzer**: gerber
- **Source**: Manufacturing Files/gerbers/
- **Related**: KH-177, KH-182, KH-185
- **Created**: 2026-03-18

### Correct
- Layer completeness, alignment, board dimensions (56.5x99.8mm) all accurate for 4-layer KiCad 7 output
- Via drill classification exact: 201 vias across 3 tool sizes

### Incorrect
- %TD*% does not reset current_component -- J2 inflated to 203 pads because subsequent inner layer flashes still attributed to it
  (component_analysis)
- front_side=0, back_side=1 wrong (actual ~117 front, ~20 back). Wrong data source for side assignment
  (component_analysis)
- smd_apertures=0 and smd_ratio misleading -- counts unique aperture defs not instances. Board is SMD-dominant
  (pad_summary)

### Missed
(none)

### Suggestions
- Fix %TD*% to clear current_component/current_net per Gerber X2 spec

---
