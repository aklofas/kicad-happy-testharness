# Findings: gmarocco/Arduino_shield_kicad / Shield Arduino v2-1

## FND-00000379: VR1 trimmer potentiometer misclassified as varistor; C5 capacitance massively overestimated: MPN prefix in value string parsed as capacitance; VR1 trimmer potentiometer incorrectly listed as protec...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: Shield Arduino v2-1.kicad_sch.json
- **Created**: 2026-03-23

### Correct
- C5 has value '865080253012 470uF 10V' in the schematic — a Würth Elektronik capacitor where the designer prepended the MPN (865080253012) into the value field. The analyzer parses '865080253012' as the capacitance in farads (0.865080253012 F = 865,080 µF) instead of extracting '470uF'. This causes signal_analysis.decoupling_analysis for the +5VA rail to report total_capacitance_uF=865080.353 instead of the correct ~470.1 µF, and inrush_analysis to use the wrong capacitance. The correct approach is to parse the last numeric token followed by a capacitance unit suffix (uF, nF, pF) from a multi-token value string.
- simulation_readiness reports needs_model=24 and total_components=81 (correctly excludes 4 mounting holes), but the components_without_model list only contains 20 entries. The 4 missing entries appear to be the fiducials (FID1, FID2, FID3) and test point (GPIO2), which are counted in the needs_model total but silently omitted from the explicit list. The count and list should be consistent.
- assembly_complexity.total_components=89 counts each unit of multi-unit ICs separately: U2 (LM324, quad op-amp) contributes 5 entries (4 op-amp units + 1 power unit) instead of 1. statistics.total_components=85 correctly counts unique references. The assembly complexity metric should use unique reference count (85) for consistency, since placing and soldering a component counts once regardless of its internal unit count.

### Incorrect
- VR1 (PT10MH01-103A2020-S) is a through-hole trimmer potentiometer (description: 'TRIMMER, 10K, 0.15W, 1TURN', lib_id: SamacSys_lib:PT10MH01-103A2020-S). The analyzer classifies it as type='varistor' (likely triggered by the 'VR' reference prefix). It is then incorrectly listed in protection_devices as clamping the +5VA rail to AN2. A trimmer pot has no protection/clamping function. The correct type should be 'potentiometer' or 'variable_resistor'.
  (statistics)
- signal_analysis.protection_devices includes VR1 (PT10MH01-103A2020-S, a trimmer potentiometer) as a 'varistor' clamping the +5VA rail. This is incorrect: a trimmer pot is a user-adjustable resistor, not an overvoltage clamping device. The protection_devices list should only contain TVS diodes, MOVs, varistors, and fuses. VR1 appears here as a downstream consequence of the varistor misclassification.
  (signal_analysis)

### Missed
- L1 (B82442T1685K050, 6.8 mH inductor) is placed in series between the +5V and +5VA power rails, with bulk/bypass capacitors C5 (470 µF) and C6 (10 µF) on the +5VA output. This is a classic L-C power filter used to create a low-noise analog supply (+5VA) from the digital +5V rail. signal_analysis.lc_filters=[] — the filter is not detected. The LC filter detector should recognize inductors on power rails with downstream capacitors as power filter topologies.
  (signal_analysis)

### Suggestions
(none)

---
