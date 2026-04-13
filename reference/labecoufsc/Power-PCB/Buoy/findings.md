# Findings: labecoufsc/Power-PCB / Buoy

## FND-00001093: kicad_version reported as 'unknown' for KiCad 7 file; Component count mismatch: statistics says 141, assembly_complexity says 143; Power ICs correctly identified: BQ24650 MPPT charge controller, TP...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: Buoy.kicad_sch.json
- **Created**: 2026-03-23

### Correct
- All major power management ICs detected with correct topologies. Battery charger identified as ic_with_internal_regulator, buck as switching, LDO correctly identified.
- power_sequencing correctly identifies that U6 EN is driven from the 3.4V rail (R22/C36 divider), and U5 EN is controlled via R16/R17. Power good signal on U5 PG pin also detected.
- All component types correctly classified: 44 resistors, 42 capacitors, 13 connectors, 16 test points, 3 transistors, 4 switches, 6 ICs, 8 diodes, 1 thermistor, 2 LEDs, 2 inductors.

### Incorrect
- file_version '20230121' maps to KiCad 7 but kicad_version field is 'unknown'. The analyzer should map known file_version timestamps to KiCad major versions.
  (signal_analysis)
- statistics.total_components=141 but assembly_complexity.total_components=143. One likely counts only BOM-included parts, the other counts all footprints including test points or logo items, but both claim to be 'total components'.
  (signal_analysis)

### Missed
- statistics.power_rails only lists ['PGND', 'PWR_FLAG']. The design has named nets like /3.4V, /Power_out, /Batman (battery rail), /V_solar_in, /V_solar_out used as power distribution rails. These appear only in net_analysis as signal_nets rather than being recognized as power distribution rails.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00001094: Board outline reports edge_count=2 mixing a circle with the rectangular board profile; 4-layer stackup correctly detected: F.Cu, In1.Cu (power), In2.Cu (power), B.Cu; Footprint count (153) correctl...

- **Status**: promoted
- **Analyzer**: pcb
- **Source**: Buoy.kicad_pcb.json
- **Created**: 2026-03-23

### Correct
- Layer types correctly identified including both inner layers typed as 'power', consistent with the inner planes being used for power distribution.
- PCB has 153 footprints vs 141 schematic components. The difference is accounted for by 4 logo footprints (G***), mounting holes, and 2 extra test points (TP2, TP14 appear in PCB but not in schematic test_points list).
- routing_complete=true, unrouted_net_count=0. Net count matches the gerber x2 net count of 72.

### Incorrect
- board_outline.edge_count=2 with one 'circle' and one 'rect'. The circle (center 81.28, 29.2) is likely a courtyard or mounting hole artifact, not part of the board profile. The true board outline is the 150x110.8mm rectangle. This may cause downstream dimension confusion.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001095: Complete 4-layer gerber set correctly detected with all required layers present; Alignment false positive: all three full gerber sets report aligned=false

- **Status**: promoted
- **Analyzer**: gerber
- **Source**: BuoyPowerPCB.json
- **Created**: 2026-03-23

### Correct
- All 11 gerber layers found, completeness=true, both PTH and NPTH drill files detected. 90 vias correctly identified via X2 attributes.

### Incorrect
- The alignment check flags layer extent differences (copper layers being smaller than Edge.Cuts) as alignment issues. This is normal for any real PCB where components don't fill the full board area. The BuoyPowerPCB set reports Width varies by 15.2mm and Height varies by 25.7mm but this is just because copper/components don't extend to the board edge, not a real misalignment.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001096: PnP-only file set correctly identified as incomplete (missing copper/mask layers); Component refs in PnP gerbers have spurious double-quote characters in names; Pad count per component inflated in ...

- **Status**: promoted
- **Analyzer**: gerber
- **Source**: PCBWay Files.json
- **Created**: 2026-03-23

### Correct
- The PCBWay Files directory contains only component placement (pnp_top/pnp_bottom) files. Analyzer correctly reports complete=false with B.Cu, F.Cu, B.Mask, Edge.Cuts etc. all missing.

### Incorrect
- In PCBWay Files output, component_refs contain quoted strings like '"C1"', '"C10"' with literal embedded quotes. This is a parsing bug where X2 component attribute strings are not being unquoted when the PnP format wraps them in quotes.
  (signal_analysis)
- In the PCBWay Files pads_per_component, all 2-pad passives (capacitors, resistors) show 3 pads instead of 2, and multi-pad ICs are similarly inflated by 1. This is because the PnP component files include an extra centroid/outline aperture counted as a pad.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001097: 4-layer complete gerber set with NPTH mounting holes correctly detected

- **Status**: new
- **Analyzer**: gerber
- **Source**: PCBWay Production Files 24.4.24.json
- **Created**: 2026-03-23

### Correct
- 4 NPTH holes (2.1996mm = ~M2.2 mounting holes) correctly classified. All 11 layers present. Via count of 90 matches PCB output.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001098: Earlier gerber revision correctly parsed with same structural results as later revision

- **Status**: new
- **Analyzer**: gerber
- **Source**: PCBWay Production Files.json
- **Created**: 2026-03-23

### Correct
- Both PCBWay Production Files sets report identical pad counts, via counts, and net counts, confirming the two exports differ only in minor routing details between design iterations.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
