# Findings: Erhannis/VoltageSwitchboard / voltage_tests

## FND-00001666: Component count correct: 7 components (2C, 2R, 1L, 1D, 1 boost IC); Boost converter LM27313XMF not detected as power_regulator; LM27313XMF switching regulator classified as 'switch' instead of 'ic'

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: dc_boost_10v.kicad_sch.json.json
- **Created**: 2026-03-24

### Correct
- The analyzer correctly identified 7 total components matching the schematic: C1_10B1, C2_10B1, R1_10B1, R2_10B1, L1_10B1, D1_10B1, POW1_10B1. Component type breakdown (capacitor:2, resistor:2, inductor:1, diode:1, switch:1) is accurate. VIN, VOUT, and GND power rails are correctly identified.

### Incorrect
- POW1_10B1 (LM27313XMF, Regulator_Switching:LM27313XMF) is a switching boost regulator IC. The analyzer assigns it type 'switch' based on keyword or library matching, but it should be classified as 'ic' (or a switching regulator subtype). This cascades to: (1) it is excluded from ic_pin_analysis, (2) it is excluded from power_regulators detection, (3) the feedback resistor divider on FB is not detected. The same error applies to dc_boost_8_5v's POW1_85B1.
  (statistics)

### Missed
- POW1_10B1 (LM27313XMF) is a switching boost regulator from lib Regulator_Switching, but it is classified as type 'switch' rather than 'ic'. Because the power_regulator detector only runs on 'ic'-typed components, it is entirely absent from signal_analysis.power_regulators. The resistor divider on the FB pin (R1 100k from VOUT to FB, R2 14k from FB to GND) is also not detected as a voltage_divider or feedback_network. Both dc_boost_10v and dc_boost_8_5v have this same miss.
  (signal_analysis)

### Suggestions
- Fix: LM27313XMF switching regulator classified as 'switch' instead of 'ic'

---

## FND-00001667: Component count and net topology correct for 8.5V boost design

- **Status**: new
- **Analyzer**: schematic
- **Source**: dc_boost_8_5v.kicad_sch.json.json
- **Created**: 2026-03-24

### Correct
- 7 components correctly identified (same topology as dc_boost_10v but R2 differs: 16k vs 14k). Net structure (GND, VIN, VOUT, unnamed SW node, unnamed FB node) matches the schematic. Decoupling capacitors on VIN and VOUT are correctly identified.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001668: LDO regulator correctly detected with LM337L_SO8; design_observation incorrectly reports missing caps on LDO input/output rails

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: negative_ldo_-10v.kicad_sch.json.json
- **Created**: 2026-03-24

### Correct
- POW1_N10L1 (LM337L_SO8) is correctly detected as topology 'LDO' in signal_analysis.power_regulators with input_rail '-VIN' and output_rail '-VOUT'. The ic_pin_analysis correctly identifies the ADJ pin connected to R1B (75 ohm) and R2 (240 ohm). 6 components total is correct.

### Incorrect
- The design_observation with category 'regulator_caps' reports {"missing_caps": {"input": "-VIN", "output": "-VOUT"}} for POW1_N10L1. However, C1_N10L1 (10uF) is present on -VIN and C2_N10L1 (10uF) is present on -VOUT, confirmed by ic_pin_analysis.decoupling_caps_by_rail. The decoupling_analysis array is empty (because -VIN and -VOUT are not recognized as power rails by the decoupling detector), causing the design_observation to falsely flag missing caps that are actually present and correctly wired. Same error in negative_ldo_-11v.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001669: Negative LDO -11V correctly identified with different top resistor (1.8k vs 1.6k)

- **Status**: new
- **Analyzer**: schematic
- **Source**: negative_ldo_-11v.kicad_sch.json.json
- **Created**: 2026-03-24

### Correct
- 6 components correctly identified. R1A_N11L1 is 1.8k (vs 1.6k in the -10V variant), correctly captured. LDO topology, input/output rails, and ADJ feedback network are all correct. The power_regulators entry for POW1_N11L1 is accurate.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001670: Fixed 1.8V LDO (APE8865N) correctly detected with estimated_vout=1.8; LDO output voltage correctly estimated at 1.8V from part name suffix

- **Status**: new
- **Analyzer**: schematic
- **Source**: positive_ldo_1v8.kicad_sch.json.json
- **Created**: 2026-03-24

### Correct
- POW1_P1V8L1 (APE8865N-18-HF-3) is correctly identified as an LDO with estimated_vout=1.8 via fixed_suffix detection. Input/output rails VIN and VOUT are correct. Input and output decoupling capacitors (C1_P1V8L1 and C2_P1V8L1) are correctly found in decoupling_analysis. 3 components total is correct.
- The APE8865N-18-HF-3 has '-18-' in its name indicating 1.8V output. The analyzer correctly extracts this as estimated_vout=1.8 with vref_source='fixed_suffix'.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001671: THT pin header connector misclassified as SMD in assembly_complexity; Single connector with all 3 pins on net IN correctly parsed

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: splitter_3.kicad_sch.json.json
- **Created**: 2026-03-24

### Correct
- The splitter sheet contains only J1_3S9 (3-pin connector), correctly identified as 1 component. All 3 pins are correctly connected to a single 'IN' net (this is a short/jumper-style schematic where all pins are tied together). Hierarchical label 'IN' with shape 'input' is correctly captured.

### Incorrect
- J1_3S9 uses footprint Connector_PinHeader_2.54mm:PinHeader_1x03_P2.54mm_Vertical, which is a through-hole (THT) part. The assembly_complexity section reports smd_count=1, tht_count=0 and package_breakdown={'other_SMD': 1}. This is wrong — a vertical pin header is THT, not SMD. It should appear as tht_count=1.
  (assembly_complexity)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001672: AP2112K-3.3 LDO regulator correctly detected with 3.3V estimated output; USBLC6-2P6 ESD protection device not detected in protection_devices

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: usb_micro_b.kicad_sch.json.json
- **Created**: 2026-03-24

### Correct
- REG1_UM1 (AP2112K-3.3) is correctly detected as an LDO with input_rail='+5V', output_rail='+3V3', and estimated_vout=3.3 via fixed_suffix. The +5V USB input and +3V3 output rails are correctly identified. 8 components total (1 USB connector, 3 resistors, 2 caps, 1 ESD, 1 LDO) is correct.

### Incorrect
(none)

### Missed
- ESD1_UM1 (USBLC6-2P6) is an ESD protection IC from lib Power_Protection:USBLC6-2P6 placed on the USB data lines. It is classified as type 'other' and is absent from signal_analysis.protection_devices. This is a missed detection — the USBLC6-2P6 is a well-known USB ESD protection part and should appear in protection_devices.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00001673: TC7662Bx0A charge pump correctly detected as switching regulator with V- output; design_observation falsely reports missing output cap for V- rail

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: voltage_inverter.kicad_sch.json.json
- **Created**: 2026-03-24

### Correct
- POW1_VI1 (TC7662Bx0A) is correctly detected in power_regulators with topology='switching' and output_rail='V-'. The flying capacitor connections (CAP+/CAP- to C1_VI1) and input/output caps (C3 on V+, C2 on V-) are correctly mapped in ic_pin_analysis. 4 components total is correct.

### Incorrect
- The design_observation with category 'regulator_caps' reports {"missing_caps": {"output": "V-"}} for POW1_VI1. However, C2_VI1 (10uF) is connected to V- as confirmed by ic_pin_analysis (pin 5 VOUT on V- has decoupling_caps=[C2_VI1]). The decoupling_analysis correctly shows C3_VI1 on V+ but misses V- because the net name 'V-' is not recognized as a power rail by the decoupling detector. The cap is present and correctly wired; the observation is incorrect.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001674: voltage_inverter_alt TC7662Bx0A correctly detected with 6 components

- **Status**: new
- **Analyzer**: schematic
- **Source**: voltage_inverter_alt.kicad_sch.json.json
- **Created**: 2026-03-24

### Correct
- 6 components (3 caps, 1 IC, 2 Schottky diodes) correctly identified. TC7662Bx0A detected as switching regulator. D1_VIA1 and D2_VIA1 are Schottky diodes used as external rectifiers to extend the output voltage range, correctly parsed. 3 no_connect markers on BOOST, LV, OSC pins are correctly counted.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001675: Top-level hierarchical schematic: 68 components across all sub-sheets correctly aggregated; Two boost converter regulators (LM27313XMF x2) missing from power_regulators in top-level schematic; Powe...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: voltage_tests.kicad_sch.json.json
- **Created**: 2026-03-24

### Correct
- The voltage_tests top-level schematic aggregates all sub-sheets. 68 total components is correct (7+7+6+6+3+4+6+8+1 sub-sheet components = 48 plus 17 connectors + 3 extras from USB sub-sheet). Component types: connector:18, capacitor:18, resistor:13, ic:6, diode:4, switch:2, inductor:2, mounting_hole:4, other:1 are all accurate. 46 nets and 241 wires match the hierarchical design.

### Incorrect
- The statistics.power_rails list includes items like '/201ab4ae-b835-4fcf-b591-c6b37cf9a2b1/VIN' and '/7cdd2df5-332b-4860-ac66-fea4c590218c/V+' instead of the human-readable sheet names (e.g., '/DC Boost 10v/VIN'). This makes the power rail list harder to interpret. The power_net_routing section in the PCB output uses the correct readable names ('/DC Boost 10v/VIN'), confirming the schematic analyzer is not resolving sheet names from the hierarchical sheet labels.
  (statistics)

### Missed
- voltage_tests aggregates all sub-sheets and finds 6 power_regulators, but should find 8: LM337L_SO8 x2 (negative LDOs), APE8865N-18-HF-3 x1 (positive LDO), AP2112K-3.3 x1 (USB LDO), TC7662Bx0A x2 (inverters), LM27313XMF x2 (boost converters). POW1_10B1 and POW1_85B1 are missing because they are typed 'switch' not 'ic'. This is the same issue as in the individual dc_boost schematics.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00001676: PCB correctly identified as 4-layer board with 68 footprints; Board dimensions 68.58mm x 63.5mm correctly extracted; DFM analysis: standard tier, 0 violations, correct minimum track/drill metrics; ...

- **Status**: promoted
- **Analyzer**: pcb
- **Source**: voltage_tests.kicad_pcb.json.json
- **Created**: 2026-03-24

### Correct
- copper_layers_used=4 (F.Cu, In1.Cu, In2.Cu, B.Cu) is correct. footprint_count=68 matches the schematic component count. routing_complete=True and unrouted_net_count=0 are correct — the board is fully routed. 258 track segments, 23 vias, 6 zones are accurately reported.
- The board_width_mm=68.58 and board_height_mm=63.5 are correctly extracted from the board outline. These are reasonable dimensions for a multi-supply voltage switchboard PCB.
- dfm_tier='standard' is correct for a 4-layer board with min_track_width_mm=0.2, min_drill_mm=0.4, min_annular_ring_mm=0.2. These are standard JLCPCB/PCBWay design rules. violation_count=0 is consistent with a production-ready board.
- thermal_analysis.zone_stitching correctly identifies two filled zones: GND on In1.Cu (3961.5 mm², 18 vias) and +3V3 on In2.Cu (3961.5 mm², 3 vias). This is a typical 4-layer stackup with power/ground planes on the inner layers. Via densities are accurately reported.
- connectivity reports total_nets_with_pads=46, routed_nets=34 (some nets are routed via copper pours/zones rather than discrete tracks), unrouted_count=0, routing_complete=True. This is consistent with a board using internal copper pour planes for power/ground nets.

### Incorrect
- The statistics report smd_count=47, tht_count=17 (total 64), but footprint_count=68. The 4 missing are the mounting holes (H1-H4), which are NPTH (non-plated through holes) with no pads. These are not counted in either smd_count or tht_count, creating an apparent discrepancy. The analyzer should either count NPTH footprints separately or note this in the statistics.
  (statistics)

### Missed
(none)

### Suggestions
(none)

---
