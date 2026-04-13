# Findings: jvedder/Biploar-power-supply-KiCAD / Bipolar power supply

## FND-00000391: LM337 feedback voltage divider (R21/R22) not detected; ADJ_P/ADJ_N detected as a differential pair; IN_P/IN_N detected as a differential pair; AC rectifier/dual half-wave rectifier topology not det...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: Bipolar power supply.kicad_sch.json
- **Created**: 2026-03-23

### Correct
(none)

### Incorrect
- design_analysis.differential_pairs contains an entry pairing ADJ_P and ADJ_N as a differential pair. These are the independent feedback/adjust nodes of two separate linear regulators (LM317 and LM337), not a true differential signal pair. They are on different signal paths with no intentional differential relationship.
  (design_analysis)
- design_analysis.differential_pairs also contains IN_P and IN_N as a differential pair. These are the positive and negative DC rail inputs to two independent regulators, not a differential signal pair. They are simply the two DC bus rails of a split-supply power supply.
  (design_analysis)
- The analyzer reports estimated_vout=1.364V for U1 (LM317) with R11=249Ω as r_top (VPOS side) and R12=2.73kΩ as r_bottom (GND side). The correct LM317 formula is Vout = Vref*(1 + R_bottom/R_top) = 1.25*(1 + 2730/249) ≈ 14.96V. The analyzer instead computes 1.25*(1 + 249/2730) ≈ 1.364V, meaning it treats R11 as the feedback resistor (bottom) and R12 as the reference resistor (top), which is inverted. The voltage divider ratio 0.916415 = 2730/2979 further confirms R12 is being treated as r_top. The estimated output is off by a factor of ~11.
  (signal_analysis)
- design_analysis.net_classification lists VPOS, VNEG, IN_P, and IN_N all as 'signal'. These are DC power supply rails (rectified/regulated voltages driving loads and supplied by regulators). They should be classified as power nets. Only GND is correctly classified as ground.
  (design_analysis)

### Missed
- The schematic has a symmetric dual-supply design. U1 (LM317) uses R11=249Ω (VPOS→ADJ_P) and R12=2.73kΩ (ADJ_P→GND) as its feedback divider — detected. U2 (LM337) uses an identical topology: R21=249Ω (VNEG→ADJ_N) and R22=2.73kΩ (ADJ_N→GND). signal_analysis.voltage_dividers contains only the R11/R12 divider. The R21/R22 divider for the LM337 is absent from voltage_dividers.
  (signal_analysis)
- The schematic implements a dual half-wave rectifier: D11 (AC→__unnamed_5) and D21 (AC→__unnamed_1) feed the positive and negative rectified rails from the AC input (J1/J2). signal_analysis.bridge_circuits is empty and there is no detection of the rectifier or the C11/C21 bulk reservoir capacitors as a rectifier+filter topology.
  (signal_analysis)

### Suggestions
- Fix: VPOS, VNEG, IN_P, IN_N classified as signal nets rather than power nets

---
