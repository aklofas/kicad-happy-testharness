# Findings: halcyon / Template module_template-module

## FND-00002114: copper_layers_used reported as 0 despite a filled GND zone present on both F.Cu and B.Cu; Unrouted pad list shows H1.1 and H2.1 each duplicated four times rather than listing distinct pads

- **Status**: promoted
- **Analyzer**: pcb
- **Source**: pcb_halcyon_Template module_template-module.kicad_pcb.json
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
- The board has a single GND copper zone that spans F&B.Cu, is filled (filled_area_mm2=1018.52 with regions on both B.Cu and F.Cu), yet statistics.copper_layers_used is 0 and copper_layer_names is empty. The zone fill is the only copper on this template board, so the counter for copper layers used does not account for zone-only copper usage.
  (statistics)
- The connectivity.unrouted entries for the Wuerth standoff footprints (H1, H2) list 'H1.1' and 'H2.1' four times each, with pad_count=4, even though each footprint has 7 pads total (pad_nets shows only one logical connection). The duplicate pad references reflect multiple copper pads all numbered '1' in the footprint, but the output makes it look like the same pad appears four times rather than four distinct pads sharing the same number.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---
