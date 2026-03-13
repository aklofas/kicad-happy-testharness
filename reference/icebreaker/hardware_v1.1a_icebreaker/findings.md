# Findings: icebreaker / hardware_v1.1a_icebreaker

## FND-00000043: Ferrite bead value "600" parsed as 600 Henries

- **Status**: new
- **Analyzer**: schematic
- **Source**: hardware_v1.1a_icebreaker.kicad_sch.json
- **Created**: 2026-03-13

### Correct
(none)

### Incorrect
- L1/L2 are 600-ohm ferrite beads in 0402. LC filter shows resonant_hz=2.97 and henries=600.0. Physically impossible — ferrite beads are rated in ohms at frequency, not henries.
  (signal_analysis.lc_filters)

### Missed
(none)

### Suggestions
- Detect ferrite beads by library name or impedance-rated value format. Do not parse bare numeric inductor values as henries when the component is a ferrite bead.

---

## FND-00000044: FT2232H internal 1.8V LDO not detected as power regulator

- **Status**: new
- **Analyzer**: schematic
- **Source**: hardware_v1.1a_icebreaker.kicad_sch.json
- **Created**: 2026-03-13

### Correct
(none)

### Incorrect
(none)

### Missed
- VREGOUT pin 49 of FT2232H drives +1V8 rail via internal LDO. Only dedicated VREG components are detected as power regulators.
  (signal_analysis.power_regulators)

### Suggestions
- Detect VREGOUT/VREG pins on ICs as internal power regulators driving rails

---

## FND-00000045: Crystal/oscillator circuit not detected

- **Status**: new
- **Analyzer**: schematic
- **Source**: hardware_v1.1a_icebreaker.kicad_sch.json
- **Created**: 2026-03-13

### Correct
(none)

### Incorrect
(none)

### Missed
- U7 is 12MHz SiT2001 MEMS oscillator. crystal_circuits=[]. Active oscillators not detected, only passive crystal circuits.
  (signal_analysis.crystal_circuits)

### Suggestions
- Add detection for active oscillator components (SiT, MEMS, TCXO) in addition to passive crystals

---

## FND-00000046: 93C46B EEPROM missed in memory_interfaces

- **Status**: new
- **Analyzer**: schematic
- **Source**: hardware_v1.1a_icebreaker.kicad_sch.json
- **Created**: 2026-03-13

### Correct
(none)

### Incorrect
(none)

### Missed
- U1 is a 93C46B EEPROM in pkl_memory library but not detected in memory_interfaces.
  (signal_analysis.memory_interfaces)

### Suggestions
- Detect EEPROM components by library name (memory/EEPROM keywords) or part number patterns

---

## FND-00000047: RC filter on LDO enable is soft-start delay, not signal filter

- **Status**: new
- **Analyzer**: schematic
- **Source**: hardware_v1.1a_icebreaker.kicad_sch.json
- **Related**: KH-019
- **Created**: 2026-03-13

### Correct
(none)

### Incorrect
- R3=10k + C39=1u on U2 EN pin detected as RC filter. This is a soft-start delay circuit for an LDO enable pin, not a signal filter.
  (signal_analysis.rc_filters)

### Missed
(none)

### Suggestions
- Recognize RC circuits on regulator enable pins as soft-start/delay circuits rather than signal filters

---

## FND-00000048: Multi-unit resistor array parts duplicated in components list

- **Status**: new
- **Analyzer**: schematic
- **Source**: hardware_v1.1a_icebreaker.kicad_sch.json
- **Created**: 2026-03-13

### Correct
(none)

### Incorrect
- 164 entries in components list vs 135 unique refs. Multi-unit resistor array parts are listed once per unit instead of once per component.
  (components)

### Missed
(none)

### Suggestions
- Deduplicate multi-unit components in the components list, or clearly mark unit numbers

---
