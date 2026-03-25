# Findings: SparkFun_Default_KiCad_Setup / Example-Basic Board_SparkFun_Basic_Board_Example

## FND-00001389: LDO regulator (RT9080-3.3) correctly identified with 3.3V output; I2C bus not detected in bus_analysis despite SCL/SDA nets and Qwiic connector; Component count of 20 total components accurately re...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: SparkFun_Basic_Board_Example.kicad_sch
- **Created**: 2026-03-24

### Correct
- U2 RT9080-3.3 is detected as topology=LDO, input_rail=VCC, output_rail=3.3V, estimated_vout=3.3. This is accurate — the RT9080-3.3 is a fixed 3.3V LDO taking 3.8–6V in. Part count is 20 total components (1 IC, 4 caps, 1 connector, 4 standoffs, 2 TPs, 4 fiducials, 4 logos) which matches the PCB footprint list exactly.
- statistics.total_components=20 and the type breakdown (1 ic, 4 capacitors, 1 connector, 4 standoffs/mounting_holes, 2 test_points, 4 fiducials, 4 other/logos) is consistent with the BOM entries listing U2, C2/C3/C4/C5, J1, ST1–ST4, TP1/TP2, FID1–FID4, G1/G2/G4, and G3/OSHW logo. Power rail list [3.3V, GND, VCC] is correct.
- The design_observations include a decoupling_coverage entry for 3.3V rail with cap_count=2, total_uF=11.0. The power_regulators entry for U2 correctly identifies output_caps C4 (1.0uF) and C5/C2 (10uF on input and output). The nearby_caps in the PCB output also correctly place C3, C4, C2, C5 within ~5mm of U2 on the same layer.

### Incorrect
- G1, G2, G4 (logo/aesthetic symbols with on_board=false) appear in statistics.missing_mpn. Logo and aesthetic symbols that are not on-board should not generate missing MPN warnings since they are mechanical/graphical annotations with no electrical function and no expected MPN. The missing_footprint list for G4 and G2 is similarly spurious for off-board decorative items.
  (statistics)

### Missed
- The schematic has named global labels SCL and SDA connected to a JST Qwiic connector J1 (4-pin, 1mm, I2C). The design_observations correctly categorizes the nets as i2c (clock/data), but bus_analysis.i2c is an empty array []. The SCL and SDA nets each have only one pin (single_pin_nets), which likely causes the I2C bus detector to skip them — but they are clearly I2C interface pins on an output connector and should be reported.
  (design_analysis)

### Suggestions
(none)

---

## FND-00001390: AP3012 boost converter output_rail mis-identified as '3.3V' instead of '5V'; I2C bus with level shifter (BSS138 MOSFETs Q1/Q2) not detected in bus_analysis.i2c; BSS138 gate driver mis-attributed to...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: Example-Qwiic 1U Breakout_SparkFun_Qwiic_1U_Breakout.kicad_sch
- **Created**: 2026-03-24

### Correct
- statistics.total_components=37. The BOM lists: 4 mounting holes, 8 resistors, 4 jumpers, 2 test points, 3 logos/aesthetic, 4 fiducials, 1 diode (D1 LED), 1 Schottky (D2), 2 capacitors, 3 connectors (J1/J2 Qwiic + J3 6-pin), 1 IC (U5), 1 inductor, 2 transistors (Q1/Q2 BSS138). That sums to 37. Power rails [3.3V, 5V, GND, VCC] are all correct.

### Incorrect
- The AP3012 (U5) is a step-up (boost) switching regulator. The PCB netlist confirms a 5V net exists. The analyzer sets input_rail='3.3V' and output_rail='3.3V' — treating it as a buck or non-boosting converter. The inductor L1 and Schottky D2 are in the boost topology, and the output should connect to the 5V net. The output_rail should be '5V', not '3.3V'. This also causes the vout_net_mismatch check to flag the wrong rail.
  (subcircuits)
- transistor_circuits for Q1 and Q2 both list gate_driver_ics=[{reference:'U5', value:'AP3012'}]. The BSS138 gates are connected to the 3.3V power net, not to an output of U5/AP3012. The analyzer is incorrectly propagating gate-net neighbors to find a driving IC, picking up U5 because it shares the 3.3V net. The correct classification is that the gate is pulled to a power rail (3.3V) — there is no gate-driver IC.
  (subcircuits)

### Missed
- This board has a classic bi-directional I2C level-shifter circuit: Q1/Q2 (BSS138 N-MOSFETs) with 2.2k pull-ups (R4/R5/R7/R8) bridging 3.3V SCL/SDA to HV_SCL/HV_SDA. The nets SCL, SDA, HV_SCL, HV_SDA are clearly I2C. The transistor_circuits section detects Q1/Q2 but misidentifies U5 (AP3012) as their gate_driver_ic — it's the 3.3V rail that gates them. bus_analysis.i2c is empty [], missing both the LV and HV sides of the I2C bus.
  (design_analysis)

### Suggestions
(none)

---

## FND-00001391: I2C bus correctly detected in both design_observations and bus_analysis for LIS3DH accelerometer; 25 total components correctly counted for LIS3DH micro breakout; LIS3DH GND pins flagged as multi_d...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: Example-Qwiic Micro Breakout_SparkFun_Example_Micro.kicad_sch
- **Created**: 2026-03-24

### Correct
- design_observations contains two i2c_bus entries for SCL and SDA with device U1 (LIS3DH). bus_analysis.i2c also has both SCL and SDA with device U1. has_pullup=false is correct — this board omits pull-ups (relying on host-side pull-ups per SparkFun Qwiic convention, with JP2 jumper for optional on-board pull-ups). The LIS3DH is correctly identified as the only I2C device.
- statistics.total_components=25. The BOM lists: 4 resistors (R1/R2/R3/R6), 3 logos (G1/G2/G3), 3 jumpers (JP1/JP2/JP3), 3 connectors (J1/J2/J5), 2 fiducials (FID3/FID4), 2 caps (C3/C4), 4 test points (TP5/TP6/TP7/TP8), 1 mounting hole (ST1), 1 IC (U1 LIS3DH), 1 LED (D1). That sums to 25. Power rails [3.3V, GND] are correct for a simple sensor breakout.
- JP3 (ADR jumper, value='ADR', type=SolderJumper_2_Open) connects GND to pin J5.1 (GND side) and to a net that reaches U1 SDO/SA0 pin for I2C address selection. The jumper is correctly categorized as type='jumper'. The LIS3DH SDO pin connection for address selection is properly traced in the component connectivity.

### Incorrect
- connectivity_issues.multi_driver_nets flags 'GND' as having two drivers: U1 pin 12 (GND, power_out) and U1 pin 5 (GND, power_out). IC components with multiple GND pins (common in sensor packages like LGA-16) should not generate a multi-driver warning — both pins are power_in or passive in practice, not competing drivers. This is a false-positive ERC warning that would confuse users.
  (connectivity_issues)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001392: copper_layers_used=3 correctly reflects only 3 of 4 defined layers have actual copper; Unrouted nets correctly identified: 3.3V and VCC are unrouted while GND is covered by zone; board_width_mm and...

- **Status**: promoted
- **Analyzer**: pcb
- **Source**: SparkFun_Basic_Board_Example.kicad_pcb
- **Created**: 2026-03-24

### Correct
- The stackup defines 4 copper layers (F.Cu, In1.Cu, In2.Cu, B.Cu) but copper_layers_used=3 with copper_layer_names=[B.Cu, F.Cu, In1.Cu]. In2.Cu is defined in the layer table but contains no copper (no tracks, no zone coverage — the zone spans only F.Cu/B.Cu/In1.Cu). The GND zone confirming In1.Cu but not In2.Cu validates this count. However, this is a template board and the 4-layer stackup with only 3 used is plausible for an unfinished design.
- routing_complete=false, unrouted_count=2. The 3.3V net (U2.5, C5.1, J1.2, C4.1) and VCC net (U2.1, U2.3, TP2.1, C3.1, C2.1) are listed as unrouted. GND is covered by the ground zone (zone covers F.Cu/B.Cu/In1.Cu, fill_ratio=0.95), which is why it is not in the unrouted list. This is accurate for a SparkFun template in-progress board.
- footprint_count=20 in the PCB matches statistics.total_components=20 in the schematic. The component_groups breakdown (C×4, FID×4, G×4, J×1, ST×4, TP×2, U×1) is consistent. smd_count=16 (all real electrical parts are SMD) and tht_count=0 is plausible since standoffs and fiducials have SMD-classified pads in this library.

### Incorrect
- statistics.board_width_mm=null and board_height_mm=null, yet the dimensions array contains four aligned dimension annotations all reading '50.8 mm' (and 2.5mm corner chamfers). The board_outline section shows edge_count=0 and bounding_box=null, indicating the Edge.Cuts layer has no graphical outline drawn — only dimension annotations exist. The analyzer correctly handles this (no edge = null dimensions), but a more helpful output would note the dimension annotations suggest a 50.8mm × 50.8mm board target.
  (statistics)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001393: 67 PCB footprints vs 37 schematic components explained by 29 kibuzzard decorative footprints; Board dimensions correctly extracted as 25.4mm × 25.4mm (1" × 1") Qwiic standard form factor; routing_c...

- **Status**: promoted
- **Analyzer**: pcb
- **Source**: Example-Qwiic 1U Breakout_SparkFun_Qwiic_1U_Breakout.kicad_pcb
- **Created**: 2026-03-24

### Correct
- The PCB has footprint_count=67 while the schematic has 37 components. The component_groups in the PCB output reveals a 'kibuzzard' group with 29 references — these are PCB-only decorative annotation footprints (version badge, creative commons license, silkscreen artwork) not present in the schematic. The remaining 38 real footprints correspond to the 37 schematic components plus one extra (likely the OSHW/Qwiic logo footprint placed board-only).
- board_width_mm=25.4, board_height_mm=25.4. This is the standard SparkFun Qwiic 1U form factor (1 inch square). The bounding_box shows a rectangular outline from (123.266, 85.406) to (148.666, 110.806), confirming 25.4mm on each side. The Edge.Cuts layer has edge_count=1 (a single rectangle), correctly parsed.

### Incorrect
- The 1U Breakout PCB reports routing_complete=false with unrouted_net_count=16 and track_segments=0. This board is presented as a finished SparkFun example design (rev v10). Either the board genuinely has no copper traces routed (only a GND zone) and relies entirely on copper pours, or the analyzer is failing to detect ratsnest completion in a zone-routed design. Given that the Micro Breakout (a similar template) is fully routed with 90 track segments, the 1U Breakout appears to be a design-in-progress template rather than a finished board.
  (statistics)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001394: Board dimensions 19.05mm × 7.62mm correctly extracted for Micro Breakout form factor; PCB footprint count of 35 matches expected schematic component count of 25 plus board-only items

- **Status**: new
- **Analyzer**: pcb
- **Source**: Example-Qwiic Micro Breakout_SparkFun_Example_Micro.kicad_pcb
- **Created**: 2026-03-24

### Correct
- board_width_mm=19.05mm (0.75") and board_height_mm=7.62mm (0.3"). This matches SparkFun's Qwiic Micro Breakout standard dimensions. Routing is complete (routing_complete=true, unrouted_net_count=0) with 90 track segments and 14 vias on a 2-layer board, which is plausible for a compact 25-component sensor breakout.
- footprint_count=35 vs 25 schematic components. smd_count=17 (functional SMD parts) + tht_count=2 (likely J1/J5 PTH pins) = 19 functional parts, with remaining 16 being board-only decorative/mechanical (fiducials, logos, standoffs, kibuzzard annotations). This is consistent with the Micro Breakout having fewer decorative footprints than the 1U Breakout.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
