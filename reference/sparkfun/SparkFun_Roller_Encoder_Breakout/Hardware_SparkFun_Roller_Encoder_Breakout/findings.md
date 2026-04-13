# Findings: sparkfun/SparkFun_Roller_Encoder_Breakout / Hardware_SparkFun_Roller_Encoder_Breakout

## FND-00001477: Component count, types, and net topology correctly captured for simple breakout; Roller encoder SW1 with quadrature outputs A, B and switch S1/S2 correctly wired to J1; assembly_complexity incorrec...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: SparkFun_Roller_Encoder_Breakout.kicad_sch
- **Created**: 2026-03-24

### Correct
- 9 total components: SW1 (roller encoder switch), J1 (4-pin connector), ST1-ST4 (standoffs), G1 (OSHW logo, not in BOM), G3/G5 (SparkFun logos). 4 nets (A, B, SWITCH, GND) all correct. BOM has 4 real parts (excluding G1 which is exclude_from_bom). All pin connections accurately traced.
- All 5 pins of SW1 correctly connected: A→J1 pin 2, B→J1 pin 1, S1→J1 pin 3 (SWITCH net), C→GND, S2→GND. The net topology exactly matches the schematic. J1 pin 4 correctly mapped to GND.
- The schematic uses global_label with shape=input for A, B, and SWITCH nets. On a passive breakout with no driving IC, these inputs are technically undriven. The analyzer correctly flags all three as undriven_input_label warnings, which is accurate ERC-style analysis.

### Incorrect
- J1 is a through-hole 4-pin connector (confirmed in PCB output where J1 type=through_hole). The assembly_complexity section shows smd_count=9, tht_count=0, which is incorrect. The connector J1 should be counted as THT. This appears to be a schematic-side heuristic that doesn't have access to PCB footprint type information.
  (assembly_complexity)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001478: PCB footprint count of 23, board dimensions 25.4mm x 25.4mm, and routing correctly captured; B.Cu layer type reported as 'jumper' instead of 'signal'; Standoff footprints ST1-ST4 classified as 'smd...

- **Status**: promoted
- **Analyzer**: pcb
- **Source**: SparkFun_Roller_Encoder_Breakout.kicad_pcb
- **Created**: 2026-03-24

### Correct
- The small 1-inch square PCB (25.4x25.4mm) has 23 footprints: SW1, J1, ST1-4, G1 (OSHW logo), 2x G*** SparkFun logos, Ref**, and 13 kibuzzard decorative graphics. routing_complete=true, 4 nets, 11 track segments, 0 vias, all correct.
- The single GND zone correctly covers both F.Cu and B.Cu layers, is filled, has outline_area=645.16mm2 matching the 25.4x25.4mm board, filled_area=1110.77mm2 (counting both layers), fill_ratio=1.722 (sum of both layers relative to outline area). J1 and SW1 correctly identified as connected to GND domain.

### Incorrect
- In the layers array, B.Cu (layer number 2) has type='jumper' rather than type='signal'. KiCad 9.0 uses a different internal layer type numbering for back copper in this board. The layer is a standard signal copper layer and should be classified as 'signal'. This may cause downstream analysis to treat B.Cu differently from F.Cu.
  (statistics)
- ST1-ST4 use the SparkFun-Hardware:Standoff footprint and each has a single pad (pad_count=1) but are classified as type='smd'. These are mechanical mounting holes/standoffs — they have no electrical connections (pad_nets={}, connected_nets=[]) and represent physical drill features, not SMD pads. They should be classified as mounting_hole or through_hole.
  (statistics)
- The edge_clearance_warnings list includes G1 with edge_clearance_mm=-71.75, suggesting it is 71.75mm outside the board outline. G1 is the OSHW logo in the schematic-only area of the PCB file and has no sch_path link. Its position (232.41, 159.385) is indeed far outside the 135-161mm board boundary. This is expected for decorative/documentation symbols placed off-board; the warning is correct but may be noise for the use case.
  (placement_analysis)

### Missed
(none)

### Suggestions
- Fix: B.Cu layer type reported as 'jumper' instead of 'signal'
- Fix: Standoff footprints ST1-ST4 classified as 'smd' type instead of mounting hole

---
