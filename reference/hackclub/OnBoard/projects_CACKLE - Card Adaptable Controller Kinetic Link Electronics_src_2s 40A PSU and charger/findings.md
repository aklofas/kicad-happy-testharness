# Findings: OnBoard / projects_CACKLE - Card Adaptable Controller Kinetic Link Electronics_src_2s 40A PSU and charger_2s 40A PSU and charger

## FND-00000091: 2S battery PSU/charger with BQ76905 BMS, half-bridge motor driver, RS-485. 16 false positive rf_matching detections on power filter components. RS-485 termination resistors misidentified as voltage divider.

- **Status**: confirmed
- **Analyzer**: schematic
- **Source**: repos/OnBoard/projects/CACKLE - Card Adaptable Controller Kinetic Link Electronics/src/2s 40A PSU and charger/2s 40A PSU and charger.kicad_sch
- **Created**: 2026-03-14

### Correct
- BQ76905 BMS IC correctly detected in bms_systems
- Half-bridge circuit correctly identified with high/low side MOSFETs
- RS-485 differential pair correctly detected with series resistors
- TPS7A2633 LDO and AP63203WU switching regulator correctly identified
- Battery voltage divider R30(866k)/R31(866k) correctly detected for monitoring
- Four transistor circuits correctly identified including power MOSFETs

### Incorrect
- 16 false positive rf_matching detections — resistors (R18 5mOhm sense, R21/R12 10ohm, R24/R23 10k) and capacitors misidentified as antennas; these are power supply filter components on a PSU board
  (signal_analysis.rf_matching)
- R27(120ohm)/R26(120ohm) RS-485 termination/bias resistors falsely detected as voltage divider between RS485+ and RS485-
  (signal_analysis.voltage_dividers)
- BOM sum (92) does not match total_components (112) — 20 missing: net_tie(11)+test_point(6)+mounting_hole(2)=19, still 1 unaccounted
  (statistics)
- DNP count=11 but only 5 DNP entries in BOM, inconsistent
  (bom)

### Missed
- No current sense detection despite R18 (5mOhm, 10W) being a high-power current sense resistor
  (signal_analysis.current_sense)
- No charger circuit detection despite board name being "2s 40A PSU and charger"
  (signal_analysis)
- Missing regulator input/output cap warnings despite design_observations noting them
  (signal_analysis.decoupling_analysis)

### Suggestions
- rf_matching detector should not flag components with values like 5mOhm, 10ohm, 10k as antennas
- Voltage divider detector should consider that equal-value resistors between bus signals are termination not dividers
- Current sense should detect low-ohm high-wattage resistors

---
