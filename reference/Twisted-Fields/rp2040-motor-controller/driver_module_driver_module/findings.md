# Findings: rp2040-motor-controller / driver_module_driver_module

## FND-00000127: BLDC motor driver module: excellent current sense detection with INA240 amplifiers and 3-milliohm shunts, but missing half-bridge gate driver recognition for EG3113

- **Status**: confirmed
- **Analyzer**: schematic
- **Source**: repos/rp2040-motor-controller/driver_module/driver_module.kicad_sch
- **Created**: 2026-03-14

### Correct
- Three current sense circuits correctly identified: INA240A1D amplifiers with 3-milliohm shunt resistors on phases A, B, C with correct max current estimates (~16.7A at 50mV)
- VMOT power rail decoupling correctly analyzed: 448.8uF total (2x 220uF 63V solid + 4x 2.2uF 100V ceramic) - appropriate for motor driver
- TPS7A1601DGNT LDO identified for 12V to 3.3V local regulation
- TVS protection diodes (SMAJ51A) correctly identified on power inputs
- Three PNP BJT transistors identified with 100-ohm base resistors for bootstrap/charge pump circuits
- Thermistor (TH1) present in component list for motor temperature monitoring

### Incorrect
- Current sense associates two shunts (R113, R105) with same INA240 U21 on A_P/A_N - likely one shunt per phase, check pin mapping
  (signal_analysis.current_sense)

### Missed
- EG3113 half-bridge gate drivers (3 instances) not recognized as motor gate drivers - they are the key BLDC driver ICs controlling 6 MOSFETs
  (signal_analysis)
- Three-phase BLDC bridge topology not detected - 3x EG3113 half-bridge drivers form a complete 3-phase inverter
  (signal_analysis.bridge_circuits)
- Bootstrap capacitor circuits for high-side gate drive not identified
  (signal_analysis)
- Phase outputs (A, B, C motor connections) not linked to the current sense and gate driver circuits as a complete motor drive channel
  (signal_analysis)

### Suggestions
- Detect half-bridge and full-bridge gate driver ICs (EG3113, IR2110, DRV8301 families) as motor drive components
- Identify 3-phase bridge topologies when 3 half-bridge drivers share motor power rails
- Link current sense circuits to their associated phase in multi-phase motor drives
- Detect bootstrap capacitors on gate driver VB/HO pins

---
