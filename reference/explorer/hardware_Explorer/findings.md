# Findings: explorer / hardware_Explorer

## FND-00000215: AnyShake Explorer seismograph data acquisition board with STM32F103C8Tx MCU, 3-axis geophone signal conditioning (6x ADA4528-2ARMZ dual op-amps), MP2236GJ switching regulator, TPS5430DDA negative-rail generator, RS-232 interfaces, and NEO-M8M GNSS. Excellent op-amp and filter analysis. Crystal detection has a false positive with the active oscillator, and TPS5430DDA output topology is not fully traced.

- **Status**: confirmed
- **Analyzer**: schematic
- **Source**: hardware_Explorer.kicad_sch.json
- **Created**: 2026-03-15

### Correct
- 12 op-amp circuits correctly analyzed across 6x ADA4528-2ARMZ dual op-amps: 6 inverting preamp stages (U17-U19 units 1+2) with gains from -1.0 to -19.6, and 6 compensator stages (U13-U15 units 1+2) for the geophone signal processing chain
- U3 MP2236GJ switching regulator correctly identified with Vref=0.8V (lookup), feedback divider R7 (100k) / R8 (12k), and estimated Vout=7.467V from VIN input
- R7/R8 feedback divider correctly identified with is_feedback=true, ratio=0.107, connected to U3 FB pin
- 6 anti-aliasing filters correctly detected at 26.98 Hz (R64-R66, R79-R81 at 5.9k with 1uF caps) on PREAMP_ZP/ZN/EP/EN/NP/NN to AAF_ZP/ZN/EP/EN/NP/NN nets
- Multiple sub-Hz bandpass filter stages correctly detected using 43k resistors with 4.7uF caps (~0.79 Hz) for the EHZ/EHE/EHN seismic signal paths
- R1 (330k) / R2 (510k) voltage divider correctly detected as enable threshold for U3 MP2236GJ EN pin (not feedback)
- 7 protection devices correctly identified: D2 SMAJ12A on power, D8 SMAJ5.0CA on digital, D17-D20 SMAJ15CA on RS-232 TX/RX lines
- U5 AMS1117-3.3 and U2 LP2985-2.5 LDOs correctly detected with fixed output voltages from part number suffix
- U4 TPS72325DBV correctly identified as inverting LDO (negative output regulator)
- U6 AT24CS08-SSHM EEPROM correctly detected as memory interface connected to U11 STM32F103C8Tx via 4 shared signal nets (I2C)
- R4 (3.3k) / R3 (10k) voltage divider correctly detected with U1 TPS5430DDA VSENSE pin connection
- VIN and VCC decoupling correctly analyzed: VIN has 3 caps (45uF total), VCC has 8 caps (60.9uF total)

### Incorrect
- Y1 SG-8002CA 8M-PCML0 is an active oscillator (SG-8002CA series by Epson), not a passive crystal. The analyzer incorrectly identified 12 power decoupling capacitors on D+3V3 rail as crystal load caps, resulting in a nonsensical effective_load_pF=50003.0. Active oscillators have no external load caps.
  (signal_analysis.crystal_circuits)
- U1 TPS5430DDA detected as switching regulator with input_rail=VCC but no output_rail identified. The TPS5430DDA in this design generates the GNDA analog reference rail through an unusual topology (PH->L1->GNDA), and its feedback divider R4/R3 is detected as a separate voltage_divider but not linked to U1
  (signal_analysis.power_regulators)
- Design observation for regulator_caps flags U4 TPS72325DBV and U5 AMS1117-3.3 as missing output caps, but the output nets are __unnamed which makes it hard to verify. U2 LP2985-2.5 also flagged for missing output caps on __unnamed_12
  (signal_analysis.design_observations)

### Missed
- The 3-axis geophone signal processing chain (EHZ/EHE/EHN paths) with low-pass, bandpass, and anti-aliasing stages feeding into an ADC is not characterized as a coherent multi-channel data acquisition system in design_observations
  (signal_analysis.design_observations)
- RS-232 interface topology with D17-D20 SMAJ15CA protection on TX/RX lines not detected as a bus protocol (RS-232 male and female connectors J6/J7 with protection)
  (signal_analysis.design_observations)

### Suggestions
- Detect SG-8002CA and similar active oscillator part numbers (SG-*, ASCO*, ASE*, DSC*) as active_oscillator type and skip load cap analysis for them
- Link voltage dividers feeding regulator VSENSE/FB pins to the corresponding power_regulator entry, even when the feedback topology is non-standard
- Consider detecting multi-channel analog signal processing chains (geophone, accelerometer conditioning) as a design pattern

---
