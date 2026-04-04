# Findings: Spider-eMMC / Carrier_SpiderCarrier.kicad_pcb

## FND-00001578: statistics.dnp_parts=0 is correct for Carrier (no DNP components), but statistics.total_components=8 undercounts by 1; 61082-041400LF (40-pin SMD connector) is missing from BOM output entirely; 610...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: SpiderCarrier.kicad_pcb.kicad_sch
- **Created**: 2026-03-24

### Correct
- The analyzer correctly identifies C4(4.7uF) and C5(100nF) on +1V8, and C2(4.7uF) and C3(1uF) on +3.3V. C1(1uF) is correctly omitted from decoupling because its pin1 connects to an eMMC NC pad row (at y=130.81 in schematic coordinates) rather than to a power rail. The 2-rail decoupling coverage (bulk+bypass for each) is accurately reported.

### Incorrect
- The Carrier schematic has 9 component entries in the components list (two separate symbols both annotated 'U?': SDINBDG4-8G and 61082-041400LF). Because the BOM deduplication groups both U? references as one entry, total_components counts 8 (BOM quantity sum) instead of 9 physical symbols. The annotation_issues section correctly flags duplicate_references=['U?'] and unannotated=['U?']. The component count is off by one.
  (statistics)
- The 61082-041400LF (Amphenol FCI, LCSC C236050) is a 40-pin SMD connector used as the eMMC socket interface between the carrier and the host board. The analyzer classifies it as type='ic' because it comes from a custom library (MyJLCLib2024) and has no connector-recognizable keywords. The symbol's pin type is 'unspecified' throughout, so type heuristics fall back to 'ic'. The statistics.component_types show ic:1 but should show ic:1, connector:2 if both U? components were correctly classified.
  (signal_analysis)
- The SDINBDG4-8G eMMC is powered by both +3.3V (VCC pins E6, F5, J10, K9) and +1V8 (VCCQ pins C6, M4, N4, P3, P5). The power_budget only reports the eMMC on the +3.3V rail (estimated_mA=10) and omits +1V8 entirely. The design_analysis.power_domains correctly identifies both +1V8 and +3.3V as IC power rails for U?, but this information does not propagate to power_budget. Same issue is present in UnifiedBoard output.
  (power_budget)

### Missed
- The Carrier schematic contains a second U? symbol (lib_id MyJLCLib2024:61082-041400LF, LCSC C236050), which is the 40-pin eMMC socket connector with in_bom=yes. Because both symbols share the reference 'U?', the BOM deduplication keeps only the first entry (SDINBDG4-8G) and silently drops the 61082-041400LF. The BOM lists 6 unique parts instead of 7, and the connector does not appear in any BOM entry. statistics.unique_parts=6 should be 7.
  (statistics)

### Suggestions
- Fix: 61082-041400LF is classified as type 'ic' but is a multi-pin SMD board-to-board connector

---

## FND-00001579: statistics.dnp_parts=0 is wrong; the schematic contains 9 DNP components; power_budget missing +1V8 rail load for eMMC (SDINBDG4-8G)

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: UnifiedBoard_SpiderUnifiedBoard.kicad_sch
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
- The UnifiedBoard schematic has 9 resistors marked (dnp yes) and (in_bom no): R11 (4.7KOhm), and R3–R10 (all 10KOhm). The analyzer's components list correctly identifies all 9 with dnp=True, but statistics.dnp_parts reports 0. This means the statistics field is not being computed from the components list but from some other path that misses the dnp flag. The total_components=32 includes all 32 (DNP + non-DNP), which is correct behavior for total count, but dnp_parts must reflect the 9 DNP components.
  (statistics)
- Same issue as the Carrier schematic: the SDINBDG4-8G eMMC uses both +1V8 (VCCQ) and +3.3V (VCC). The power_budget only shows +3.3V with estimated_mA=10 for U?. The +1V8 rail is absent from power_budget.rails despite the decoupling_analysis correctly identifying C4 and C5 as +1V8 decoupling capacitors.
  (power_budget)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001580: Unrouted net Net-(U1-RCLK) correctly detected between R2.1 and U1.H5; DFM tier correctly classified as 'challenging' due to 0.05mm minimum track width; Footprint count of 9 is correct; both U1 (eMM...

- **Status**: new
- **Analyzer**: pcb
- **Source**: SpiderCarrier.kicad_pcb.kicad_pcb
- **Created**: 2026-03-24

### Correct
- The Carrier PCB has one unrouted connection between the RCLK pin of the eMMC (U1.H5) and the RCLK pullup resistor (R2.1). The analyzer correctly reports routing_complete=false, unrouted_count=1, and identifies the specific pads involved. This matches the design state where the eMMC Repeated Clock signal is intentionally or unintentionally left unrouted.
- The Carrier PCB uses 0.05mm track width (below the 0.1mm advanced process minimum) for the high-density FBGA-153 routing. The analyzer correctly identifies this as challenging tier with two DFM violations: track_width (0.05mm vs 0.1mm advanced limit) and annular_ring (0.1mm vs 0.125mm standard limit). Both violations are accurately described.
- The Carrier PCB has 9 footprints: C1–C5, R2, VSF4 (test pad), U1 (SDINBDG4-8G eMMC, FBGA-153), and U4 (61082-041400LF connector). This is consistent with the source .kicad_pcb file. The discrepancy between PCB footprint count (9) and schematic total_components (8) is caused by the BOM deduplication bug for duplicate U? references, not a PCB analyzer error.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001581: Routing complete with 0 unrouted nets on UnifiedBoard PCB; Footprint count of 34 is correct including logo and unnamed component footprints

- **Status**: new
- **Analyzer**: pcb
- **Source**: UnifiedBoard_SpiderUnifiedBoard.kicad_pcb
- **Created**: 2026-03-24

### Correct
- The UnifiedBoard PCB is fully routed with 275 track segments, 61 vias, 4 zones, and no unrouted nets. The connectivity analysis correctly reports routing_complete=true and routed_nets=17 (power + data signal nets). Total net_count=132 includes the many auto-named single-pad nets from the eMMC NC pads.
- The UnifiedBoard PCB has 34 footprints: 32 schematic components (23 non-DNP + 9 DNP), 1 board-only logo (G***, LOGO), and 1 unnamed SMD footprint with no reference. The smd_count=16 counts footprints with smd attribute; the 16 connectors/test-points have exclude_from_pos_files attribute and are counted separately. This breakdown is accurate per the PCB file attributes.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001582: Referenced gerber output files do not exist; repo contains no gerber files

- **Status**: promoted
- **Analyzer**: gerber
- **Source**: Fabrication.json _ Fabrication_v2.json
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
(none)

### Missed
- The task listed two gerber output files (Fabrication.json and Fabrication_v2.json) but neither exists under results/outputs/gerber/Spider-eMMC/. The gerbers.txt manifest is empty, confirming no gerber files were found in the Spider-eMMC repository. The repo contains only .kicad_pcb and .kicad_sch source files with no exported gerber/drill files. No gerber analysis was performed.
  (signal_analysis)

### Suggestions
(none)

---
