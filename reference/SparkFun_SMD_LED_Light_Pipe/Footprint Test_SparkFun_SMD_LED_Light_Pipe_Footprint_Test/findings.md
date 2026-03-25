# Findings: SparkFun_SMD_LED_Light_Pipe / Footprint Test_SparkFun_SMD_LED_Light_Pipe_Footprint_Test

## FND-00001479: APA102 addressable LED chain of 4 LEDs (D5-D8) correctly detected with SPI protocol; Component counts correct: 10 total, 6 LEDs (4 APA102 + 1 Blue + 1 White), 2 resistors, 1 connector, 1 logo; Curr...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: SparkFun_SMD_LED_Light_Pipe_Footprint_Test.kicad_sch
- **Created**: 2026-03-24

### Correct
- The signal_analysis.addressable_led_chains correctly identifies one chain of 4 APA102-2020 LEDs (D8→D7→D6→D5), data_in_net='APA102 DAT', protocol='SPI (APA102)', estimated_current_mA=160. The daisy-chain topology with CI/CO and DI/DO connections is correctly traced. D5 is correctly noted as the last LED with CO/DO floating.
- The design has D2 (Blue 0603), D4 (White 1206), D5-D8 (APA102-2020 addressable), R1 and R2 (330 ohm current limiting), J1 (4-pin connector), G1 (SparkFun logo, not on board). All component types and quantities correctly reported in statistics and BOM.
- D5 is the last LED in the chain. Its CO (pin 1) and DO (pin 4) are correctly mapped to single-element nets '__unnamed_4' and '__unnamed_6' respectively, each with only that pin. This accurately reflects the intentional open-circuit termination of the daisy chain.
- J1 correctly provides 3.3V (pin 1), APA102 CLK (pin 2), APA102 DAT (pin 3), and GND (pin 4). The APA102 CLK and APA102 DAT nets correctly enter D8 CI and DI pins respectively as the start of the chain. ERC warning for missing driver on these nets is appropriate since J1 is a passive connector.

### Incorrect
(none)

### Missed
- R1 and R2 are 330 ohm resistors placed in series between GND and the cathodes of D4 (White 1206) and D2 (Blue 0603) respectively, with anodes at 3.3V. These are classic LED current-limiting resistors. The signal_analysis has no entry for these simple LED drive circuits, and no protection_devices or other detection captures them. The design_observations section is also empty.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00001480: PCB footprint count of 21 and all component groups correctly identified; Dual-zone copper fill correctly detected: GND on F.Cu and 3.3V on B.Cu; Track segment count of 111 (71 linear + 40 arcs) cor...

- **Status**: new
- **Analyzer**: pcb
- **Source**: SparkFun_SMD_LED_Light_Pipe_Footprint_Test.kicad_pcb
- **Created**: 2026-03-24

### Correct
- 21 footprints: D2, D4, D5, D6, D7, D8 (6 LEDs), R1, R2 (2 resistors), J1 (connector), G*** (SparkFun logo), 2x REF** (light pipe holders with pads), 1x REF** (4-gang light pipe holder), 8 kibuzzard decoration footprints. All identified correctly in component_groups.
- The board has two copper pours: a GND zone on F.Cu (front) with fill_ratio=0.579 and a 3.3V zone on B.Cu (back, priority=1) with fill_ratio=0.753. Both zones cover the full board outline (702.42mm2). Via stitching for 3.3V is correctly detected with 6 vias at 0.6mm/0.3mm drill in the thermal_analysis section.
- The tracks section reports segment_count=71 and arc_count=40, totaling 111 which matches statistics.track_segments=111. The arc tracks are used for routing in the LED/light-pipe area. Total length 70.66mm and all tracks on F.Cu are consistent with the single-layer routing above the 3.3V back-copper plane.
- The PCB has 14 nets total. routed_nets=12 and unrouted_count=0 means routing is complete — the 2 'unconnected-' nets (D5 CO and DO) are stubs that have only one pad each and no ratsnest to route. routing_complete=true is correct. The 2-net discrepancy between total_nets_with_pads=14 and routed_nets=12 is properly handled.
- The placement_analysis correctly identifies 4 courtyard overlaps: D4 with REF** (10.214mm2), REF** with D2 (4.322mm2), R2 with REF** (2.161mm2), R1 with REF** (2.161mm2). These overlaps are intentional as the SMD light pipe holder clips over the LED, so the analyzer is correct to report them but the design intent is deliberate.
- power_net_routing correctly identifies GND with 5 track segments at 0.3048mm width (12 mil) on F.Cu, complemented by the GND copper pour. The 3.3V net is not in power_net_routing since it only exists as a back-copper zone with via connections, which is correct.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
