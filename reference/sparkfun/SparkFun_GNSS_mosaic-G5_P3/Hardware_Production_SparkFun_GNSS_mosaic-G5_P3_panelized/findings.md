# Findings: sparkfun/SparkFun_GNSS_mosaic-G5_P3 / Hardware_Production_SparkFun_GNSS_mosaic-G5_P3_panelized

## FND-00001434: Board dimensions, layer count, net count, and component counts are accurate; mosaic-G5 PCB correctly shows more zones than ZED-X20P (6 vs 2), consistent with larger GNSS IC

- **Status**: new
- **Analyzer**: pcb
- **Source**: Hardware_SparkFun_GNSS_mosaic-G5_P3.kicad_pcb
- **Created**: 2026-03-24

### Correct
- Board dimensions 43.18 x 43.18 mm match the ZED-X20P (same SparkFun form factor). 4-layer stackup is correct. footprint_count=147 matches component_groups sum=147. Net count 75 matches the schematic (75 total nets). smd_count=49, tht_count=4 correctly reflect the 49 SMD-type and 4 through_hole-type footprints respectively (the remaining 94 are board_only, allow_soldermask_bridges, or exclude_from_pos types — kibuzzard logo decals and other non-component graphics). routing_complete=true with 0 unrouted nets is correct.
- zone_count=6 for mosaic-G5 vs zone_count=2 for ZED-X20P. This is plausible: the mosaic-G5 (U3) is a much larger 94-pad LGA package than the ZED-X20P (U5, 54-pad) and requires more copper pour zones for ground and thermal management. The mosaic-G5 also has 164 vias vs ZED-X20P's 162, and higher zone count is consistent with more aggressive ground stitching. The DFM tier=standard is correct for both boards.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001435: Panel PCB also falsely reports routing_complete=false due to NC pad replication across 4 instances

- **Status**: promoted
- **Analyzer**: pcb
- **Source**: SparkFun_GNSS_mosaic-G5_P3_panelized.kicad_pcb
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
- Same issue as the ZED-X20P panelized board: unrouted_count=30, all entries are 'unconnected-(NC-Pad)' nets with 4 pads each (panel has 4 instances of the board). For example, 'unconnected-(D12-K1-Pad1)' appears with 4 pads ['D12.1', 'D12.1', 'D12.1', 'D12.1']. All 30 unrouted nets are NC pads from J1 USB-C, D12/D13 ESD ICs, and U3 reserved pins. The single-board mosaic-G5 PCB file correctly shows routing_complete=true. Panel dimensions are 115.8 x 100.56 mm, consistent with a 2x2 array of 43.18mm boards with V-score rails.
  (statistics)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001436: RC filter and LC filter detectors return empty results despite multiple filtering components present

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: Hardware_SparkFun_GNSS_mosaic-G5_P3.kicad_sch
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
(none)

### Missed
- rc_filters=[] and lc_filters=[] for the mosaic-G5 schematic, yet the design has a ferrite bead L1 (470 Ohm @ 100MHz) and multiple decoupling caps. The design also has U3 (mosaic-G5) with VANT supply pin filtered through a ferrite bead — this is a common RF bias filtering pattern that should be detected. By contrast, the ZED-X20P correctly (if imperfectly) detects RC and LC filter structures involving R6/C3/L1/L2. The mosaic-G5 uses the same L1 ferrite bead topology but the detector finds nothing, suggesting a net topology difference causes the detection to miss it.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00001437: Same GKO misidentification as B.Mask causes false missing Edge.Cuts report for mosaic-G5 panel; Layer set, trace widths, and pad counts are accurate for the mosaic-G5 panel

- **Status**: promoted
- **Analyzer**: gerber
- **Source**: Hardware_Production
- **Created**: 2026-03-24

### Correct
- The 9 Gerber files are parsed correctly. 7 unique trace widths (0.1524–0.5588 mm) are detected, matching the wider range expected for a design with a larger GNSS module (U3 has more power pins needing wider traces). Front copper has 1615 flashes vs ZED-X20P's 3882 — consistent with mosaic-G5 being a 2x2 panel (4 copies) vs ZED-X20P's 3x3 (9 copies). The smd_ratio=1.0 correctly reflects that all pads with X2 data are SMD (both designs are fully SMD assembly on top side, with THT PTH headers on bottom). The zip archive contains 9 gerbers + 1 drill file correctly identified within the archive listing.

### Incorrect
- Identical bug to the ZED-X20P gerber output: SparkFun_GNSS_mosaic-G5_P3_panelized.GKO is assigned layer_type='B.Mask' with FileFunction='Soldermask,Bot' in x2_attributes, but its aperture_analysis has a Profile-function aperture indicating it is the board outline. completeness.missing_required=['Edge.Cuts'] is therefore a false positive. drill_files=0 in statistics is also incorrect — the zip archive contains 1 drill file. The layer_extents for B.Mask (132.274 x 116.844 mm) are also suspicious as a board outline layer would have extents matching the panel outline (~115.8 x 100.56 mm for the mosaic-G5 panel), while mask extents are normally slightly larger than copper extents.
  (completeness)

### Missed
(none)

### Suggestions
(none)

---
