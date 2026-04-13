# Findings: jvarghes2501/BreadBoard_Power_Supply_KICAD_Project / Breadboard_Power_Supply

## FND-00000395: RC low-pass filter falsely detected from LED current-limiting resistor R1 and bypass cap C1; design_observations falsely reports missing decoupling caps on both LM7805 (U1) and LM317 (U2); LED powe...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: Breadboard_Power_Supply.kicad_sch.json
- **Created**: 2026-03-23

### Correct
- The analyzer correctly detects R2 (330 ohm) and R3 (560 ohm) as the LM317 feedback divider, with R2 connecting the output rail (3.3V net) to the ADJ pin and R3 connecting ADJ to GND. The estimated Vout of 1.987V (Vref=1.25V, formula Vout = 1.25*(1+330/560)) is mathematically correct, and the vout_net_mismatch observation correctly flags the 39.8% discrepancy between the calculated voltage and the net name '3.3V'.
- signal_analysis.power_regulators correctly lists U1 (LM7805_TO220, input 12V, output 5V) and U2 (LM317_TO-220, input 12V, output 3.3V net, with feedback divider). Both are labelled topology 'LDO'. The component counts (17 total: 7 connectors, 3 capacitors, 2 ICs, 3 resistors, 1 switch, 1 LED) are correct per the schematic.

### Incorrect
- The analyzer reports an RC low-pass filter (48.23 Hz) formed by R1 (330 ohm) and C1 (10 uF). In the actual circuit, R1 is a current-limiting resistor in series with LED D1 (path: 12V -> R1 -> D1 anode -> D1 cathode -> GND). C1 is an input bypass capacitor on the 12V rail for U1 (LM7805). These two components share the 12V node but serve entirely different purposes. The R-C topology is coincidental, not a deliberate filter. There is no RC filter in this design.
  (signal_analysis)
- signal_analysis.design_observations contains two 'regulator_caps' entries claiming that input and output caps are missing for U1 and U2. However, ic_pin_analysis.decoupling_caps_by_rail for U1 lists C1 (10 uF) on the 12V input and C2 (0.1 uF) on the 5V output. For U2 it lists C1 (10 uF) on the 12V input and C3 (1 uF) on the 3.3V output. All four decoupling caps are present. The design_observations field is internally inconsistent with the ic_pin_analysis field.
  (signal_analysis)
- design_analysis.net_classification marks the 5V and 12V nets as 'signal'. The 5V net is driven by U1's power_out pin (VO) and carries regulated 5V supply to output connectors. The 12V net is connected to the power_in VI pins of both U1 and U2. Both are clearly power distribution nets, not signal nets. GND is correctly classified as 'ground'. By contrast, PWR_input and PWR_output are correctly classified as 'power'.
  (design_analysis)

### Missed
- The schematic contains a classic power-on LED indicator: 12V -> S1 (power switch) -> 12V bus -> R1 (330 ohm current limiter) -> D1 (LED anode) -> D1 (LED cathode) -> GND. The components and net connections are all correctly captured in nets and ic_pin_analysis, but the analyzer produces no signal_analysis entry for this LED indicator subcircuit. There is no entry in any signal_analysis list (e.g., a dedicated LED indicator or LED driver detector) that identifies this topology.
  (signal_analysis)

### Suggestions
(none)

---
