# Findings: Scylla-PCB-Plate / flex_flex

## FND-00001401: Key matrix correctly detected as 5x6 with 24 switches and 12 dual-diode packages; Addressable LED chain detection produces 3 overlapping chains instead of recognizing the branching parallel topolog...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: flex.kicad_sch
- **Created**: 2026-03-24

### Correct
- The 12 diodes (D_Schottky_x2_KCom_AAK) are dual-diode packages — each has two anodes (connecting to two separate switch rows) and a common cathode (to a column). 12 packages × 2 switches per package = 24 switches total, matching switches_on_matrix=24. The 5 row nets (row1-row5) and 6 column nets (col1-col6) are correctly named. estimated_keys=24 matches actual switch count. detection_method='net_name' is appropriate and accurate.

### Incorrect
- The 48 SK6812MINI LEDs use a 2D branching topology: each intermediate net carries 2 DOUT outputs (from two LEDs) and 2 DIN inputs (to two LEDs), rather than a simple daisy chain. The analyzer follows different traversal paths and reports 3 chains: chain0 (24 LEDs), chain1 (24 LEDs sharing only D2 with chain0), and chain2 (1 LED, D27, as a stub). Together they cover all 48 unique LEDs, but the chain count and structure are misleading. Reporting 2-3 separate chains with chain_length=24 each overstates estimated_current_mA (reports 1440mA+1440mA = 2880mA instead of the actual 2880mA for 48 LEDs combined), so the numeric total accidentally comes out right but the structure is wrong.
  (signal_analysis)
- connectivity_issues.multi_driver_nets reports 24 pairs of nets where two DOUT pins appear to share a net — e.g., net __unnamed_3 has D19-DOUT and D20-DOUT. However, examining the full net reveals it also carries D21-DIN and D22-DIN: the net legitimately connects two LED outputs to two LED inputs in a branching daisy-chain arrangement. This is valid for the Scylla's LED matrix wiring and does not represent a real electrical conflict. The erc_warnings section also fires an output_conflict for the 'Dout' net (D59 and D60 both drive it) for the same reason.
  (design_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001402: PCB dimensions, DFM tier, and footprint count are accurate including board-only logo footprints

- **Status**: new
- **Analyzer**: pcb
- **Source**: flex.kicad_pcb
- **Created**: 2026-03-24

### Correct
- Board dimensions 126.31x113.05mm are consistent with a full split-keyboard half plate. 105 footprints = 93 from schematic + 12 G*** board-only logo footprints (confirmed board_only=true, exclude_from_bom=true). DFM tier 'advanced' is correctly triggered by 0.1mm annular ring (below standard 0.125mm limit) and board size >100mm on both axes. smd=16 + tht=83 + board_only=6 = 105 total, consistent. Routing complete with zero unrouted nets.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
