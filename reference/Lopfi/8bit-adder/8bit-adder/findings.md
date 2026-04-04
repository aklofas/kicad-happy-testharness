# Findings: 8bit-adder / 8bit-adder

## FND-00000347: assembly_complexity misclassifies THT axial resistors as other_SMD

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: 8bit-adder.kicad_sch.json
- **Created**: 2026-03-23

### Correct
(none)

### Incorrect
- The _extract_package_info() function checks for THT using keywords ('tht', 'through_hole', 'dip', 'to-220', 'to-92') but 'axial' is absent. All 243 axial resistors with footprint 'RobinsParts:R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal' fall through to 'other_SMD'. The correct smd_count should be ~6 (connectors/USB) not 249; tht_count should be ~342 not 99. The same bug affects adder.kicad_sch (29 axial as SMD) and nand.kicad_sch (3 axial as SMD). Fix: add 'axial' to the THT keyword list in _extract_package_info().
  (assembly_complexity)

### Missed
(none)

### Suggestions
(none)

---
