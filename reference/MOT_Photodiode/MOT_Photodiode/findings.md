# Findings: MOT_Photodiode / MOT_Photodiode

## FND-00000921: LT3032-12 dual-output LDO not detected as a power regulator; U2 ADA4898-1 classified as 'compensator' instead of transimpedance amplifier (TIA); V- flagged as cross-domain signal needing level shif...

- **Status**: new
- **Analyzer**: schematic
- **Source**: MOT_Photodiode.kicad_sch.json
- **Created**: 2026-03-23

### Correct
- C1/C2 (10µF) on ±15V and C5 (10µF) on V+ are all correctly identified as bulk decoupling with no high-frequency bypass caps. The design_observations flags missing bypass caps for all three rails, which is accurate.
- The design is powered via J1 (3-pin supply connector) providing +15V/-15V/GND with no PWR_FLAG symbols. The pwr_flag_warnings correctly identify that KiCad ERC will flag these rails. This is expected behavior for connector-powered designs.

### Incorrect
- The opamp configuration is reported as 'compensator'. The actual circuit is a TIA: J3 (photodiode) connects to the inverting input, GND connects to the non-inverting input, and R3||C8 is the feedback network from output to inverting input. This is a canonical transimpedance amplifier topology, not a compensator. The 'compensator' label is misleading for this photocurrent-to-voltage converter.
  (signal_analysis)
- design_analysis.cross_domain_signals reports the V- net (U1 OUTN → U2 V-) as needing a level shifter between domains '-15V' and 'V+'. This is a false positive: V- is the negative supply output of the LT3032 dual LDO (power_out pin), feeding the opamp's negative supply input (power_in). Supply rails connecting regulator outputs to IC supply pins should not be flagged as cross-domain signals requiring level shifters.
  (signal_analysis)

### Missed
- U1 (LT3032-12, lib_id Regulator_Linear:LT3032-12) is a dual-output positive/negative LDO providing +V and -V rails to the opamp, but signal_analysis.power_regulators is empty. The IC is classified as type 'ic' with no regulator topology assigned. This is a missed detection — the LT3032 family should be recognized by its lib_id prefix.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00000922: Routing completeness correctly reconciles 14 nets with 4 no-connect pads; DFM correctly identifies 0.1mm annular ring as requiring advanced process tier; U2 exposed pad (EP) on V- net correctly fla...

- **Status**: new
- **Analyzer**: pcb
- **Source**: MOT_Photodiode.kicad_pcb.json
- **Created**: 2026-03-23

### Correct
- PCB has 14 nets total; 4 are unconnected-(...) nets from NC pins. routed_nets=10, unrouted_count=0 is correct — the 10 signal/power nets are fully routed, the 4 NC-pad nets need no routing.
- min_annular_ring_mm=0.1 is flagged as below the 0.125mm standard limit, requiring advanced process. The DFM tier is reported as 'advanced'. This is accurate for this compact 32×25mm board.
- U2 ADA4898-1 SOIC-8-1EP has its exposed pad on the V- (negative supply) net with 0 nearby_thermal_vias. The thermal_pad_vias analysis correctly identifies this, which is a legitimate thermal concern for a high-speed op amp.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
