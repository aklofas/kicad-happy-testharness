# Findings: upb-lea/KiClearance / examples_clearance_example

## FND-00000744: Simple test schematic: all 6 components correctly extracted (J1, J2, J3, R1, D1, U2); Isolation barrier (NSL-32 optocoupler) not detected in isolation_barriers

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: examples_clearance_example.kicad_sch.json
- **Created**: 2026-03-23

### Correct
- Component types, connectivity (7 nets), and pin mappings all match the source. NSL-32 optocoupler correctly typed as 'ic'. All nets correctly traced through the optocoupler's LED-input and photocell-output sides.

### Incorrect
(none)

### Missed
- signal_analysis.isolation_barriers is empty despite U2 being an NSL-32 optocoupler (lib_id 'Isolator:NSL-32'). The subcircuits section correctly identifies U2 with J1/J2 neighbors, but isolation_barriers is not populated. The Isolator lib namespace should trigger detection.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00000745: PCB stats correct: 6 footprints (4F/2B), 2 SMD, 4 THT, fully routed 7 nets; layer_transitions reports nets crossing layers without vias — this is suspicious but real; Board outline missing correctl...

- **Status**: promoted
- **Analyzer**: pcb
- **Source**: examples_clearance_example.kicad_pcb.json
- **Created**: 2026-03-23

### Correct
- Footprint count, layer placement, routing completeness, zone data all accurate. Net names match schematic-side names.
- The KiClearance test PCB has no Edge.Cuts outline — the analyzer correctly reports null for all board dimension fields.

### Incorrect
- Net-(D1-A) and Net-(J3-Pin_1) are reported as spanning both B.Cu and F.Cu with via_count=0. This means tracks cross layers without vias, which would be a DRC error in a real board. However the board has no Edge.Cuts (board_outline edge_count=0), suggesting this is purely a test/demo PCB, not a production design. The analyzer correctly reports this anomaly.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---
