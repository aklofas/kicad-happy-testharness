# Findings: moteus / hw_c1_moteus_c1

## FND-00000050: Current sense shunts (2mOhm) not detected

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: hw_c1_moteus_c1.kicad_sch.json
- **Created**: 2026-03-13

### Correct
(none)

### Incorrect
(none)

### Missed
- 3x R4/R5/R6 with Kelvin connections and anti-alias RC filters feeding DRV8323 integrated CSA. current_sense=[]. 2mOhm shunt resistors not detected.
  (signal_analysis.current_sense)

### Suggestions
- Detect very low value resistors (< 100mOhm) as current sense shunts, especially when connected to CSA/sense amplifier inputs

---

## FND-00000051: Three-phase bridge nets all identical (OUTX, GHX, GLX, SPX_Q)

- **Status**: new
- **Analyzer**: schematic
- **Source**: hw_c1_moteus_c1.kicad_sch.json
- **Related**: KH-026
- **Created**: 2026-03-13

### Correct
(none)

### Incorrect
- h_bridge.kicad_sch instantiated 3x but nets not namespaced per instance. All three phases share identical net names OUTX, GHX, GLX, SPX_Q instead of phase-specific names.
  (nets)

### Missed
(none)

### Suggestions
- Namespace nets per hierarchical sheet instance to distinguish phase A/B/C

---

## FND-00000057: CAN 120-ohm termination not linked to CAN bus detection

- **Status**: new
- **Analyzer**: schematic
- **Source**: hw_c1_moteus_c1.kicad_sch.json
- **Created**: 2026-03-13

### Correct
(none)

### Incorrect
(none)

### Missed
- CAN bus 120-ohm termination resistor present but not linked to CAN bus protocol detection.
  (signal_analysis.bus_protocols)

### Suggestions
- When detecting CAN bus, also identify termination resistors (120 ohm between CANH/CANL)

---

## FND-00000294: moteus motor controller PCB: copper_layers_used misses In1.Cu (zone-only layer), zone stitching via density inflated by per-polygon area calculation, V+ power net current capacity misleading without zone copper area

- **Status**: promoted
- **Analyzer**: pcb
- **Source**: hw_c1_moteus_c1.kicad_pcb.json
- **Related**: KH-155, KH-159
- **Created**: 2026-03-17

### Correct
- Footprint count and SMD/THT breakdown consistent with compact motor controller design
- Routing completeness correctly detected
- DFM analysis present with appropriate tier
- Decoupling placement analysis correctly identifies bypass cap associations

### Incorrect
- copper_layers_used does not count In1.Cu which has zone fills but no tracks. The board uses In1.Cu as a ground/power plane via zone fills, but since there are no track segments on that layer, it is not counted
  (statistics.copper_layers_used)
- Zone stitching via density calculation uses per-polygon areas rather than per-net totals, inflating density numbers when a net has multiple zone polygons
  (zone_stitching_vias)
- V+ power net current capacity analysis does not account for zone copper area, making the capacity rating misleading for nets primarily routed through zones
  (power_net_routing)

### Missed
(none)

### Suggestions
- Count layers with zone fills (not just tracks) in copper_layers_used
- Use per-net total zone area for stitching via density, not per-polygon
- Include zone copper area in power net current capacity calculations

---
