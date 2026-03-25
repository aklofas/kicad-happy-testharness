# Findings: Voltage_reference / reference_board

## FND-00001749: Component count (23) and type breakdown correctly extracted from hierarchical schematic; Net count (20) and BOM extraction are correct; LT1001 (U3) opamp classified as 'comparator_or_open_loop' but...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: reference_board.kicad_sch.json.json
- **Created**: 2026-03-24

### Correct
- The analyzer correctly counts 23 total components spanning the top-level sheet (J1, U1, LOGO1, H1, C1, #LOGO1, #SYM1) and the LM399.kicad_sch sub-sheet (U2, U3, R1, R2, C2–C6, D1, NT1–NT5, RN1). Component type breakdown (connector=1, ic=3, graphic=1, mounting_hole=1, capacitor=6, other=2, resistor=2, net_tie=5, resistor_network=1, diode=1) sums to 23 and matches the source.
- 20 nets are correctly extracted from the hierarchical schematic, including hierarchical port nets with UUID-qualified names. BOM entries for all 14 in-BOM components are correctly listed with values, footprints, references and types.
- decoupling_analysis correctly identifies V3.3 with C1 (100n, 15.9 MHz SRF). U1 (TMP236 temperature sensor) runs on V3.3 and has one bypass capacitor — this is accurately reflected.

### Incorrect
- The analyzer reports configuration='comparator_or_open_loop' for U3 (LT1001/OP07). In reality U3 is a non-inverting amplifier: the output (Vout / U3.pin6) feeds back through NT4 (net tie) to RN1.pin3, then the RN1 midpoint (pin2) connects to U3.pin2 (inverting input), forming a classic non-inverting gain stage. The feedback path is invisible to the analyzer because NT4 is a net tie that creates a separate net (__unnamed_6) between Vout and RN1.pin3, breaking the net-level feedback chain. This is a Kelvin-sense (4-wire) design pattern that defeats the opamp feedback detector.
  (signal_analysis)
- design_analysis.power_domains.ic_power_rails.U3 lists power_rails=['Vout']. However Vout is U3's output signal (pin6), not its power supply. U3's true power pins are pin7 (V+, power_in) connected to net '/…/V-heater+' and pin4 (V-, power_in) connected to '/…/V_heater-'. These hierarchical port nets are classified as 'output_drive' not 'power', so the power domain mapper erroneously latches onto 'Vout' (which IS in power_rails). This cascades into a false decoupling warning claiming U3 has no decoupling cap on Vout.
  (design_analysis)
- signal_analysis.design_observations contains a 'decoupling' warning for U3 (LT1001) with rails_without_caps=['Vout']. This is incorrect: Vout is U3 pin6 (output), not a power supply. The actual supply rails V-heater+ and V_heater- (hierarchical port nets) do have decoupling caps (C4 for V+, C5 for V-). The warning arises from the erroneous power domain mapping discussed above.
  (signal_analysis)

### Missed
- feedback_networks is empty. RN1 (17k/20k VoltageDivider symbol) forms a feedback divider from U3's output (Vout) to U3's inverting input (__unnamed_7), traversing NT4 (net tie). The net tie boundaries prevent the feedback network detector from tracing the path. This is a missed detection: the design has a clear resistor-divider feedback network that sets the gain of the LT1001.
  (signal_analysis)

### Suggestions
- Fix: LT1001 (U3) opamp classified as 'comparator_or_open_loop' but is a non-inverting amplifier

---

## FND-00001750: Component count (16) correctly extracted from sub-schematic; LT1001 (U3) opamp classified as 'comparator_or_open_loop' in sub-schematic — same misclassification as parent; V- (LT1001 negative suppl...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: LM399.kicad_sch.json.json
- **Created**: 2026-03-24

### Correct
- The sub-schematic (LM399.kicad_sch) contains 16 components: U2 (LM399), U3 (LT1001), R1, R2, C2, C3, C4, C5, C6, D1, NT1, NT2, NT3, NT4, NT5, RN1. The analyzer correctly counts these and classifies types (ic=2, resistor=2, capacitor=5, net_tie=5, resistor_network=1, diode=1).
- The subcircuits section correctly identifies U2 (LM399) as a subcircuit center with neighbors C2, C3, NT1, NT2, NT5, R1, and U3. This accurately reflects the Kelvin-sense current source and voltage buffer cluster surrounding the buried zener reference.
- All five net tie components (NT1–NT5, Device:NetTie_2) are correctly classified as type='net_tie' and excluded from in_bom counts. This is correct: net ties are PCB-level connection elements, not real BOM components.

### Incorrect
- The sub-schematic analysis independently misclassifies U3 (LT1001) as 'comparator_or_open_loop'. The feedback path from V_zener- (output) through NT4 to RN1.pin3, then RN1.pin2 to U3 inverting input is again broken by the net tie boundary. The true configuration is non-inverting amplifier with gain set by RN1 (17k/20k). Both the top-level and sub-schematic analyses make the same error.
  (signal_analysis)

### Missed
- statistics.power_rails lists only ['GND', 'V+']. V- (connected to U3.pin4, type power_in) is absent. In net_classification V- is labeled 'signal' rather than 'power'. Because V- is a hierarchical port with no explicit power symbol in the sub-sheet, the analyzer does not recognize it as a supply rail. Consequently C5 (100n on V-) is not reported in decoupling_analysis, and the negative supply of the LT1001 appears unmonitored.
  (signal_analysis)

### Suggestions
- Fix: LT1001 (U3) opamp classified as 'comparator_or_open_loop' in sub-schematic — same misclassification as parent

---

## FND-00001751: Footprint count (21), SMD (11), THT (3), and board dimensions (34x25mm) are all correct; Via count (5), zone count (1), routing complete with 0 unrouted nets; DFM tier 'standard' with 0 violations ...

- **Status**: new
- **Analyzer**: pcb
- **Source**: reference_board.kicad_pcb.json.json
- **Created**: 2026-03-24

### Correct
- 21 footprints exactly matches the PCB file. SMD=11 (C1–C6, R1, R2, D1, U1, U3) and THT=3 (J1, U2/LM399, RN1) are correct; H1 (mounting hole), NT1–NT5, and LOGO1 are correctly excluded from the SMD/THT count as mechanical/non-component items. Board dimensions 34.0×25.0mm match the dimension annotations in the PCB.
- Via count 5 matches 5 board-level (via ...) entries in the PCB source. Zone count 1 (GND fill on B.Cu, area ~357.7mm²) is correct. routing_complete=true and unrouted_net_count=0 correctly reflect the fully routed board.
- dfm.dfm_tier='standard', dfm.violation_count=0. min_track_width_mm=0.15 and min_drill_mm=0.3 are consistent with the precision analog design. Two-layer stackup (F.Cu, B.Cu) correctly identified.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
