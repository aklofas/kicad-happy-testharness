# Findings: siderakb/ergo-snm-keyboard / ErgoSNM_Keyboard_rev1_ErgoSNM_keyboard

## FND-00002185: Bus width counts label instances instead of unique signal names, systematically overcounting; Key matrix correctly detected in rev1 flat schematic (5 rows x 7 cols, 35 keys with 35 diodes)

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: ErgoSNM_Keyboard_rev1_ErgoSNM_keyboard.kicad_sch.json
- **Created**: 2026-03-24

### Correct
- The rev1 flat schematic (no hierarchy, no MCU on-sheet, uses Pro Micro connectors J5/J6) correctly detects the 5x7 key matrix with ROW_0..ROW_4 and COL_0..COL_6, counting exactly 35 switch and 35 diode components all on the matrix. The 4 PWR_FLAG warnings (VCC, GND, VBUS, +BATT have no PWR_FLAG or power_out driver) are accurate—rev1 uses Pro Micro connectors without explicit power flags. The 17 label_shape_warnings for ROW/COL global labels shaped as 'input' with no driver are correctly flagged since the MCU is external.

### Incorrect
- The bus_topology 'width' field reports the total number of label placements on the sheet rather than the number of unique signal names. In the rev1 schematic, COL_0..COL_6 (7 unique nets) produces width=18 because each global label appears 2-3 times in the schematic. Similarly, ROW_0..ROW_4 (5 unique nets) gives width=20. This is a bug in analyze_bus_topology() at line 4109: `'width': len(members)` where 'members' is the un-deduplicated list of label occurrences. The fix is `len(set(members))` or deduplication before counting.
  (bus_topology)

### Missed
(none)

### Suggestions
(none)

---
