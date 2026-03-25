# Findings: STM32-KICAD-DESIGN / stm32 design

## FND-00001342: AO3401A P-channel MOSFET incorrectly classified as N-channel (is_pchannel: false); MP2359DJ switching regulator feedback net reported as BUCK_SW instead of BUCK_FB; Crystal Y1 (16MHz) load caps cor...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: stm32 design.sch.json
- **Created**: 2026-03-24

### Correct
- Y1 (16MHz HSE crystal) correctly identifies C3 and C1 (both 12pF) as load caps, computes effective_load_pF=9.0. The 12pF caps giving 9pF effective load (6pF series + 3pF stray) is a standard and correct calculation for a 16MHz MCU crystal circuit.
- I2C1_SDA and I2C1_SCL nets are both detected as i2c_bus in design_observations, with R2 as SDA pull-up and R5 as SCL pull-up, both connected to the +3.3VA rail. This is accurate for a properly configured I2C bus on an STM32 design.
- 50 total components parsed with correct breakdown: 16 caps, 3 ICs (STM32F405, MP2359DJ, USBLC6), 11 resistors, 2 inductors, 2 LEDs, 1 crystal, 1 fuse, 1 transistor, 1 ferrite bead, 2 diodes, 5 connectors, 4 mounting holes. All counts match the BOM section and component list.

### Incorrect
- Q1 is an AO3401A which is a P-channel MOSFET (confirmed by its datasheet — AO3401A is a P-ch MOSFET in SOT-23). The analyzer reports is_pchannel=false. Additionally, gate_net and source_net are both reported as '__unnamed_52', which suggests a pin connectivity parsing error — gate and source cannot share the same net in a functional circuit.
  (signal_analysis)
- U2 (MP2359DJ) is a step-down converter. The analyzer reports fb_net='BUCK_SW' (the switch node) instead of the correct feedback net 'BUCK_FB'. BUCK_FB is the actual feedback divider output connected to the FB pin of U2. BUCK_SW is the switching node (inductor drive), not the feedback net. This is a pin mapping error in the switching regulator detector.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001343: 4-layer PCB dimensions correctly match gerber Edge.Cuts extents; Inner power planes correctly identified as GND (In1) and +3.3VA (In2); Net count discrepancy between schematic (85) and PCB (79) is ...

- **Status**: new
- **Analyzer**: pcb
- **Source**: stm32 design.kicad_pcb.json
- **Created**: 2026-03-24

### Correct
- PCB reports board_width_mm=66.04 and board_height_mm=67.945. The gerber output reports Edge.Cuts width=66.04mm and height=67.945mm (from bounding_box). These match exactly, confirming correct board outline extraction from the legacy KiCad 5 format file.
- The 4-layer stackup correctly identifies In1.Cu as type='power' (GND plane) and In2.Cu as type='power' (+3.3VA plane). The thermal analysis confirms GND zone on In1.Cu and +3.3VA zone on In2.Cu, each covering ~4487mm² (nearly full board area). This is a correct dedicated power plane identification.
- Schematic reports 85 nets but PCB has 79 nets. The difference (6 nets) is accounted for by schematic-only power rails and unconnected symbol nets that don't appear in the physical layout. This is a normal pattern for KiCad 5 designs where some schematic power flags and unconnected pins create phantom nets.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001344: 4-layer gerber set correctly identified as complete with all required layers present; Drill classification correctly identifies 117 vias, 8 component holes, 2 NPTH, and 4 mounting holes; Gerber ali...

- **Status**: promoted
- **Analyzer**: gerber
- **Source**: Gerber.json
- **Created**: 2026-03-24

### Correct
- 11 Gerber files parsed: F.Cu, B.Cu, In1.Cu, In2.Cu, F.Mask, B.Mask, F.Paste, B.Paste, F.SilkS, B.SilkS, Edge.Cuts. Both PTH and NPTH drill files present. completeness.complete=true with missing_required=[] and missing_recommended=[]. This is correct for a standard 4-layer KiCad design.
- Total 133 holes: 117 vias (0.4mm drill), 8 PTH component holes (0.5mm), 2 NPTH (0.9mm), 2 larger PTH (1.2mm), 4 mounting holes (2.2mm). The classification heuristic correctly separates these categories. The drill_tools section faithfully records 0 holes for tools T3 (0.5994mm) and T4 (0.6502mm), indicating unused tool definitions in the drill file.
- pad_summary reports 50 SMD apertures (SMDPad flashes), 340 via apertures, 12 THT holes, smd_ratio=0.81. This is consistent with 50 SMD component pads out of 62 total component pads (50+12=62), yielding 50/62=0.81. The design is predominantly SMD as expected for an STM32 board.
- Gerber reports board_dimensions width_mm=66.04 and height_mm=67.94 (source: edge_cuts_extents), matching the PCB analyzer output of board_width_mm=66.04 and board_height_mm=67.945 to within rounding. Cross-file consistency is maintained.

### Incorrect
- The analyzer flags alignment as failed because F.SilkS width is 70.526mm vs Edge.Cuts width of 66.04mm (4.5mm wider) and height 64.588mm vs 67.945mm. Silkscreen deliberately extends slightly beyond the board outline to include reference designators near edge-mounted components. The ~4.5mm overhang on F.SilkS is normal for silkscreen text of edge connectors. The B.Paste and B.SilkS having 0-width extents (no back-side SMD or back silkscreen content) is also normal for an all-front-side SMD design. The misalignment flag is over-sensitive for silkscreen layers.
  (alignment)

### Missed
(none)

### Suggestions
(none)

---
