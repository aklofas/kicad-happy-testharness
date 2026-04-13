# Findings: polykit/kosmo-sidechain / kosmo-sidechain

## FND-00002374: Precision rectifier/envelope detector circuit not detected; Vactrol (VTL5C optocoupler) not detected as isolation barrier; TL074 quad op-amp correctly identified with all 4 functional units analyze...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: schematic_kosmo-sidechain_kosmo-sidechain.kicad_sch.json.json
- **Created**: 2026-03-24

### Correct
- The analyzer correctly processes all 5 schematic symbols for U1 (4 op-amp units + 1 power unit) and deduplicates them to a single BOM line with quantity 1. Op-amp configurations for units 1 and 4 are correctly identified as inverting amplifiers with accurate gain calculations (-10.0 and -2.128 respectively).

### Incorrect
(none)

### Missed
- U1 unit 2 (TL074) with D1/D2 in the feedback loop forms a precision half-wave rectifier — a classic op-amp envelope detector for sidechain compression. The output feeds an RC integrator (R5/C1) on U1 unit 3's non-inverting input. The analyzer classifies both units as 'comparator_or_open_loop' because the diodes in the feedback path prevent it from resolving the feedback resistor topology, but the actual function is a precision rectifier + peak/envelope detector. This is a meaningful missed detection for an audio effects board.
  (signal_analysis)
- U2 is a VTL5C Vactrol — an optocoupler combining an LED with a light-dependent resistor used for voltage-controlled gain in the sidechain compressor. Its lib_id is 'Isolator:VTL5C', clearly in the Isolator library, yet signal_analysis.isolation_barriers is empty. The analyzer should recognize Isolator-library components as isolation barriers.
  (signal_analysis)

### Suggestions
(none)

---
