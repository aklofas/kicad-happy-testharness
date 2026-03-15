# Findings: mutable_eurorack_kicad / ripples_hardware_design_pcb_KiCad_ripples_v40

## FND-00000163: Mutable Instruments Ripples filter module. Eagle-imported schematic with empty instance Values causes catastrophic power symbol net naming failure -- all power/ground connections dumped into single empty-string net.

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: ripples_hardware_design_pcb_KiCad_ripples_v40.kicad_sch.json
- **Related**: KH-088
- **Created**: 2026-03-15

### Correct
(none)

### Incorrect
- All power symbols (GND, VCC, VEE) have empty net names because instance Value is '' -- lib_symbol has correct values but analyzer never falls back to them. 127 pins in empty-string net.
  (nets)
- F1-F4 fiducials (lib_id *:FIDUCIAL1X2) classified as fuse via F->fuse single-char prefix fallback
  (statistics.component_types)

### Missed
- Zero voltage dividers detected due to empty component values from Eagle import
  (signal_analysis.voltage_dividers)
- Zero RC filters detected due to empty component values
  (signal_analysis.rc_filters)
- Op-amp configurations default to comparator_or_open_loop because feedback/input resistors can't be identified without parsed values -- 316 of 475 (66%) op-amp detections across all modules are wrong
  (signal_analysis.opamp_circuits)
- LM13700 OTA and SSM2164 VCA not recognized as op-amp-like circuits
  (signal_analysis.opamp_circuits)

### Suggestions
- Fall back to lib_symbol Value when instance Value is empty -- fixes power symbol net naming
- This single fix cascades to fix voltage dividers, RC filters, and op-amp configurations
- Add fiducial override: lib_id containing 'fiducial' should override F->fuse classification

---
