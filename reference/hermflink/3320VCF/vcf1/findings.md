# Findings: hermflink/3320VCF / vcf1

## FND-00000317: opamp_circuits=0 despite TL074 (U1, 4 units) and TL072 (U2, 2 units) forming multiple op-amp stages; feedback_networks=0 despite multiple op-amp feedback resistor networks present; U2 (TL072) missi...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: vcf1.sch.json
- **Created**: 2026-03-23

### Correct
- L1 and L2 use the 'L' inductor symbol with value '1uH' and an axial inductor footprint (Fastron SMCC), but are classified as type 'ferrite_bead' in the BOM. In eurorack synthesizer power supplies, small inductors like these are used as LC chokes on ±15V rails. The symbol is a standard inductor (L), not a ferrite bead (FB), so the classification should be 'inductor'. This is a misclassification in component type detection.

### Incorrect
- Three RC-network detections (R7+C8, R8+C8, R11+C8) at 48.23kHz share the same capacitor C8 (33pF) connected to the same node. R7, R8, and R11 are all 100k input resistors for op-amp U2 unit 1's summing junction, and C8 is a small compensation/stray capacitance cap across the summing node — not three independent RC filter stages. Reporting them as 3 separate RC filters overstates the filter count and mischaracterizes their function.
  (signal_analysis)

### Missed
- The schematic has U1 (TL074, quad op-amp) used in 4 inverting/summing amplifier configurations, and U2 (TL072, dual op-amp) in 2 amplifier stages — totaling at least 6 op-amp circuit instances. These include input mixers (U1 units 1 and 2), resonance feedback (U1 unit 3 with R19 33K feedback resistor), output stage (U1 unit 4), and CV conditioning stages (U2 units 1 and 2). The analyzer reports opamp_circuits=0 for this analog synthesizer VCF schematic that is built predominantly around op-amp circuits.
  (signal_analysis)
- Multiple resistors connect op-amp outputs to their inverting inputs forming classic inverting amplifier feedback loops. For example: R19 (33K) in U1 unit 3 feedback path (resonance stage), R38 (51K) in U2 unit 2, R15/R16 (51K) forming the output summing stage feedback on U1 unit 2, R22 (51K) on U1 unit 4. These are standard op-amp feedback networks that should be detected.
  (signal_analysis)
- The power_domains.ic_power_rails section lists U3 (AS3320) and U1 (TL074) but omits U2 (TL072). U2 has two units: unit 1 at position (2950, 2050) and unit 2 at position (9250, 3300), both powered by ±15V rails. The omission indicates the power domain analysis failed to resolve U2's power connections.
  (design_analysis)
- The schematic has C9/C10 (100n) and C11/C12 (10uF) and C13/C14 (100nF) on the power entry section for ±15V rails — a typical eurorack bulk+bypass decoupling arrangement. The decoupling_analysis only reports 1 capacitor per rail (C9 for +15V, C10 for -15V) with 0.1uF each. C11/C12 (10uF bulk electrolytic), and C13/C14 (100nF ceramic) are not counted, so the bulk and high-frequency coverage assessment is incorrect: has_bulk=false and has_high_freq=false are wrong.
  (signal_analysis)

### Suggestions
(none)

---
