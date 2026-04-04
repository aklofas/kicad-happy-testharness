# Findings: Strandjungs_ReactionGame / hardware_Strandjungs_1of5

## FND-00001593: Component count (64), type classification, and power regulator detection are accurate; Assembly complexity reports 51 SMD / 13 THT instead of ~35 SMD / 29 THT; All 5 BUZ11 transistors share the sam...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: repos_Strandjungs_ReactionGame_hardware_Strandjungs_1of5.kicad_sch
- **Created**: 2026-03-24

### Correct
- The schematic correctly identifies 64 total components including 2 ICs (U1=L7805, A1=Arduino_Nano), 4 capacitors, 10 transistors (5 BUZ11 N-MOSFET TO-220 + 5 BC847 SOT-23), 5 rectifier diodes (SM4001), 5 LEDs, 21 resistors, 12 connectors, 3 mounting holes, and 2 switches. The L7805 is correctly detected as a linear power regulator with +12V input and +5V output. Power rails (+12V, +5V, GND) are correct.

### Incorrect
- The assembly_complexity section reports smd_count=51 and tht_count=13. Manual count from footprints gives 35 SMD (4 SMD caps, 5 D_MELF diodes, 5 SOT-23 transistors, 21 R_0603 resistors) and 29 THT (U1 TO-220, 5 BUZ11 TO-220, 5 LED THT, A1 Arduino Nano, 8 terminal blocks, 4 pin headers, 3 mounting holes, 2 switches). The PCB analyzer correctly reports 35 SMD and 26 THT (3 fewer THT because mounting holes are excluded). The schematic assembly analyzer overcounts SMD significantly.
  (assembly_complexity)
- The design has 5 identical switch channels, each with a BUZ11 MOSFET driving a solenoid load and a BC847 NPN transistor driving a status LED. In the transistor_circuits output, all 5 BUZ11 instances (Q2, Q4, Q6, Q8, Q10) report flyback_diode='D7' and led_driver pointing to D8+R12. This is because the hierarchical schematic was flattened and all channels share net aliases; D7 and D8 belong to one specific channel but the analyzer cannot distinguish per-channel assignments. Each channel has its own dedicated flyback diode and LED, not a shared one.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001594: PCB footprint count, SMD/THT split, board dimensions, and routing are accurate; Net count difference between PCB (55) and schematic (52) is expected for hierarchical design

- **Status**: new
- **Analyzer**: pcb
- **Source**: repos_Strandjungs_ReactionGame_hardware_Strandjungs_1of5.kicad_pcb
- **Created**: 2026-03-24

### Correct
- PCB correctly reports 76 total footprints: 35 SMD, 26 THT, 10 board_only (kibuzzard logo graphics), 5 exclude_from_pos (mounting holes, copyright logo). Board is 48.641×80.391 mm, 2-layer, with 209 track segments, 39 vias, 1 copper zone, routing complete. The 76 PCB footprints vs 64 schematic components is explained by 10 decorative board-only graphics and 2 REF** logo footprints.
- The PCB reports 55 nets while the schematic reports 52. This is because the PCB uses hierarchical sheet-qualified net names (e.g. '/Channel 0/MAG_RTN', '/SWITCH0') while the schematic flattens hierarchical nets to shared names (e.g. 'MAG_RTN', 'SWITCH0'). The additional nets in the PCB include unconnected Arduino Nano pins (unconnected-A1-PadXX) which are properly terminated. No false net inflation.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001913: Component inventory correct: 64 total, correct multi-sheet count, type breakdown accurate; All 10 transistor circuits detected with correct topology; Decoupling capacitor values correctly parsed fo...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: Strandjungs_ReactionGame_Strandjungs_1of5.kicad_sch
- **Created**: 2026-03-24

### Correct
- total_components=64 correctly accounts for 5 hierarchical instances of switch_channel.kicad_sch (5×9=45 sub-sheet components) plus 19 main-sheet components. Type breakdown (ic=2, capacitor=4, mounting_hole=3, switch=2, connector=12, resistor=21, diode=5, led=5, transistor=10) is correct. diode=5 (SM4001 diodes D1,D3,D5,D7,D9) and led=5 (LEDs D2,D4,D6,D8,D10) are correctly distinguished. dnp_parts=1 (R16 with value 'dnp') is correct.
- All 5 BUZ11 N-channel MOSFETs (Q2,Q4,Q6,Q8,Q10) detected as type=mosfet with has_flyback_diode=True (correct, SM4001 diodes D1,D3,D5,D7,D9 provide flyback protection). All 5 BC847 NPN BJTs (Q1,Q3,Q5,Q7,Q9) detected as type=bjt with correct emitter_net=GND and appropriate base_resistors (10kΩ each). Load type=resistive for BJTs is correct (collector connects through resistive load). Total 10 transistors detected correctly.
- C1 (1uF) parsed as farads=1e-6, C2 (100n) as farads=1e-7, C4 (10uF) as farads=1e-5, C3 (100n) as farads=1e-7 — all correct. total_capacitance_uF values are accurate (1.1 µF for +12V rail, 10.1 µF for +5V rail). This contrasts with Stock-Ticker-Hardware where Unicode µ values are incorrectly parsed. SI suffix notation (uF, n, p) is handled correctly.
- pwr_flag_warnings correctly identifies +12V and GND rails lacking PWR_FLAG symbols. multi_driver_nets correctly flags +5V as having two power_out drivers: U1 (L7805 OUT pin) and A1 (Arduino Nano +5V pin). These are real ERC considerations for this design.

### Incorrect
- The L7805 (78xx series) is a fixed positive linear voltage regulator with ~2–2.5 V dropout voltage. It is NOT an LDO (Low Dropout Regulator). True LDOs (LM1117, AMS1117, MIC5219) have dropout < 1.3 V. The analyzer assigns topology='LDO' to all linear regulators matched from the Regulator_Linear KiCad library, but 78xx-series parts should be labeled 'linear' or 'fixed_linear'. The input_rail=+12V, output_rail=+5V detection is correct.
  (signal_analysis)

### Missed
- A1 (Arduino Nano) connects to +5V with a power_out pin type (Arduino can source 5V via USB). The power_budget treats power_out components as sources, not loads, so ic_count=0 for +5V. However, when the L7805 is the 5V source (external 5V input to Arduino's VIN or 5V pin), the Arduino consumes up to ~20–50 mA from the +5V rail. The power_budget should estimate the Arduino as a +5V consumer. Also the BUZ11 MOSFETs and their electromagnetic loads on +12V are not estimated (only L7805 quiescent current 10 mA is shown), which severely understates the 12V demand.
  (power_budget)

### Suggestions
(none)

---

## FND-00001914: PCB statistics correct: 76 footprints, 35 SMD, 26 THT, 2-layer

- **Status**: new
- **Analyzer**: pcb
- **Source**: Strandjungs_ReactionGame_Strandjungs_1of5.kicad_pcb
- **Created**: 2026-03-24

### Correct
- footprint_count=76 matches source exactly. smd_count=35 (SMD resistors, capacitors, diodes, transistors) and tht_count=26 (connectors, Arduino, DIP/TO-220 parts) are correct. The remaining 15 footprints are board_only or exclude_from_bom types. front_side=41, back_side=35 are correct per placement. DFM tier=standard with zero violations is accurate for this design.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
