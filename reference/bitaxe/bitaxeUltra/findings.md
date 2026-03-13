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

## FND-00000034: PARTNO property not mapped to MPN field

- **Status**: new
- **Analyzer**: schematic
- **Source**: bitaxeUltra.kicad_sch.json
- **Created**: 2026-03-13

### Correct
(none)

### Incorrect
- All 29 components have PARTNO custom property but mpn="" for all. mpn_coverage=0/28.
  (components[*].mpn)

### Missed
(none)

### Suggestions
- Add "PARTNO" to the MPN field alias fallback chain

---

## FND-00000035: 3V3 net classified as "signal" instead of "power"

- **Status**: new
- **Analyzer**: schematic
- **Source**: bitaxeUltra.kicad_sch.json
- **Created**: 2026-03-13

### Correct
(none)

### Incorrect
- power_rails array empty despite multiple power nets. 3V3 net classified as signal instead of power.
  (signal_analysis.power_rails)

### Missed
(none)

### Suggestions
- Ensure net names matching common power patterns (3V3, 5V, VCC, etc.) are classified as power rails

---

## FND-00000036: R4/C35 RC filter false positive (pull-up + decoupling caps)

- **Status**: new
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

## FND-00000037: Cross-domain false "needs_level_shifter" on I2C

- **Status**: new
- **Analyzer**: schematic
- **Source**: bitaxeUltra.kicad_sch.json
- **Created**: 2026-03-13

### Correct
(none)

### Incorrect
- INA260 sense inputs (IN+/IN-) misidentified as power domain, causing false needs_level_shifter flag on I2C bus.
  (signal_analysis.bus_protocols)

### Missed
(none)

### Suggestions
- Do not classify analog sense inputs (IN+/IN-) as power domain indicators

---

## FND-00000038: 5V hierarchical label marked as unconnected

- **Status**: new
- **Analyzer**: schematic
- **Source**: bitaxeUltra.kicad_sch.json
- **Created**: 2026-03-13

### Correct
(none)

### Incorrect
- 5V hlabel on same wire as VIN_M label but not merged. 5V hierarchical label reported as unconnected.
  (unconnected_pins)

### Missed
(none)

### Suggestions
- Merge hierarchical labels on the same wire segment when resolving connectivity

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

## FND-00000041: has_datasheet=false despite URL present for Q1/Q2

- **Status**: new
- **Analyzer**: schematic
- **Source**: bitaxeUltra.kicad_sch.json
- **Created**: 2026-03-13

### Correct
(none)

### Incorrect
- Q1/Q2 CSD17311Q5 have datasheet URL in schematic properties but has_datasheet=false in output.
  (components[*].has_datasheet)

### Missed
(none)

### Suggestions
- Check datasheet property extraction for components with hidden pins

---

## FND-00000042: Garbled pin order string in generic symbol warning

- **Status**: new
- **Analyzer**: schematic
- **Source**: bitaxeUltra.kicad_sch.json
- **Created**: 2026-03-13

### Correct
(none)

### Incorrect
- Generic symbol warning contains garbled pin order string.
  (warnings)

### Missed
(none)

### Suggestions
- Review pin order string generation for generic symbols

---
