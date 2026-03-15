# Findings: Power_HW / GEODE_rev2_SMPS_Motherboard_smps_legged_robot

## FND-00000158: GEODE rev2 power auxiliary with MAX25262 buck converter and TPS2116 power mux. 0-pin parsing for TPS2116 and PMV90ENER due to lib_name mismatch; voltage divider found but not linked to regulator.

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: GEODE_rev2_SMPS_Motherboard_power_auxiliary.kicad_sch.json
- **Related**: KH-083, KH-084
- **Created**: 2026-03-15

### Correct
- R805 (37k) / R804 (10.7k) voltage divider correctly detected with ratio=0.224

### Incorrect
- U801 TPS2116DRLR has 0 pins parsed -- lib_id '0_mux:TPS2116DRLR' doesn't match lib_symbols key 'TPS2116DRLR_1'
  (ic_pin_analysis)
- Q801/Q802 PMV90ENER NMOS FETs have 0 pins -- lib_id 'Simulation_SPICE:NMOS' doesn't match lib_symbols key 'NMOS_1'
  (ic_pin_analysis)

### Missed
- Voltage divider R805/R804 is feedback for LMR36506 (U802) but is_feedback not set, not linked in feedback_networks, no estimated_vout for U802
  (signal_analysis.feedback_networks)
- MAX25262 (IC1201) has input_rail=null -- SUP pin connects through FB1201 ferrite bead to +VBAT
  (signal_analysis.power_regulators)

### Suggestions
- Fix lib_name/lib_id mismatch for 0-pin components
- Feedback network detection should handle divider midpoint connecting to IC FB pin at top of divider, not just midpoint
- Trace through ferrite beads to identify input rails

---
