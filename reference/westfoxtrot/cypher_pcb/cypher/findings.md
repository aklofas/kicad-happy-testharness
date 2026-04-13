# Findings: westfoxtrot/cypher_pcb / cypher

## FND-00000235: Keyboard (324 components). Key matrix diode count mismatch: 88 detected vs 93 in schematic. WS2812B LED chain, LDO, and protection devices all correct.

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: cypher.kicad_sch.json
- **Created**: 2026-03-16

### Correct
- 1 LDO correctly detected
- 5 protection devices correctly detected

### Incorrect
(none)

### Missed
(none)

### Suggestions
- Investigate missing 5 key matrix diodes

---
