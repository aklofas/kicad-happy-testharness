# Findings: cubesat-boards / ykts-payload_ykts-payload

## FND-00000281: CubeSat payload board (155 components). RC filter double-counting on shared capacitors (C14, C29). MAX4372FEUK current sense amplifier with 0.1ohm shunt not detected.

- **Status**: confirmed
- **Analyzer**: schematic
- **Source**: ykts-payload_ykts-payload.kicad_sch.json
- **Created**: 2026-03-16

### Correct
- 4 voltage dividers as 4.7K/10K SPI level shifters for AT25DF161 flash correctly identified
- 4 crystal circuits (Y1/Y3 8MHz, Y2/Y4 12MHz) with 22pF load caps correct
- 3 power regulators (AMS1117-5.0, dual L78L33) correctly identified
- PMOS Q1 PMV65XP high-side switch correctly identified

### Incorrect
- RC filter double-counting: C14 appears in two entries (R30+C14 and R29+C14) — only R30+C14 is a genuine power-on reset filter; R29 shares the same cap node
  (signal_analysis.rc_filters)
- Same double-counting for C29 (R48+C29 and R47+C29)
  (signal_analysis.rc_filters)

### Missed
- MAX4372FEUK (U4) current sense amplifier with R_CSB1 (0.1ohm shunt) on +5V rail not detected in current_sense
  (signal_analysis.current_sense)

### Suggestions
- RC filter detector should deduplicate entries sharing the same capacitor
- Detect MAX4372 and similar current sense ICs by lib_id pattern with low-value shunt resistors on RS+/RS- pins

---
