# Findings: 0x60 / pcb_0x60

## FND-00000307: 20 undriven_input_label warnings are false positives for hierarchical subsheet labels; All 77 keyboard switches misclassified as SMD; MXOnly footprints are THT; assembly_complexity.unique_footprint...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: pcb_key_matrix.kicad_sch.json
- **Created**: 2026-03-23

### Correct
- sourcing_audit.mpn_percent is 0.0 and mpn_coverage is '0/142' because the MPN field is empty for all components. However, 65 diodes (1N4148, D_MiniMELF) have a valid LCSC code C5381438, which is a complete sourcing identifier for JLCPCB/LCSC. The audit treats LCSC-only coverage as zero, understating actual sourcing status. A partial coverage metric (e.g., lcsc_coverage: 65/142, ~45.8%) would be more informative.
- The key_matrices detection (rows: 5, columns: 15, switches_on_matrix: 77, diodes_on_matrix: 65, estimated_keys: 77) is accurate. The 12-switch diode shortfall is by design: the 12 Kb-prefixed switches (Kb014, Kb200, Kb213, Kb300, Kb312, Kb400, Kb401, Kb402, Kb406, Kb411, Kb412, Kb413) are alternate layout position keys sharing the same matrix nodes as primary K-prefixed switches. This is standard keyboard PCB practice for supporting multiple layout options. The 5x15=75 logical matrix positions are correctly identified.

### Incorrect
- key_matrix.kicad_sch is a hierarchical subsheet of 0x60.kicad_sch. All 20 hierarchical labels (Col0–Col14, Row0–Row4) use 'input' shape and are driven by the parent sheet via hierarchical sheet pins. The analyzer inspects the subsheet in isolation and incorrectly flags all 20 nets (Col0..Col14, Row0..Row4) as 'undriven_input_label'. These are valid hierarchical connections, not ERC errors.
  (label_shape_warnings)
- assembly_complexity reports smd_count: 142 and tht_count: 0, classifying all 142 components as SMD. The 77 keyboard switches use footprints in the 0xLib_MK_Switches:MXOnly-* family (e.g., MXOnly-1U-NoLED, MXOnly-6.25U-ReversedStabilizers-NoLED). MX-style keyboard switches are through-hole (THT) parts with PCB pins that pass through the board. Only the 65 diodes (D_MiniMELF footprint) are truly SMD. Expected: smd_count: 65, tht_count: 77.
  (assembly_complexity)
- The assembly_complexity section reports unique_footprints: 1, but the bom_optimization section correctly identifies total_unique_footprints: 12. The schematic has 1 diode footprint (D_MiniMELF) and 11 distinct switch footprints (MXOnly in sizes 1U, 1.25U, 1.5U, 1.75U, 1.75U-Stepped, 2U, 2.25U, 2.75U, 6.25U, 7U, and ISO), for 12 total. The assembly_complexity section is using an inconsistent counting method compared to bom_optimization.
  (assembly_complexity)

### Missed
(none)

### Suggestions
- Fix: All 77 keyboard switches misclassified as SMD; MXOnly footprints are THT

---
