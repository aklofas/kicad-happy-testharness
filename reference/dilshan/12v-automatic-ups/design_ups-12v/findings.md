# Findings: dilshan/12v-automatic-ups / design_ups-12v

## FND-00000308: PC817 optocoupler not detected as isolation barrier; Voltage divider R3/RV1/R8 for battery ADC sensing not detected; LM2576T-12 estimated_vout is 1.2V instead of 12V; Q3 (BD135) load_type misclassi...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: design_ups-12v.sch.json
- **Created**: 2026-03-23

### Correct
(none)

### Incorrect
- U4 is an LM2576T-12, a fixed 12V switching regulator. The '-12' suffix indicates a fixed 12V output. The analyzer reports estimated_vout: 1.2 and then flags a vout_net_mismatch (90% discrepancy) against the '+12V' net. The correct output voltage is 12V, which matches the +12V power rail — there is no actual mismatch. The analyzer appears to misparse the '-12' suffix as 1.2V.
  (signal_analysis)
- Q3 (BD135) is driven via RELAY-DRV from the PIC16F688 to switch relay RL1 (G2RL-2-DC12). The transistor_circuits entry for Q3 has load_type='led', which is incorrect. Q3 is a relay driver. D12 (1N4004) is a flyback diode across the relay coil, which may have confused the LED detection.
  (signal_analysis)
- The transistor_circuit entry for Q1 (BC547) reports base_net='GND', collector_net='__unnamed_5', and emitter_net='__unnamed_5'. Q1's base is connected to the RV2/RV3 potentiometer adjustment network (not GND), and its collector and emitter should be on different nets. This indicates a net resolution error for Q1's pin connections. Also, base_driver_ics incorrectly includes U4 (LM2576T-12), which is unrelated to Q1.
  (signal_analysis)
- The design_observations entry for U4 (LM2576T-12) reports a vout_net_mismatch with estimated_vout=1.2 vs net '+12V' at 12.0V (90% discrepancy). This is a cascading false positive from the incorrect voltage parsing of the '-12' suffix (should be 12V not 1.2V). The LM2576T-12 correctly outputs to the +12V rail.
  (signal_analysis)
- The design_observations decoupling entry for U5 (LM7805) lists rails_without_caps: ['+5V', '+12L']. However, C10 (0.1MFD) is connected between +12L and GND (the LM7805 input), and C11 (33MFD) is connected between +5V and GND (the LM7805 output). These bypass capacitors exist on the correct rails but were not recognized by the analyzer.
  (signal_analysis)
- R2 and R4 (both 0.47R) are genuine current sense shunt resistors in the battery charging current path. However, the analyzer identifies U1 (LM350) as the 'sense_ic'. The actual current sensing is performed by Q1 (BC547), which monitors voltage across the shunt to regulate charge current. U1 is the pass transistor/regulator, not the sense IC.
  (signal_analysis)

### Missed
- U3 is a PC817 optocoupler with lib_id 'Isolator:PC817', providing galvanic isolation between the 230V AC mains sensing circuit and the 5V logic side. The analyzer detected 0 isolation_barriers but U3 clearly serves this role. It was instead partially captured under transistor_circuits as a base_driver_ic for Q2.
  (signal_analysis)
- R3 (22.0K), RV1 (10K trimmer), and R8 (680R) form a series voltage divider from +VBAT to GND, with the wiper of RV1 feeding ADC-IN to the PIC16F688. This is a battery voltage monitoring divider. The analyzer reports 0 voltage_dividers detected.
  (signal_analysis)

### Suggestions
- Fix: LM2576T-12 estimated_vout is 1.2V instead of 12V
- Fix: Q3 (BD135) load_type misclassified as 'led' instead of relay driver
- Fix: Q1 (BC547) transistor circuit has wrong base_net and identical collector/emitter nets
- Fix: Current sense 'sense_ic' incorrectly identifies LM350 (U1) instead of Q1 for R2/R4 sense resistors

---
