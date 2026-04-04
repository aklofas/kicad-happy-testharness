# Findings: mutable_eurorack_kicad / shelves_hardware_design_pcb_KiCad_shelves_v05

## FND-00002507: Mutable Instruments Shelves analog quad-band parametric EQ/filter eurorack module with five TL074D/TL072D opamps, three SSM2164S quad-VCAs, and two LM4041 shunt references. Analyzer correctly parses 5-sheet hierarchy but systematically misclassifies opamp feedback as open-loop, misses RC filters, protection diodes, and shunt voltage references.

- **Status**: confirmed
- **Analyzer**: schematic
- **Source**: shelves_hardware_design_pcb_KiCad_shelves_v05.kicad_sch.json
- **Created**: 2026-03-30

### Correct
- All 5 sub-sheets parsed and merged: 242 total components, 143 nets, correct multi-sheet hierarchy
- All 14 IC instances correctly typed: LM4041DBZ, TL072D, TL074D, SSM2164S
- Q1 (NPN-SOT23) correctly detected as BJT with LED collector load and base resistors R116/R114
- 37 opamp circuit entries generated covering all 13 multi-unit opamps with correct reference, value, unit, output_net
- Named signal nets correctly identified: GND, VCC, VEE, HP_1, HP_2, BP_1, BP_2, IN, OUTPUT, AREF_+10, AREF_-10
- Power domain correctly identified: all opamps on VCC/VEE dual-supply, IC14 single-supply
- ERC multi-driver warning on MINUS_BUS correctly flags IC5/IC8/IC11 outputs as simultaneous drivers (intentional summing topology)

### Incorrect
- All 28 active opamp units classified as 'comparator_or_open_loop' despite 24 having clear resistive/RC feedback between output and inverting input. E.g. IC6u1: R40 bridges HP_2 (output) to inverting input; IC4 units 1-4 all have R+C feedback pairs.
  (signal_analysis.opamp_circuits)
- 10 panel potentiometers (POT_USVERTICAL_PS R34/R36/R68/R69/R4/R101/R3/R100, POT_USVERTICAL R42/R65) classified as type 'resistor'. They are 3-terminal user-interface controls.
  (statistics.component_types.resistor)
- P1 (PTCSMD, polyfuse/resettable fuse) classified as 'connector'. It is a PTC thermistor for power protection.
  (statistics.component_types.connector)
- design_observations reports all 12 ICs missing VCC decoupling. False positive: 14 capacitors are present on VCC net.
  (signal_analysis.design_observations)

### Missed
- 0 rc_filters detected despite extensive RC networks in state-variable filter topology (IC4, IC9, IC10 all have R+C feedback integrators).
  (signal_analysis.rc_filters)
- 0 protection_devices detected. D3-D6 (SOD323-W, anode GND, cathode on opamp outputs) are output clamping diodes. D1 is reverse-polarity protection on VEE.
  (signal_analysis.protection_devices)
- 0 power_regulators detected. IC1/IC2 (LM4041DBZ) are shunt voltage references producing AREF_+10 and AREF_-10 rails, biased via R1/R2 from VCC/VEE.
  (signal_analysis.power_regulators)

### Suggestions
- Fix opamp configuration classifier: check for passive components connecting output net to inverting input before concluding 'comparator_or_open_loop'.
- Add potentiometer detection: lib_id containing 'POT' or 'TRIM' with 3 pins should classify as 'potentiometer' not 'resistor'.
- Add PTC/polyfuse detection: value/lib_id containing 'PTCSMD', 'PTC', 'POLYFUSE' should classify as 'fuse' not 'connector'.
- Fix decoupling false positives: check net membership, not just proximity.
- Add shunt voltage reference detection (LM4041, TL431, LM385) to power_regulators.

---
