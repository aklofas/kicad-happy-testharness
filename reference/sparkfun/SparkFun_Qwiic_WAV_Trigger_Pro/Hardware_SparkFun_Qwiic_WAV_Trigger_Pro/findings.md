# Findings: sparkfun/SparkFun_Qwiic_WAV_Trigger_Pro / Hardware_SparkFun_Qwiic_WAV_Trigger_Pro

## FND-00000228: SparkFun WAV Trigger Pro USB sheet (34 components). Regulators, protection devices, voltage dividers, feedback network all correct. Critical: L2 value '30ohm' parsed as 30 Henry instead of impedance — invalidates LC filter detection. U6 AP3012 boost estimated output (2.418V) mismatches rail name 3.3V_P by 26.7%.

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: Hardware_usb.kicad_sch.json
- **Related**: KH-112
- **Created**: 2026-03-16

### Correct
- U2 AP2112K-3.3 LDO and U6 AP3012 boost converter correctly identified and classified
- U1 TPD3S014 3-channel ESD protector correctly identified protecting USB DP/DM/VBUS
- 2 voltage dividers correct: R23/R24 (100k/33k, ratio=0.248) feedback, R26/R27 (560/680ohm, ratio=0.548) VUSB detection
- R23/R24 feedback network for U6 correctly detected

### Incorrect
- L2 value '30ohm' (ferrite bead impedance) misparsed as 30.0 henries. Invalidates LC filter detection (L2/C27 reported as LC filter with 29Hz resonance, but L2 is impedance not inductance).
  (signal_analysis.lc_filters)

### Missed
(none)

### Suggestions
- Fix inductor value parser to distinguish ohm (impedance) from henry (inductance) — ferrite beads rated in ohms should not be treated as inductors
- Verify U6 estimated output (2.418V) against design intent — 26.7% mismatch with 3.3V_P rail name

---
