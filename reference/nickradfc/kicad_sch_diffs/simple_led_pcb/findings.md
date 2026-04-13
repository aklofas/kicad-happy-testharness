# Findings: nickradfc/kicad_sch_diffs / simple_led_pcb

## FND-00002372: Four single-pin nets from unconnected RGB LED channels not reported in connectivity_issues.single_pin_nets; assembly_complexity reports smd_count=3 for components with no assigned footprints

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: schematic_kicad_sch_diffs_simple_led_pcb.kicad_sch.json.json
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
- The RGB LED (D1, Device:LED_RGB) has 6 pins. Only the RA (pin 6) connects to the resistor, and BK (pin 3) connects to the battery negative. The remaining four pins — RK (pin 1), GK (pin 2), BA (pin 4), GA (pin 5) — each form isolated single-pin nets (__unnamed_3 through __unnamed_6), as confirmed by their point_count of 1 in the nets section. However, connectivity_issues.single_pin_nets is an empty array. The analyzer correctly nets the pins but fails to flag these dangling connections in the connectivity issues report.
  (connectivity_issues)
- All three components (BT1, R1.1, D1) have empty footprint fields and appear in missing_footprint. Without footprint assignments, the SMD vs THT classification cannot be determined from the schematic alone. Yet assembly_complexity reports smd_count=3, tht_count=0, implying all components are SMD. This is a false inference — the correct output should be smd_count=0 or the field should reflect 'unknown' when footprints are absent. The complexity_score of 40 based on 3 'medium' SMD parts is similarly unreliable.
  (assembly_complexity)

### Missed
(none)

### Suggestions
(none)

---

## FND-00002373: Empty PCB correctly analyzed as having zero footprints, tracks, and nets

- **Status**: new
- **Analyzer**: pcb
- **Source**: pcb_kicad_sch_diffs_simple_led_pcb.kicad_pcb.json.json
- **Created**: 2026-03-24

### Correct
- The simple_led_pcb.kicad_pcb file exists as an empty board layout (the schematic symbols have no footprints). The PCB analyzer correctly reports footprint_count=0, track_segments=0, via_count=0, net_count=0, and routing_complete=true. The copper_presence warning about unfilled zones is appropriate.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
