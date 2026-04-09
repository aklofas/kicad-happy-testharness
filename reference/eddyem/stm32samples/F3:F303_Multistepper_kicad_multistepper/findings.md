# Findings: eddyem/stm32samples / F3:F303_Multistepper_kicad_multistepper

## FND-00002522: Multistepper controller (STM32F303, isolated CAN via ISO1050, LM2576 buck, 2x LM1117 LDO, 8 stepper modules). Issues: B0505S DC-DC converter as transistor (Q prefix), LM2576 as LDO, IRF9310 P-MOSFET as N-channel, bare '0.1' cap values parsed as 0.1F instead of 0.1uF.

- **Status**: confirmed
- **Analyzer**: schematic
- **Source**: F3:F303_Multistepper_kicad_multistepper.kicad_sch.json
- **Created**: 2026-04-09

### Correct
- 243 components across 13 sheets correctly parsed
- U3 USBLC6 and D24 PESD1CAN ESD protection correctly detected
- Y1 8MHz crystal with 6pF load caps correctly detected
- U6/U8 LM1117-3.3 LDOs correctly identified
- J1 SWD debug interface correctly detected

### Incorrect
- Q1 B0505S isolated DC-DC converter classified as transistor — Q prefix misleads. Has Vin/GND/+Vo/0V pins.
  (components)
- U5 LM2576-5.0 classified as LDO — it's a switching buck with L1 and D27 freewheeling diode
  (signal_analysis.power_regulators)
- Q2 IRF9310 has is_pchannel=false but description says 'P-MOSFET', keywords include 'PMOS'
  (signal_analysis.transistor_circuits)
- Caps with value '0.1' (12 caps) parsed as 0.1F instead of 0.1uF — inflates decoupling totals to 100047uF, RC filters show 0 Hz cutoff
  (signal_analysis.decoupling_analysis)

### Missed
- 8 stepper motor driver modules (XX1-XX8) not in motor_drivers despite 'stepper_module' value
  (signal_analysis.motor_drivers)
- ISO1050 CAN transceiver isolation barrier not detected
  (signal_analysis.isolation_barriers)
- CAN bus protocol not detected despite ISO1050 + CANH/CANL + termination
  (signal_analysis)

### Suggestions
- Check lib_symbol description/keywords for MOSFET channel type
- Bare numeric cap values <1 in 0603/0805 are microfarads not farads
- Detect B0505S-type isolated DC-DC by pin names, not ref prefix
- Classify LM2576/LM2596 as switching buck, not LDO

---
