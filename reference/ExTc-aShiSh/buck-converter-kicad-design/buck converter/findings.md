# Findings: ExTc-aShiSh/buck-converter-kicad-design / buck converter

## FND-00002294: Trimmer1 (Device:R_Trim) misclassified as 'transformer' instead of 'resistor'; Feedback voltage divider (R1+R2 on LM2596 FB pin) not detected as feedback_network or voltage_divider; design_observat...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: schematic_buck-converter-kicad-design_buck converter.kicad_sch.json.json
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
- The component Trimmer1 uses lib_id 'Device:R_Trim' and has description 'Trimmable resistor (preset resistor)' with keywords 'R res resistor variable potentiometer trimmer'. The analyzer assigns it type='transformer' and category='transformer', which is wrong. It should be classified as a resistor or potentiometer. This also causes it to appear in component_types as 'mounting_hole: 1' (for HS1) and 'transformer: 1' (for Trimmer1) rather than the correct resistor count.
  (statistics)
- The design_observations entry for 'regulator_caps' lists both input (__unnamed_3) and output (__unnamed_4) as missing caps. However, ic_pin_analysis for U1 pin VIN (__unnamed_3) shows has_decoupling_cap=true with C1 explicitly listed. The input cap is not missing. Additionally, the output_rail is misidentified as __unnamed_4 (the switching node between U1-OUT, D1, and L1) rather than the actual filtered output __unnamed_0 (where C2 actually lives), causing the output cap to also appear missing.
  (signal_analysis)

### Missed
- R1 (1k) and R2 (3k) form the classic feedback resistor divider from the output to the FB pin of U1 (LM2596T-5), setting the output voltage. The ic_pin_analysis correctly identifies R1 and R2 as connected to the FB pin, but signal_analysis.feedback_networks is empty and signal_analysis.voltage_dividers is empty. This resistor divider is the primary feedback network of the switching regulator and should be detected.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00002295: R3 footprint correctly flagged as outside board boundary (edge_clearance=-4.98mm)

- **Status**: new
- **Analyzer**: pcb
- **Source**: pcb_buck-converter-kicad-design_buck converter.kicad_pcb.json.json
- **Created**: 2026-03-24

### Correct
- The placement_analysis.edge_clearance_warnings correctly identifies R3 with a negative edge clearance of -4.98mm, meaning the component courtyard extends ~5mm outside the board Edge.Cuts boundary. This is a genuine design issue the analyzer correctly caught. Input and output connectors are also flagged with marginal 0.9mm clearance.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
