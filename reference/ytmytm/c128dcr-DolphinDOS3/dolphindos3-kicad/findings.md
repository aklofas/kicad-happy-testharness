# Findings: ytmytm/c128dcr-DolphinDOS3 / dolphindos3-kicad

## FND-00002296: multi_driver_nets reports 20 false-positive duplicate-driver entries for glue logic outputs; bus_topology 'width' field counts label instances rather than unique signal count

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: schematic_c128dcr-DolphinDOS3_dolphindos3-kicad_dolphindos3-kicad.kicad_sch.json
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
- The connectivity_issues.multi_driver_nets list contains 28 entries, of which 20 are false positives where the same component/pin pair is listed twice as both drivers (e.g., IC10 pin 8 appears twice on net __unnamed_0). This duplication in the driver list is an internal analyzer bug causing spurious multi-driver warnings. Only 8 entries are real cases (D0-D7 shared between ROM IC2 and RAM IC3), which are also not real errors since ROM and RAM share the data bus with appropriate chip-select logic.
  (connectivity_issues)
- The detected_bus_signals entry for the A bus reports width=74 with range A0..A15, implying a 74-bit bus. The actual bus is 16-bit (A0..A15). The 74 figure is the total count of net label instances in the schematic (each address line appears ~4-5 times across multiple ICs). The 'width' field should represent the number of unique signals (16), not the total label occurrence count. Same issue affects D bus (width=48, should be 8) and PA bus (width=16, should be 8).
  (bus_topology)

### Missed
(none)

### Suggestions
(none)

---

## FND-00002297: Gerber set correctly assessed as complete with all required layers present

- **Status**: new
- **Analyzer**: gerber
- **Source**: gerber_c128dcr-DolphinDOS3_dolphindos3-kicad_plots.json
- **Created**: 2026-03-24

### Correct
- The completeness check correctly identifies all 9 required layers (F.Cu, B.Cu, F.Mask, B.Mask, F.Paste, B.Paste, F.SilkS, B.SilkS, Edge.Cuts) are present with both PTH and NPTH drill files. missing_required and missing_recommended are both empty. Layer alignment is confirmed correct across all copper and mask layers.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
