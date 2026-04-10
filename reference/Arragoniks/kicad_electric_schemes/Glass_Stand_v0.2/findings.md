# Findings: kicad_electric_schemes / Glass_Stand_v0.2_Glass_Stand_v0.2

## FND-00002357: total_components reports 12 but 42 components are present in the components list

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: schematic_kicad_electric_schemes_Glass_Stand_v0.2_Glass_Stand_v0.2.kicad_sch.json
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
- statistics.total_components=12 and component_types shows 7 entries (ic:2, transistor:1, resistor:2, etc.) but the components array contains 42 entries with actual counts ic:6, transistor:5, resistor:13, capacitor:7, connector:7, diode:3, switch:1. This is the same deduplication-by-reference-prefix bug seen in dev_f070: unresolved references like 'U?', 'Q?', 'R?' are each counted once regardless of how many instances exist. Partially-annotated components like 'C4', 'C5', 'R11', 'U1' are also present, making the undercounting inconsistent.
  (components)

### Missed
(none)

### Suggestions
(none)

---

## FND-00002358: Correctly returns empty PCB analysis for an empty .kicad_pcb stub (no footprints, no routing)

- **Status**: new
- **Analyzer**: pcb
- **Source**: pcb_kicad_electric_schemes_Glass_Stand_v0.2_Glass_Stand_v0.2.kicad_pcb.json
- **Created**: 2026-03-24

### Correct
- The Glass_Stand_v0.2.kicad_pcb file is a 1900-byte stub with no footprints. The analyzer correctly returns footprint_count=0, track_segments=0, copper_layers_used=0, routing_complete=true (vacuously). The copper_presence warning ('No filled polygon data') is appropriate. The PCB analysis does not crash on this minimal file.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00002359: No power rails detected on a 220V AC mains power supply schematic

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: schematic_kicad_electric_schemes_Reverse_Brother_Power-v1.0_2015-03-14_Reverse_Brother_Power-v1.0_2015-03-14.kicad_sch.json
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
(none)

### Missed
- The design is a 220VAC switched-mode power supply (J1 labeled '220~', with transformer T1, rectifier diodes, filter caps, and transistor switches). statistics.power_rails=[] and all 18 nets are unnamed (__unnamed_0 through __unnamed_17). The schematic does not use KiCad power symbols (PWR_FLAG, GND, VCC, etc.) — it uses direct wire connections only. Since the power rail detector relies on KiCad power symbols rather than inferred topology, no rails are found. The analyzer could potentially identify AC_LINE and rectified DC rails from the transformer/rectifier topology but does not attempt this.
  (statistics)

### Suggestions
(none)

---

## FND-00002360: Correctly analyzes minimal RC circuit with 3 components and no power symbols

- **Status**: new
- **Analyzer**: schematic
- **Source**: schematic_kicad_electric_schemes_Proj_1_Proj_1.kicad_sch.json
- **Created**: 2026-03-24

### Correct
- Proj_1 is a trivial schematic with 2 resistors and 1 capacitor. total_components=3 matches the actual component list length of 3 — accurate because these components have unique annotated references (R1, R2, C1). power_rails=[] is correct since no power symbols are present. The component_types breakdown (resistor:2, capacitor:1) is accurate.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
