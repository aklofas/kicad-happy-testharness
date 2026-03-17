# Findings: cubesat-boards / ykts-power_ykts-power

## FND-00000282: CubeSat power board (KiCad 5, 130 components). Solar cell array with blocking diodes falsely detected as 2x2 key matrix. RC filter double-counting on C5. False missing-input-cap warnings for TPS63001/TPS63002 due to hierarchical PGND/VIN merge. BQ25070 chargers and INA3221 power monitor not detected.

- **Status**: confirmed
- **Analyzer**: schematic
- **Source**: ykts-power_ykts-power.sch.json
- **Created**: 2026-03-16

### Correct
- 4 switching regulators (TPS63001 x2, TPS63002 x2) correctly identified with inductors and feedback nets
- 4 KIA3415 dual PMOS transistors correctly detected as P-channel with gate resistors
- 2 voltage dividers (490K/100K) correctly detected as BQ25070 feedback dividers
- 2 crystals (Y1=8MHz, Y2=12MHz) with 22pF load caps correct

### Incorrect
- RC filter double-counting: R2+C5 and R1+C5 both reported as separate filters sharing capacitor C5
  (signal_analysis.rc_filters)
- False missing-input-cap warnings for all 4 TPS63001/TPS63002 — caps exist but hierarchical sheet merges PGND with VIN
  (signal_analysis.design_observations)

### Missed
- BQ25070 (U7, U14) battery charger ICs not detected as charging controllers — bms_systems empty
  (signal_analysis.bms_systems)
- INA3221AIRGVR (U6) 3-channel current/power monitor with 3x 0.1ohm shunts not detected in current_sense
  (signal_analysis.current_sense)

### Suggestions
- Key matrix detector should filter out Device:Solar_Cell components
- Detect BQ25070/BQ25071 MPPT charger ICs in bms_systems
- Suppress missing-cap warnings when PGND appears on same net as VIN (hierarchical artifact)

---
