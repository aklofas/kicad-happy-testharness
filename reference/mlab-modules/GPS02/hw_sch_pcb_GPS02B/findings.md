# Findings: mlab-modules/GPS02 / hw_sch_pcb_GPS02B

## FND-00000599: ESD protection for D- reported as has_esd_protection=False despite U1 (USBLC6-2SC6) protecting it; I2C pullups R2 and R3 (10k to +3V3) not detected; has_pull_up=False for both SDA and SCL; MIC5504-...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: hw_sch_pcb_GPS02B.kicad_sch.json
- **Created**: 2026-03-23

### Correct
- power_regulators correctly identifies U2 as LDO topology with output_rail=+3V3, estimated_vout=3.3, vref_source=fixed_suffix from '3.3YM5' part number suffix.
- rf_matching correctly identifies J18 (SMA) as the antenna with L_match topology using L2 (27nH) and C7 (47pF), targeting U3 (NEO-M8P). RC filter and LC filter for the RF path are also correctly reported at 338MHz cutoff / 141MHz resonance.
- transistor_circuits correctly identifies Q1 as a BJT in LED driver configuration: emitter grounded, D6 (GREEN LED) in collector path, base resistor R14 (220R), current resistor R16 (220R) on +3V3 power rail.

### Incorrect
- design_observations shows D- with has_esd_protection=False and D+ with has_esd_protection=True, yet protection_devices correctly lists U1's protected_nets as [D+, D-, DM, DP]. The asymmetry between D+ and D- detection is a bug in how the observation cross-references the protection device's protected_nets list. DP and DM are similarly False despite being listed.
  (signal_analysis)
- The NEO-M8P (U3) I2C pins connect through 33R series resistors (R8, R9) to the SDA{slash}#CS and SCL{slash}CLK label nets, where R2 and R3 (10k) provide pullups to +3V3. The bus analyzer only checks for pullups on the net directly connected to the IC pin (__unnamed_4, __unnamed_5), missing the pullups one net hop away through the series resistors. This is a real network topology limitation that produces a false 'missing pullup' conclusion.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---
