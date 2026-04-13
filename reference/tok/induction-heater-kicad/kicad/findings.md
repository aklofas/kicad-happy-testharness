# Findings: tok/induction-heater-kicad / kicad

## FND-00002222: PCB analysis returns all-zero statistics for a valid .kicad_pcb file

- **Status**: promoted
- **Analyzer**: pcb
- **Source**: pcb_induction-heater-kicad_kicad_kicad.kicad_pcb.json
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
- The PCB analyzer reports 0 footprints, 0 tracks, 0 vias, 0 zones, null board dimensions, and 0 nets for a real induction heater PCB. The .err file content indicates 'Written to ...' suggesting no error was thrown, yet the output is completely empty. The schematic shows 8 components (2 MOSFETs, 1 gate driver IC, 1 diode, 1 inductor, 1 capacitor, 1 resistor, 1 connector) that should appear in the PCB. This is likely a parsing failure for a KiCad 5-format PCB file that silently returns empty rather than erroring.
  (statistics)

### Missed
(none)

### Suggestions
(none)

---

## FND-00002223: Half-bridge topology with dual NMOS and dedicated gate driver not detected as bridge circuit; Gate driver IC (MCP14E10) correctly linked to both MOSFETs and decoupling warning issued

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: schematic_induction-heater-kicad_kicad_kicad.sch.json
- **Created**: 2026-03-24

### Correct
- The analyzer correctly identifies both Q1 and Q2 as NMOS MOSFETs with U1 (MCP14E10) as their gate driver IC. It also correctly raises a design_observation for 'decoupling' noting that U1's +12V rail has no local bypass capacitor (rails_without_caps: ['+12V']). The power rails (+12V, +24V, GND) are correctly classified.

### Incorrect
(none)

### Missed
- The induction heater uses two IRFP4332 N-channel MOSFETs (Q1, Q2) driven by an MCP14E10 dual gate driver IC in a half-bridge configuration with a resonant tank (L + 2.2uF capacitor). The bridge_circuits list is empty. The transistor_circuits entries for Q1 and Q2 also incorrectly report drain_net as 'GND' and drain_is_power as true — on a half-bridge the drains connect to the high rail (+24V) or the midpoint, not GND. This suggests a pin mapping confusion in the legacy KiCad 5 MOSFET symbol (Q_NMOS_DGS: D=pin1, G=pin2, S=pin3 but the actual net connections may differ). The resonant LC tank (L? + C?) also produces no lc_filters entry, likely because both components have generic unannotated values.
  (signal_analysis)

### Suggestions
(none)

---
