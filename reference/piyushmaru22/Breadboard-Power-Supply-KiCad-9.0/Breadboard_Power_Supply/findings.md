# Findings: piyushmaru22/Breadboard-Power-Supply-KiCad-9.0 / Breadboard_Power_Supply

## FND-00000394: R1+C1 falsely detected as RC low-pass filter; R2+C3 falsely detected as RC low-pass filter; PWR_FLAG warning incorrectly fired for GND net; Named power rails 12V, 3.3V, and 5V classified as 'signal...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: Breadboard_Power_Supply.kicad_sch.json
- **Created**: 2026-03-23

### Correct
(none)

### Incorrect
- The analyzer reports R1 (330Ω) and C1 (10µF) as forming a 48.23 Hz RC low-pass filter with input_net='__unnamed_1' and output_net='12V'. However, R1 is the LED current-limiting resistor (its pin 1 is on the 12V net and pin 2 connects to D1 anode on net __unnamed_1), and C1 is a bulk bypass capacitor on the 12V rail to GND. These two components share a node on 12V but are in completely different functional paths — they do not form an RC filter. The RC filter topology requires R and C in series between the signal and ground with the output taken at their junction, which is not the case here.
  (signal_analysis)
- The analyzer reports R2 (330Ω) and C3 (1µF) as forming a 482.29 Hz RC low-pass filter with input_net='__unnamed_0' (the LM317 ADJ node) and output_net='3.3V'. R2 is the upper resistor in the LM317 feedback network (from the VO output at 3.3V to the ADJ pin), and C3 is the output bypass capacitor on the 3.3V rail. These are distinct functional elements of the LM317 adjustable regulator circuit. They share the 3.3V node but do not form an RC filter — C3 connects between 3.3V and GND as a bypass cap, while R2 connects between 3.3V and the ADJ pin as a feedback element.
  (signal_analysis)
- The pwr_flag_warnings section reports that 'Power rail GND has power_in pins but no power_out or PWR_FLAG'. However, the schematic contains PWR_FLAG symbol #FLG02 placed at (76.2, 124.46) which is on the GND net (wires connect it to GND at 87.63, 124.46). The power_symbols section of the same JSON output correctly lists this PWR_FLAG on GND. The warning is contradicted by data the analyzer itself extracted.
  (pwr_flag_warnings)
- The design_analysis.net_classification section classifies '12V', '3.3V', and '5V' as 'signal' nets. These are clearly power rails: 12V is the input supply fed through J5 (barrel jack) and SW1; 5V is the output of regulator U1 (LM7805); 3.3V is the output of regulator U2 (LM317). All three have voltage regulators driving them and are identified as 'input_rail' and 'output_rail' in the power_regulators section of signal_analysis. They should be classified as 'power' nets.
  (design_analysis)
- The design_observations section flags both U2 (LM317) and U1 (LM7805) under 'regulator_caps' as having missing_caps for input and output rails. In reality: U1 has C1 (10µF) on its 12V input and C2 (0.1µF) on its 5V output — both confirmed present in ic_pin_analysis. U2 has C1 (10µF) on its 12V input and C3 (1µF) on its 3.3V output — also confirmed present. The decoupling_caps_by_rail field for both U1 and U2 in ic_pin_analysis correctly lists these caps. The design_observations 'missing_caps' flag contradicts the analyzer's own ic_pin_analysis findings.
  (signal_analysis)
- assembly_complexity reports smd_count=7, tht_count=10, other_SMD=7, and unique_footprints=2. All 17 components in the BOM use footprints with 'THT' in their library name (Capacitor_THT, LED_THT, Resistor_THT, Package_TO_SOT_THT, Button_Switch_THT) or are connectors. The 7 SMD count likely corresponds to the 7 connector components (J1–J7) whose footprints are resolved from the PCB lib (PinHeader, TerminalBlock, BarrelJack) — none of which are SMD. Additionally, there are at least 9 distinct footprints in the BOM, not 2.
  (assembly_complexity)

### Missed
- The LM317 circuit uses R2 (330Ω, from VO/3.3V to ADJ) and R3 (560Ω, from ADJ to GND) as the standard feedback resistor divider that sets the output voltage. This is a classic voltage divider topology. The signal_analysis.voltage_dividers array is empty, even though R2 and R3 form a textbook resistive divider from the 3.3V output to GND with the tap connected to the LM317 ADJ pin. The expected output voltage would be Vref*(1 + R2/R3) + Iadj*R2 ≈ 1.25*(1 + 330/560) ≈ 1.25*1.589 ≈ ~2.0V (close to the labeled 3.3V with component tolerances and Iadj). This feedback divider is the primary design feature of the adjustable regulator sub-circuit and its omission from voltage_dividers is a missed detection.
  (signal_analysis)

### Suggestions
- Fix: Named power rails 12V, 3.3V, and 5V classified as 'signal' instead of 'power'

---
