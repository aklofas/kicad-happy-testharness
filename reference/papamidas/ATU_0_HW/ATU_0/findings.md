# Findings: papamidas/ATU_0_HW / ATU_0

## FND-00000353: RL* relay components misclassified as resistors; relay type missing entirely from statistics; relay type absent from component_types statistics in all three output files

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: ATU_0.sch.json
- **Created**: 2026-03-23

### Correct
- 18 relay components (RL1-RL18, value=HFD2-L2, lib=ATU_0-rescue:HFD2-L2-flipdotUSV-cache) are all typed 'resistor' instead of 'relay'. The classify_component function extracts prefix 'RL', finds no 'RL' entry in type_map, then falls through to single-char fallback: prefix[0]='R' → 'resistor'. The fix is to add 'RL' to type_map as 'relay'. Impact: statistics.component_types reports resistor=39 (should be 21 resistors + 18 relays); relay type is absent from statistics entirely. The relay misclassification also prevents any relay-aware signal-path analysis (e.g., switched RF network detection).

### Incorrect
(none)

### Missed
- All 18 HFD2-L2 relay components (RL1-RL18) are present in the design but the 'relay' key never appears in statistics.component_types across any of the three output files. The correct count is relay=18 in ATU_0.sch (hierarchical), relay=8 in Csektion.sch, relay=8 in Lsektion.sch. This is a direct consequence of the RL-prefix misclassification bug in classify_component (kicad_utils.py): 'RL' is not in type_map so it falls back to 'R' → 'resistor'.
  (statistics)

### Suggestions
(none)

---

## FND-00000354: RL* relay components misclassified as resistors in Csektion (capacitor-switching section)

- **Status**: new
- **Analyzer**: schematic
- **Source**: Csektion.sch.json
- **Created**: 2026-03-23

### Correct
- 8 relay components (RL11-RL18, value=HFD2-L2) are typed 'resistor' instead of 'relay'. statistics.component_types shows resistor=16 (should be 8 real R* resistors + 8 relays separately). Same root cause as ATU_0.sch: 'RL' prefix not in type_map, falls back to single-char 'R' → 'resistor'.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00000355: RL* relay components misclassified as resistors in Lsektion (inductor-switching section); resistor count inflated from 0 to 8

- **Status**: new
- **Analyzer**: schematic
- **Source**: Lsektion.sch.json
- **Created**: 2026-03-23

### Correct
- 8 relay components (RL3-RL10, value=HFD2-L2) are typed 'resistor' instead of 'relay'. Lsektion contains zero real resistors (no R* components), so the correct resistor count is 0. The output reports resistor=8, which is entirely due to the RL prefix falling through to single-char 'R' → 'resistor' in classify_component. The relay type is absent from statistics.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
