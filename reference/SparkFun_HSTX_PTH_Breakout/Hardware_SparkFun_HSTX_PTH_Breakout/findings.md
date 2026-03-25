# Findings: SparkFun_HSTX_PTH_Breakout / Hardware_SparkFun_HSTX_PTH_Breakout

## FND-00001461: Component count of 8 is accurate; power_rails lists only GND, missing 3.3V; HSTX differential pairs misclassified as UART nets; HSTX differential pairs not detected; Net count of 16 and wire count ...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: SparkFun_HSTX_PTH_Breakout.kicad_sch
- **Created**: 2026-03-24

### Correct
- The schematic contains ST1, ST2 (standoffs/mounting holes), FID1, FID2 (fiducials), J1 (22-pin FPC connector), J2 (17-pin PTH connector), G1 (SparkFun logo), and G2 (OSHW logo). The count of 8 and breakdown by type (2 mounting_hole, 2 fiducial, 2 connector, 2 other) are all correct.
- The nets section contains exactly 16 entries (3.3V, D2-/HSTX1, CK+/HSTX2, CK-/HSTX3, D1+/HSTX4, D1-/HSTX5, D0+/HSTX6, D0-/HSTX7, GND, SDA, SCL, IO1/IO29, IO0/IO28, D3+/NC, D3-/NC, D2+/HSTX0), consistent with statistics.total_nets = 16.
- This board is purely a passthrough breakout — FPC connector to PTH header with no active components, no regulators, no filters, and no decoupling caps. All signal_analysis arrays (voltage_dividers, rc_filters, power_regulators, protection_devices, etc.) are correctly empty.

### Incorrect
- The schematic has a net named '3.3V' that appears in the nets section and is connected to pins of J1 and J2. The 3.3V net is a power signal (it is named with a voltage and passed through the breakout board). However, statistics.power_rails only lists ['GND'], omitting 3.3V. The net_classification in design_analysis correctly marks 3.3V as 'signal' (not 'power'), which explains why it wasn't promoted — but this is a borderline case since the PTH connector is just routing 3.3V through from an HSTX cable. Without a PWR_FLAG or dedicated power symbol driving 3.3V, the omission is technically defensible, but it is an observable omission that may mislead users.
  (statistics)
- The bus_analysis section lists 8 nets (D0-/HSTX7, CK+/HSTX2, CK-/HSTX3, D1+/HSTX4, D1-/HSTX5, D0+/HSTX6, D2-/HSTX1, D2+/HSTX0) as 'uart' bus entries. These are RP2350 HSTX (High-Speed Transmitter) differential pairs — a parallel serializer interface for DVI/HDMI output, completely distinct from UART. They also appear under testability_analysis as 'uart' key nets. The differential_pairs array is empty, which is another missed detection: these HSTX pairs (D0+/D0-, D1+/D1-, D2+/D2-, CK+/CK-) should be flagged as differential pairs, not UART.
  (design_analysis)

### Missed
- The HSTX connector (J1, 22-pin FPC) carries 4 differential pairs: D0+/D0-, D1+/D1-, D2+/D2-, CK+/CK-. These are passed through to the PTH connector J2. The design_analysis.differential_pairs array is empty. The signal names in the nets (with +/- suffixes) and the HSTX protocol should have triggered differential pair detection. The HSTX_to_DVI sibling design correctly detects these as HDMI differential pairs when they reach the HDMI connector.
  (design_analysis)

### Suggestions
(none)

---

## FND-00001462: Board dimensions 16x44mm, 2-layer, net count 16 are correct; footprint_count of 43 is inflated by 33 kibuzzard decoration footprints; smd_count=5 and tht_count=1 are inconsistent with the design; E...

- **Status**: promoted
- **Analyzer**: pcb
- **Source**: SparkFun_HSTX_PTH_Breakout.kicad_pcb
- **Created**: 2026-03-24

### Correct
- The PCB statistics correctly report board_width_mm=16.0, board_height_mm=44.0, copper_layers_used=2 (F.Cu and B.Cu), net_count=16, routing_complete=true, and unrouted_net_count=0.
- thermal_analysis.zone_stitching correctly reports a GND zone spanning F&B.Cu with zone_area_mm2=704.0, via_count=28, and 0.3mm drill sizes. This matches statistics.via_count=28.

### Incorrect
- The PCB reports footprint_count=43 and smd_count=5, tht_count=1. The high footprint count is due to 33 kibuzzard-prefixed board-only decoration footprints (zero pads, board_only=true), plus 2 fiducials, 2 standoffs, 2 connectors, 1 OSHW logo, 1 Ref**, 1 SparkFun logo (G2). The electrical component count (J1, J2, FID1, FID2, ST1, ST2) is 6 which matches the schematic's 6 on-board components. The footprint_count includes all PCB items including non-electrical decoration, which may mislead users about functional component count.
  (statistics)
- smd_count=5 and tht_count=1 are very low for a board with 43 footprints. Examining the footprints: J2 is correctly through_hole (1 THT), but the 2 standoffs (ST1, ST2) and 2 fiducials (FID1, FID2) are classified as 'smd'. G2 (OSHW logo) and the kibuzzard items are board_only. The 33 kibuzzard footprints have no pads and so don't contribute to smd/tht counts. The effective classification appears to count only pads-present footprints, reporting 5 SMD (2 standoffs + 2 fiducials + G2 with pads?) and 1 THT (J2). J1 (FPC connector) appears to be missing from the tht_count or smd_count — it should be SMD (FPC connectors are SMD type).
  (statistics)
- placement_analysis.edge_clearance_warnings reports G2 (OSHW_Logo) at -79.0mm and J2 at -40.23mm edge clearance. Negative clearance values indicate the analyzer is computing clearance for a footprint placed outside the board area or using a reference point far from the board edge. G2 has no courtyard and is an aesthetic-only footprint — it should be excluded from clearance checks. The J2 connector is intentionally placed at the edge (a PTH breakout header). These false warnings could mislead users.
  (placement_analysis)

### Missed
(none)

### Suggestions
(none)

---
