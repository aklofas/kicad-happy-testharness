# Findings: LibreSolar/bms-8s50-ic / kicad_bms-8s50-ic

## FND-00002287: BMS cell_count reported as 7 but ISL94202 design is an 8S BMS; False positive I2C bus detection on SCL/SDA nets that are ISL94202 non-I2C pins; RJ45 connectors JP1/JP2 misclassified as type 'jumper...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: schematic_bms-8s50-ic_kicad_bms-8s50-ic.sch.json
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
- The analyzer reports cell_count=7 with cell_nets=['VC3','VC4','VC5','VC6','VC7'] (5 nets). However, inspecting the nets shows VC1 through VC8 all connect to U7 (ISL94202), meaning there are 8 cell taps (VC0 is the bottom reference, VC1–VC8 are the 8 cell boundaries). The ISL94202 is explicitly an 8-cell BMS IC. The analyzer is only counting the VC nets it can match to a specific pattern and undercounting by 3 (VC1, VC2, and the inference from VC8). Expected cell_count=8.
  (signal_analysis)
- The analyzer reports two i2c_bus observations for nets named 'SCL' and 'SDA' connected to U7 (ISL94202). Inspection of the actual net connections shows: the 'SCL' net connects only to U7/FETSOFF (an input pin that controls FET gate-off, not an I2C clock), and the 'SDA' net connects to U7/~INT (output) and U7/RGO (power_out). Neither net is an I2C bus — they are control and power pins that happen to share names with common I2C net labels. The I2C detection should require at least one connected device with an actual I2C role, not just net name pattern matching.
  (signal_analysis)
- JP1 and JP2 have value 'RJ45_NS' (an 8P8C RJ45 connector from Amphenol) but are classified as 'jumper' type in the BOM and statistics. This is because the analyzer uses the reference prefix 'JP' to infer jumper type, overriding the value. The component_types shows jumper=3 (should be 1, just JP3 which is a Jumper_NC_Small) and connector=9 (should be 11). RJ45 connectors should be classified as connectors regardless of their reference prefix.
  (statistics)

### Missed
- The ISL94202 has dedicated current sense input pins CSI1 and CSI2. Nets CSI1 and CSI2 are present in the schematic: CSI2 connects to Q10/Q11 source, R57/R58, and several capacitors (a current sensing node); CSI1 connects to a bypass capacitor. The analyzer reports current_sense=[] (empty). The ISL94202's built-in current sense path via CSI1/CSI2 should be detectable since the pins are named and nets are populated.
  (signal_analysis)

### Suggestions
(none)

---
