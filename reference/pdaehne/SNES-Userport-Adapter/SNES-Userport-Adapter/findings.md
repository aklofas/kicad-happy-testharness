# Findings: pdaehne/SNES-Userport-Adapter / SNES-Userport-Adapter

## FND-00001292: Edge.Cuts counted as copper layer, copper_layers_used reported as 3 instead of 2; Edge clearance warning for J2 (SNES socket) at -0.5mm is likely a false positive; GND copper zone correctly identif...

- **Status**: promoted
- **Analyzer**: pcb
- **Source**: SNES-Userport-Adapter.kicad_pcb.json
- **Created**: 2026-03-24

### Correct
- zones[0] net='GND', layers=['F&B.Cu'], filled_area_mm2=3893.99, fill_region_count=2 — correctly shows a stitched two-layer ground pour covering the full board.

### Incorrect
- Same bug as SFH203: copper_layer_names includes 'Edge.Cuts' and copper_layers_used=3. This is a 2-layer board (F.Cu + B.Cu). Edge.Cuts is a mechanical layer, not a copper layer.
  (signal_analysis)
- J2's courtyard extends 0.5mm beyond the board edge, flagged as edge_clearance_mm=-0.5. The SNES controller socket is an edge-mount connector intentionally designed to overhang the board edge for socket access. This is expected, not a placement error.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001293: VCC_Ctrl / jumper JP1 power switching correctly parsed; missing_connector_labels warning fires for J4 (C64 Userport) which has extensive silkscreen labeling on PCB

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: SNES-Userport-Adapter.kicad_sch.json
- **Created**: 2026-03-24

### Correct
- JP1 (SolderJumper_2_Open) correctly connects VCC to /VCC_Ctrl on its pads. The schematic shows power_rails includes VCC_Ctrl as a separate rail, and the jumper's role as an optional power bridge is reflected in the net topology.

### Incorrect
- PCB silkscreen shows detailed labels for J4 ('C64, PET, Plus/4 or VIC-20 Userport'), J2 ('SNES Controller'), J1 pin labels, and J3 ('Audio Out'). The schematic-level check fires because pin labels aren't in the schematic symbol, but the PCB has full documentation. This is a minor false positive in a connector-centric adapter board.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---
