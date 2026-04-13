# Findings: Bastardkb/dactyl-pcb-single-col / single-col

## FND-00002325: Key matrix (6x1) and SK6812MINI LED chain (6 LEDs) correctly detected; Bus topology reports 'row' signal width=18 instead of 6 (counts label instances, not unique signals)

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: schematic_dactyl-pcb-single-col_single-col_single-col.kicad_sch.json
- **Created**: 2026-03-24

### Correct
- The key_matrices detector correctly found a 6-row x 1-column matrix with 6 switches and 6 diodes using net_name detection (row1..row6, col0). The addressable_led_chains detector correctly identified 6 SK6812MINI LEDs (D7-D12) as a WS2812-protocol chain with Din/Dout signal flow and correctly estimated 360mA current draw.

### Incorrect
- The bus_topology.detected_bus_signals reports {prefix: 'row', width: 18, range: 'row1..row6'}. There are only 6 unique row signals (row1 through row6), but each global_label appears 3 times in the schematic (once per sheet group), giving 18 label instances. The width field is counting label occurrences rather than unique signal names. The correct width should be 6. This would mislead a user into thinking there is an 18-bit bus when only 6 unique row signals exist.
  (bus_topology)

### Missed
(none)

### Suggestions
(none)

---

## FND-00002326: DFM correctly flags advanced-process requirement for 0.1mm annular ring

- **Status**: new
- **Analyzer**: pcb
- **Source**: pcb_dactyl-pcb-single-col_single-col_single-col.kicad_pcb.json
- **Created**: 2026-03-24

### Correct
- The PCB uses 0.1mm annular rings (min_annular_ring_mm=0.1) which correctly triggers a DFM tier upgrade to 'advanced'. The standard limit is 0.125mm and advanced is 0.1mm. This is appropriate for this thin keyboard column PCB (17mm wide) where tight tolerances are expected.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
