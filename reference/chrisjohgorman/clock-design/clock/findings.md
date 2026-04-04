# Findings: clock-design / clock

## FND-00002016: 4MHz crystal circuit correctly detected with load cap analysis; Decoupling warning for ATmega162 and HD44780 correctly flagged

- **Status**: new
- **Analyzer**: schematic
- **Source**: repos_clock-design_clock.sch.json
- **Created**: 2026-03-24

### Correct
- Y1 (Device:Crystal, 4MHz) is correctly classified as type 'crystal'. The crystal_circuits entry has both 27pF load caps (C1, C2) identified, effective_load_pF=16.5 (computed as (27*27)/(27+27)+3pF stray), and in_typical_range=true. The ATmega162-16PU XTAL1/XTAL2 pins correctly connect to the crystal nets.
- The design has only 2 capacitors (27pF crystal load caps C1/C2) and no bypass/bulk capacitors on the +5V rail. The design_observations correctly flag both U1 (ATmega162-16PU) and DS1 (HD44780) as lacking decoupling on +5V, with rails_with_caps=[]. This is accurate — no 100nF bypass caps are present in the source schematic.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00002017: Dummy PCB file (placeholder) handled gracefully with zero footprints

- **Status**: new
- **Analyzer**: pcb
- **Source**: repos_clock-design_clock.kicad_pcb.json
- **Created**: 2026-03-24

### Correct
- The clock-design PCB file is a single-line KiCad placeholder: '(kicad_pcb (version 4) (host kicad "dummy file") )'. The PCB analyzer correctly returns footprint_count=0, zero tracks/vias/zones, and null board dimensions rather than crashing. This is correct behavior for an empty PCB.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
