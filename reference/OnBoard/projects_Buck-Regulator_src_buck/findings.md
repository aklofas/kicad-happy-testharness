# Findings: OnBoard / projects_Buck-Regulator_src_buck

## FND-00000109: Simple LM2596S-12 buck regulator. Good subcircuit and signal detection but incorrectly applies adjustable-version feedback analysis to the fixed 12V variant.

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: repos/OnBoard/projects/Buck-Regulator/src/buck.kicad_sch
- **Created**: 2026-03-14

### Correct
- Correctly identified LM2596S-12 as a switching regulator with VCC input
- Correctly identified voltage divider R3=10k/R1=1k with ratio 0.0909
- Correctly detected feedback network connected to pin 4 of U1
- Correctly flagged missing output capacitor on regulator output net
- Correctly identified 680uF input and 220uF output bulk decoupling
- Correctly identified Schottky diode and inductor in the buck topology

### Incorrect
- LM2596S-12 is a FIXED 12V output regulator - the -12 suffix indicates fixed output. The feedback divider analysis calculates estimated_vout=14.135V using Vref=1.285V which is wrong. For fixed output versions, pin 4 (ON/OFF) is not a feedback pin, and the resistor divider likely serves as enable/UVLO control, not output voltage setting.
  (signal_analysis.power_regulators)
- IC ref fields are ? for all components including U1, J1, J2
  (ic_pin_analysis)
- IC function not identified for LM2596S-12 despite lib_id containing Regulator_Switching
  (ic_pin_analysis)
- Output rail shown as __unnamed_1 instead of being associated with Vout net
  (signal_analysis.power_regulators)

### Missed
- LM2596 variant identification (-12 = fixed 12V, -5 = fixed 5V, -3.3 = fixed 3.3V, -ADJ = adjustable) should drive different analysis paths
  (signal_analysis.power_regulators)
- Schottky diode (D1=SS54) in the buck converter freewheeling path not analyzed as part of the switching topology
  (subcircuits)

### Suggestions
- Parse regulator part number suffixes to determine fixed vs adjustable variants
- For fixed-output regulators, skip feedback divider analysis and report the fixed output voltage from the part number
- Use lib_id path (Regulator_Switching:LM2596S-12) to identify IC function when value alone is insufficient
- Trace output net through inductor to identify actual output rail name

---
