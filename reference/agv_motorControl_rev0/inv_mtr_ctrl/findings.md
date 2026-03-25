# Findings: agv_motorControl_rev0 / inv_mtr_ctrl

## FND-00001980: Three-phase bridge circuit correctly detected with correct MOSFET assignments; bridge_circuits.driver_ics is empty — DRV8328B (U1) not recognized as gate driver IC; VDSLVL voltage divider (R3=141k/...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: inv_mtr_ctrl.kicad_sch.json
- **Created**: 2026-03-24

### Correct
- signal_analysis.bridge_circuits correctly identifies a three_phase topology with 3 half-bridges: (Q1/Q2 → SHA), (Q3/Q4 → SHB), (Q5/Q6 → SHC), all driven from VDC rail. This matches the actual design with 6× BSC067N06LS3G N-MOSFETs in a 3-phase bridge driven by DRV8328B.
- Analyzer detects voltage_dividers with R3(141kΩ)/R4(10kΩ) from VCC to GND producing ratio 0.066, with midpoint connected to U1 pin 26 (VDSLVL — voltage drain sense level). This is a correct identification of the threshold-setting divider for the DRV8328B's drain-source overvoltage protection.
- statistics.dnp_parts:17 matches the schematic where D1/D2/D3 (Zener clamps, DNP), C9/C10/C12-C17 (bulk/snubber caps, DNP), and R17-R22 (snubber resistors, DNP) are marked Do Not Place for initial prototype testing.
- signal_analysis.decoupling_analysis correctly identifies the VDC rail with C1(10uF), C2(.1uF), C8(100uF), C9(100uF), C10(100uF), C11(.01uF) for 310.11uF total. Note: C9/C10 are DNP in the schematic; the analyzer includes DNP parts in the decoupling analysis which may inflate the 'active' capacitance.
- statistics.power_rails: ['GND', 'VCC', 'VDC']. The VCC rail powers logic (U1 DRV8328B), while VDC is the high-voltage motor bus powering all MOSFET drains. M_GND is a separate motor ground seen in the nets but not listed as a power rail (it connects only to the motor connector J9 pins 3/4).

### Incorrect
- signal_analysis.bridge_circuits[0].driver_ics:[] despite U1=DRV8328B being a dedicated gate driver IC for this 3-phase bridge (connected to all 6 MOSFET gates via GHA/GHB/GHC/GLA/GLB/GLC nets). The DRV8328B provides bootstrap gate driving directly to the 6 gate resistors. The analyzer fails to associate U1 with the bridge.
  (signal_analysis)
- The analyzer detects R6(31Ω)/R8(10kΩ) as a 'voltage divider' (ratio 0.99691, top_net GLA, bottom GND). R6 is actually a gate resistor (between GLA driver output and MOSFET gate Q2), and R8 is a 10kΩ pull-down to GND (to discharge the gate when driver is off). This is a gate drive circuit, not a voltage divider. The 31Ω/10kΩ pair appears across 5 more gate drive pairs.
  (signal_analysis)
- The title_block.title says 'DRV8323 Development Board' but the lib_id for U1 is 'DRV_controllers:DRV8328B' (DRV8328B is a simplified gate driver vs DRV8323 which has SPI interface). The analyzer does not flag this component/title mismatch as a design observation. This is a real discrepancy in the source design worth noting.
  (title_block)

### Missed
- The schematic has 16 test_points (component_types.test_point:16) but in the PCB output, component_groups shows only 1 test point (TP8). The remaining test points likely use net/power tie symbols with no PCB footprint, or TP pads that are tracked differently. The schematic-to-PCB component count mismatch for test points warrants a design observation.
  (statistics)

### Suggestions
(none)

---

## FND-00001981: 4-layer board correctly detected with F.Cu, In1.Cu, In2.Cu, B.Cu; 72 footprints detected vs 78 schematic components — discrepancy explained by mounting holes (in_bom:false); 16 copper zones detecte...

- **Status**: new
- **Analyzer**: pcb
- **Source**: inv_mtr_ctrl.kicad_pcb.json
- **Created**: 2026-03-24

### Correct
- Analyzer reports copper_layers_used:4 with correct layer names. A 4-layer stackup is appropriate for this power electronics board requiring separate power planes (likely VDC on In1.Cu, GND on In2.Cu) for current handling and EMI reduction.
- statistics.footprint_count:72 vs schematic total_components:78. The 4 mounting holes (H1-H4) have in_bom:false in the schematic. The 17 DNP parts still get footprints placed on PCB. The gap of 6 is larger than 4; some DNP test points may also lack PCB footprints. This is reasonable.
- zone_count:16 zones on a 4-layer board with VDC bus, GND, and phase output (SHA/SHB/SHC) copper pours. Large copper zones are essential for current handling in a 3-phase motor driver with high-current MOSFETs.
- statistics.routing_complete:true with unrouted_net_count:0 for all 54 nets. The 260 track segments and 133 vias provide connectivity across the 4-layer power board.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
