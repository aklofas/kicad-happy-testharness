# Findings: nuess0r/ctrl-M / ctrl-m

## FND-00002320: Bus width values are exactly double the actual signal count for all detected buses; Keyboard matrix (R0..R15 rows, C0..C7 columns) not detected as a key_matrix; USB D+/D- differential pair classifi...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: schematic_ctrl-M_ctrl-m.kicad_sch.json.json
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
- The bus_topology detector reports: A8..A10 as width=6 (actual: 3 signals), B13..B15 as width=6 (actual: 3 signals), C0..C7 as width=16 (actual: 8 signals), R0..R15 as width=32 (actual: 16 signals). Every bus width is exactly 2x the correct value. This suggests a bug in the bus width computation — possibly counting bus entries from both ends of a wire or double-counting bidirectional connections.
  (bus_topology)
- The design has a USB_B connector (J1) with net names D+ and D-, and a USBLC6-2SC6 ESD protection IC (U1). The differential_pairs detector classifies this pair as type='differential' rather than type='USB'. Compare with crimpdeq-pcb where nets named USB_D+/USB_D- are correctly classified as type='USB'. The classifier is net-name-sensitive and misses the USB type when net names are simply D+/D- without the 'USB_' prefix, even when a USB connector and ESD IC are present.
  (design_analysis)

### Missed
- This is a Model M keyboard controller. The schematic has 16 row signals (R0..R15) and 8 column signals (C0..C7) connecting STM32F072 GPIO pins to row/column connectors J7 and J8. The bus_topology correctly identifies these as named buses, but signal_analysis.key_matrices returns an empty list. The analyzer should recognize the R*/C* naming convention with matching GPIO connections as a keyboard matrix.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00002321: footprint 'side' field is always null despite layer information being available; PCB correctly identifies 2-sided assembly and fully routed board

- **Status**: promoted
- **Analyzer**: pcb
- **Source**: pcb_ctrl-M_ctrl-m.kicad_pcb.json.json
- **Created**: 2026-03-24

### Correct
- The analyzer correctly identifies ctrl-M as a 2-layer board (B.Cu, F.Cu) with components on both sides (21 front, 18 back), 10 through-hole and 18 SMD parts, 445 track segments, 52 vias, routing_complete=true with 0 unrouted nets. The 4 extra footprints (PCB count 39 vs schematic 35) are accounted for by REF** silkscreen markers and additional connector footprints not in the schematic component list.

### Incorrect
- All 39 footprints in the PCB output have side=null, even though each footprint correctly has a 'layer' field ('F.Cu' or 'B.Cu'). The statistics correctly derive front_side=21 and back_side=18 from the layer data, but the per-footprint 'side' field is never populated. The same null-side bug appears in crimpdeq-pcb. Similarly, PCB zones have layer=null despite having copper fill on specific layers. This affects any consumer that reads per-footprint or per-zone side/layer fields.
  (statistics)

### Missed
(none)

### Suggestions
(none)

---
