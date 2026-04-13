# Findings: greatscottgadgets/LNA3030 / LNA3030

## FND-00000140: LNA3030 is nearly identical to LNA1109 - a Great Scott Gadgets LNA board with BGB741L7ESD LNA, SAW filter (FAR-F5QA vs DCC6C variant), GRF6011 switches, TVS diodes, and SMA connectors. Same 26 components, same topology. Exhibits identical analyzer issues as LNA1109: LNA falsely classified as power regulator, false crystal circuits, empty component categories, and fragmented RF chain detection.

- **Status**: confirmed
- **Analyzer**: schematic
- **Source**: repos/LNA3030/LNA3030.sch
- **Related**: KH-016
- **Created**: 2026-03-14

### Correct
- Same correct detections as LNA1109: RF chain finds amplifier U3 and filter U4, RF matching from SMA to switch, TVS protection on RF inputs, decoupling on VCC
- Component count and net structure consistent with the near-identical LNA1109 design (26 vs 25 components)

### Incorrect
- Same false positive as LNA1109: U3 (LNA) classified as power_regulator
  (signal_analysis.power_regulators)
- Same false positive crystal circuits as LNA1109
  (signal_analysis.crystal_circuits)
- All 26 components have category=None
  (components[*].category)

### Missed
- Same as LNA1109: complete RF signal path not traced, LNA bias network not identified, operating frequency not inferred
  (signal_analysis.rf_chains)

### Suggestions
- Same fixes as LNA1109 apply - this validates that the issues are systematic, not project-specific

---
