# Findings: battery_ups_kicad / battery_ups

## FND-00001965: Power regulator modules (XL4015 step-down U1, step-up U3) not detected in signal_analysis.power_regulators; multi_driver_nets false positive: GND driven by U1.OUT- and U3.OUT- is not a real conflic...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: battery_ups.kicad_sch.json
- **Created**: 2026-03-24

### Correct
- total_components=16 matches the schematic. Batteries (BT1/BT2 18650 cells), diodes (D1/D2 for power ORing and protection), fuse (F1 5A), switch (SW1 SPDT), connectors (J1/J2 barrel jacks, J3 battery tester header), ICs (U1 XL4015, U2 HX-2S-JH20 BMS, U3 step-up), and 4 mounting holes (H3-H6) are all correctly identified.

### Incorrect
- connectivity_issues.multi_driver_nets reports GND as having two power_out drivers: U1 pin 4 (OUT-) and U3 pin 4 (OUT-). These are custom module footprints (power converters) where the OUT- terminal is naturally connected to board GND — it is the ground reference of each module's output. This is not a multi-driver conflict but rather two ground-referenced outputs sharing the common ground plane. The alert is a false positive caused by power converter module pins being typed as power_out.
  (connectivity_issues)

### Missed
- The design has U1 (footprint XL4015_StepDown, a 5A buck converter module) and U3 (footprint StepUp12V, a boost module) that form the power conversion chain. signal_analysis.power_regulators is empty. The analyzer lacks sufficient context from the custom module footprint names and blank values ('~') to identify these as power regulators. These are module-level regulators that lack schematic symbol pin names like EN/FB/SW, making detection difficult without value/footprint heuristics.
  (signal_analysis)
- statistics.power_rails only contains ['GND']. The design operates at 2S Li-ion battery voltage (~8.4V max from two 18650 cells) plus has a step-down output and a step-up output (12V). The power nets Net-(D1-A), Net-(U2-P+), etc. represent these voltage rails but are unnamed (no global power symbols for the positive rails). While the KiCad 8 design uses local nets rather than global power symbols for positive rails, the analyzer could flag this as lacking clear VCC/V+ power rail definitions.
  (statistics)

### Suggestions
(none)

---

## FND-00001966: PCB correctly analyzed: 16 footprints, 2-layer board, 85.5x122mm, fully routed; Via-in-pad correctly detected on J3 (BattTester connector); Edge clearance violations correctly flagged for J1 and J2...

- **Status**: new
- **Analyzer**: pcb
- **Source**: battery_ups.kicad_pcb.json
- **Created**: 2026-03-24

### Correct
- footprint_count=16 matches the schematic component count. 2 copper layers (F.Cu, B.Cu), board size 85.5x122mm, 78 track segments, 2 vias, 1 GND zone (filled, F&B.Cu), routing_complete=true, 11 nets. The board has wide traces (1-3mm) appropriate for the battery current levels.
- Two vias within J3 pad courtyard are detected as via-in-pad with same_net=true. J3 is a multi-contact battery tester connector (custom footprint) that apparently uses vias inside pad areas to connect front to back copper. This is a real DFM concern correctly identified.
- Both J1 and J2 (BarrelJack_Horizontal footprints) show edge_clearance_mm=-0.25, meaning their courtyards extend 0.25mm beyond the board edge. This is correct: horizontal barrel jacks are designed to overhang the PCB edge, and the negative clearance is expected but the flag is appropriate for DFM review.
- Board is 85.5x122mm (height 122mm > 100mm threshold), correctly identified as requiring a higher pricing tier at JLCPCB for standard fabrication. The dfm_tier='standard' and violation_count=1 are both accurate.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
