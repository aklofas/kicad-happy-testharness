# Findings: Transformerless-Power-Supply---KiCAD / Transformerless Power Supply_Transformerless Power Supply

## FND-00001618: Full-bridge rectifier (D1–D4: four 1N4007 diodes) not detected; bridge_circuits=[]; LM7805 (TO220 fixed linear regulator) classified as topology 'LDO'; C4 value '225K/2.2uF' parsed as 225000 F (225...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: Transformerless Power Supply.kicad_sch
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
- U1 (LM7805_TO220) is reported with topology='LDO'. The LM7805 is a fixed-output linear regulator with approximately 2 V dropout — it is not a low-dropout device. The correct topology classification is 'linear' or 'linear_fixed'. This same issue applies to the NCP1117-3.3 in Touch_Keyboard which is labeled LDO (it genuinely is an LDO), so the classifier does not distinguish between fixed linear regulators and true LDOs.
  (signal_analysis)
- C4 is an X2 AC safety capacitor. Its value string '225K/2.2uF' follows EIA code notation: '225' = 2.2 µF, 'K' = ±10% tolerance; the '/2.2uF' is the explicit capacitance. The analyzer's value parser reads '225K' as 225 × 1000 = 225,000 F, storing parsed_value=225000.0. The correct parsed value is approximately 2.2e-6 (2.2 µF). This renders any downstream capacitance-dependent analysis (self-resonant frequency, decoupling adequacy) meaningless for this component.
  (components)
- The design_observations entry for U1 states missing_caps with both input rail '__unnamed_2' and output rail '5V'. In reality: C1 (0.1 µF) and C2 (1000 µF) are connected to the input rail (__unnamed_2, which is U1's VI pin), and C3 (470 µF) is connected to the output rail (5V, U1's VO pin). The caps are present but the analyzer fails to find them, likely because the input rail is unnamed ('__unnamed_2') and the detection logic may require a named power rail to match caps to a regulator's input.
  (signal_analysis)

### Missed
- D1, D2, D3, D4 form a classic full-bridge rectifier: D1(A=unnamed_1, K=unnamed_2) and D2(A=unnamed_6, K=unnamed_2) conduct on alternate half-cycles into the rectified DC-positive node (unnamed_2); D3(A=GND, K=unnamed_1) and D4(A=GND, K=unnamed_6) provide the return paths. The analyzer outputs bridge_circuits=[] despite all four diodes being correctly parsed. This is the core circuit topology of the transformerless power supply.
  (signal_analysis)

### Suggestions
- Fix: LM7805 (TO220 fixed linear regulator) classified as topology 'LDO'

---
