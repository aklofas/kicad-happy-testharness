# Findings: 3458A-A3-66533-2021-KS-RoHS-SMD-KiCad / 3458A A3 66533 2021 KS SMD

## FND-00000267: HP 3458A A3 precision DMM analog board (399 components). All 10 rf_matching detections are false positives (ferrite beads for clock distribution and precision ADC guard networks). Three LT1001 integrators misclassified as comparator_or_open_loop. AD817A integrator misclassified as compensator. AD817A non-inverting amp misclassified as transimpedance_or_buffer. Duplicate design_observations per multi-unit IC.

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: 3458A A3 66533 2021 KS SMD.kicad_sch.json
- **Created**: 2026-03-16

### Correct
- U402 OP07C open-loop servo correctly classified as comparator_or_open_loop
- U404 LT1122 unity-gain buffer correctly classified
- U170 LM358 units correctly classified as buffer and inverting amplifier
- All 8 power regulators correct: 79L05/78L05 pairs for isolated ±5V rails, +3.3V and +1.8V LDOs
- U230 20MHz active oscillator correctly identified

### Incorrect
- U151/U160/U165 (LT1001) classified as comparator_or_open_loop — each has capacitor-only feedback (C151/C160/C165) from output to inverting input, making them integrators in the voltage reference regulation loops
  (signal_analysis.opamp_circuits)
- U111 (AD817A) classified as compensator with R118 as feedback_resistor — R118 connects two different opamps' inverting inputs (inter-stage coupling), not U111's output; C118 is the sole feedback element (integrator)
  (signal_analysis.opamp_circuits)
- U140 (AD817A) classified as transimpedance_or_buffer — has R140=1k to ground and R141=18.7k feedback, making it a non-inverting amplifier at gain 19.7x
  (signal_analysis.opamp_circuits)
- Duplicate design_observations: multi-unit ICs (U302 7x, U303 7x, U353 7x, U150 7x, U8 7x, U213 5x, U403 5x) generate per-unit entries instead of per-IC
  (signal_analysis.design_observations)

### Missed
- Precision input attenuator resistor ladder (R401-R406, 453k to 14k) with paired jumpers forms the ADC voltage ranging divider — 0 voltage_dividers detected
  (signal_analysis.voltage_dividers)

### Suggestions
- RF matching should exclude ferrite beads (description/keywords containing 'ferrite', 'EMI', 'bead')
- Integrator classification: capacitor-only feedback (output to inverting input) should be labeled 'integrator' not 'comparator_or_open_loop'
- Feedback resistor identification must verify one end connects to the opamp's output net
- Non-inverting amp detection: grounding resistor at inverting input + feedback resistor from output = non-inverting, not transimpedance
- Deduplicate design_observations by component reference

---

## FND-00002506: KiCad 9 recreation of HP 3458A A/D circuit board (A3), a 399-component precision DMM with ADC hybrid, voltage reference, signal conditioning, CPLD logic, fiber-optic bus interface, and power regulation. Analyzer performs well on RC/LC filters, opamp classification, and regulator detection, but misses fiber optic isolation barriers and has a false UART detection on MCU-to-CPLD bus signal.

- **Status**: confirmed
- **Analyzer**: schematic
- **Source**: 3458A A3 66533 2021 KS SMD.kicad_sch.json
- **Created**: 2026-03-30

### Correct
- All 8 linear regulators correctly detected: U4052/U4051 (79L05/78L05), U1422 (79L05), U1812/U1811 (79L05/78L05), U1421 (78L05), U11 (LMS8117ADT-3.3), U12 (LMS8117AMP-1.8)
- U230 (20MHz DIP-14 crystal oscillator) correctly classified as active_oscillator
- LC filter L1+C8/C7 (100nH + 2.3uF, 331.86 kHz) correctly detected; L223+C902 (27uH + 100nF, 96.86 kHz) also correct
- 12 opamp circuits correctly classified including U404 (LT1122) as unity-gain buffer, U111 (AD817A) as integrator, U170 (LM358) as buffer/inverting stage, U160/U165 (LT1001) as precision reference drivers
- 17 valid RC signal filters correctly detected including R280/C280 (1k/10n, 15.92 kHz overload filter)
- All 23 power rails correctly enumerated including isolated +5 domains and precision references (+5ref, +12ref)
- Level translators U1-U7 (SN74LVC8T245PW) correctly identified bridging +3V3/+5 for CPLD interface
- Multi-sheet hierarchical parsing correct: all 4 sheets parsed with 588 nets and 1848 wires

### Incorrect
- 11 of 28 RC filters have power rail as output_net (e.g. R166/C166 output=+18). These are power supply filter networks where the analyzer inverts input/output — the signal net is the output, the power rail is the source.
  (signal_analysis.rc_filters)
- UART detection false positive: net _XRXW classified as UART connecting U220 (AT89LS51 pin33=P0.4/AD4) and U210 (CPLD). This is a bidirectional MCU-to-CPLD bus signal, not a UART line. The 'RXW' substring triggered a false match.
  (design_analysis.bus_analysis.uart)

### Missed
- Fiber optic isolation barrier not detected: HFBR-1521Z (U354, U304, U10 DNP — TX) paired with HFBR-2521Z (U301, U351 — RX) form HP-IB fiber optic isolation interface. Classified as generic IC.
  (signal_analysis.isolation_barriers)
- Ferrite bead clock distribution not detected: L233, L231, L232 (100nH) on 20MHz oscillator output as inductive isolators for clock distribution.
  (signal_analysis.lc_filters)
- Q403 (PF5301 N-JFET) diode-connected current source not detected: gate tied to GND, drain/source on same net — precision current limiter for ADC input stage.
  (signal_analysis.transistor_circuits)

### Suggestions
- Add isolation_barriers detection for HFBR-1521Z/2521Z fiber optic transceiver pairs
- Fix RC filter input/output direction: when resistor is between power rail and signal net with cap to GND, the signal net is the output
- Tighten UART detection: require pin_name to contain TXD/RXD rather than matching net name substrings
- Add diode-connected JFET current source detection: gate tied to GND/source with D=S on same net

---
