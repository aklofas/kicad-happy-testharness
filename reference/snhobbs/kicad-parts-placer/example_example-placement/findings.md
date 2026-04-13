# Findings: snhobbs/kicad-parts-placer / example_example-placement

## FND-00002198: Test point components classified as 'test_point' type but use Conn_01x01_Male lib_id — while classification is defensible, pin extraction for J1 (Conn_01x20) yields no pins; Differential pairs RX+/...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: schematic_kicad-parts-placer_example_example-placement_example-placement.kicad_sch.json
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
- J1 (a 2x10 SMD pin header, Conn_01x20) has 20 pin_uuids correctly captured, yet the 'pins' field is None and the component appears in all 14 nets. The pin-level data is absent from the components list while the net connectivity is fully resolved through the nets dict. The test_point classification for TP1–TP16 using Conn_01x01_Male footprints is reasonable (value field encodes signal name), though these are really single-pin connectors rather than true test pads.
  (statistics)

### Missed
- Test points TP6 (RX+), TP7 (RX-), TP8 (TX+), TP9 (TX-) carry values matching the standard differential pair naming pattern. The design_analysis.differential_pairs list is empty. Even though these are single-pin connectors rather than IC signal pins, the net name pattern recognition should flag these as candidate differential pairs for the LVDS/differential bus on J1.
  (design_analysis)

### Suggestions
(none)

---

## FND-00002199: Placed and unplaced PCB variants correctly parsed with 19 of 21 footprints at different positions

- **Status**: new
- **Analyzer**: pcb
- **Source**: pcb_kicad-parts-placer_example_example-placement_example-placement_placed.kicad_pcb.json
- **Created**: 2026-03-24

### Correct
- The kicad-parts-placer tool produces both an input (unplaced) and output (placed) PCB. The analyzer correctly processes both: 21 footprints each, same net count (14), same board outline (57x87mm), routing_complete=false with 14 unrouted nets (no autorouting performed). Footprint positions differ for 19 of 21 components between the two files, confirming the placer ran successfully. The 4 mounting holes are correctly typed as 'exclude_from_pos_files'.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
