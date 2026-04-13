# Findings: stffrdhrn/kicad-spice-demo / spicedemo

## FND-00002267: Opamp comparator circuit (LM193 with feedback resistors) not detected as opamp_circuit; VSS power rail classified as 'ground' rather than a negative/secondary supply

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: schematic_kicad-spice-demo_spicedemo.sch.json.json
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
- The design uses VCC for U1 pin 4 (V-) and VSS for U1 pin 8 (V+). This is an inverted labeling — in this SPICE demo schematic VSS likely represents a positive supply voltage while VCC is the negative rail (or the naming is inverted relative to convention). The analyzer classifies VSS as 'ground' in net_classification, but VSS has power_in pins and is treated as a distinct supply by the LM193. Additionally, the power_domains analysis only lists U1 as belonging to the 'VCC' domain and omits 'VSS', even though U1's V+ pin (pin 8) is connected to VSS. The decoupling observation correctly flags VCC without a cap, but VSS without a cap is not flagged.
  (design_analysis)

### Missed
- The design has a single LM193 comparator (U1, lib_id='LM193') with R1 (2K) on the non-inverting input and R2 (50K) + R3 (2K) forming a feedback/output network. Despite opamp_circuits being an analyzer detector, signal_analysis.opamp_circuits is empty. The LM193 is a dual voltage comparator with open-collector output — it is correctly identified as type 'ic' and there is a subcircuit grouping U1 with R1, but the opamp/comparator circuit topology itself was not recognized. The analyzer should detect this from the lib_id 'LM193' or the open_collector output pin type on pin 1.
  (signal_analysis)

### Suggestions
(none)

---
