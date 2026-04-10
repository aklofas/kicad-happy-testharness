# Findings: Eurorack_KiCAD_templates / Connector_panels_12HP_Connector_panel_100mm_12HP_Connector_panel_100mm

## FND-00000548: file_version reported as '4' but source header says 'EESchema Schematic File Version 2'; Empty schematic correctly produces zero components, nets, and signals

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: Connector_panels_12HP_Connector_panel_12HP_Connector_panel.sch.json
- **Created**: 2026-03-23

### Correct
- The .sch file contains only a header and no component or wire records. The analyzer correctly reports total_components=0, total_nets=0, total_wires=0, and empty signal_analysis sections.

### Incorrect
- The .sch header line reads 'EESchema Schematic File Version 2', but the analyzer outputs file_version: '4'. The file is otherwise empty (no components), so this is a minor metadata error with no functional impact.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00000549: Component extraction correct: J1 (2x5 IDC connector), D1 and D2 (Schottky diodes) all parsed accurately; Reverse-polarity protection circuit (D1+D2 Schottky on ±12V rails) not detected in protectio...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: Main_board_12HP_Main_board_12HP_Main_board.sch.json
- **Created**: 2026-03-23

### Correct
- Correct counts (3 components, 2 unique parts), correct lib_ids, footprints, and BOM grouping. Power rails +12V, -12V, GND all identified. Net connectivity matches schematic wiring.
- net_classification correctly assigns 'power' to +12V and -12V, 'ground' to GND, and 'signal' to the two unnamed connector-to-diode intermediate nets.
- None of the components carry MPN/manufacturer fields. The analyzer correctly lists all three in missing_mpn while not including the power symbols (#PWR*), which is the expected behavior.

### Incorrect
(none)

### Missed
- D1 protects the +12V rail and D2 protects the -12V rail using series Schottky diodes — a textbook Eurorack reverse-polarity protection topology. The analyzer's protection_devices list is empty and design_observations is empty. This pattern (diode in series between IDC connector pin and named power rail) should be recognizable as protection.
  (signal_analysis)

### Suggestions
(none)

---
