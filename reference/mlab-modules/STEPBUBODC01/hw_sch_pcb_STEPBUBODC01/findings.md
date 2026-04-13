# Findings: mlab-modules/STEPBUBODC01 / hw_sch_pcb_STEPBUBODC01

## FND-00001297: TPS631000 buck-boost correctly detected as switching regulator with L1, V_in/V_out rails; design_observations incorrectly flags missing input and output caps for TPS631000; Feedback voltage divider...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: STEPBUBODC01.kicad_sch
- **Created**: 2026-03-24

### Correct
- power_regulators correctly identifies U1=TPS631000DRLR as switching, with inductor L1, input_rail=V_in, output_rail=V_out, and fb_net=FB.

### Incorrect
- The 'regulator_caps' observation claims input (V_in) and output (V_out) caps are missing, but the schematic has C1=22uF (input), C2=47uF (output), C3=10uF. The analyzer failed to associate these caps with the correct rails.
  (signal_analysis)
- V_in and V_out are driven by external connectors J2/J5/J6 (header pins typed as 'input' in the library). These rails are externally driven; the ERC warning is a false positive caused by connector pin types, not a real design error.
  (signal_analysis)

### Missed
- R1=91k, R2=511k, R3=806k form output feedback dividers for the TPS631000. voltage_dividers is empty. These are standard switching regulator feedback networks.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00001298: PCB stats correct: 23 footprints, 2-layer, 30x30mm, routing complete

- **Status**: new
- **Analyzer**: pcb
- **Source**: STEPBUBODC01.kicad_pcb
- **Created**: 2026-03-24

### Correct
- Component count (23), board dimensions (~30x30mm), via_count=6, routing_complete=true all appear accurate for this small buck-boost module.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001299: Gerber set complete, all 9 layers present, aligned, correct component count

- **Status**: new
- **Analyzer**: gerber
- **Source**: hw_cam_profi_gbr
- **Created**: 2026-03-24

### Correct
- completeness=true, aligned=true. B.Mask x2_component_count=23 matches PCB footprint count. F.Paste empty is expected (all front-side pads are THT connectors).

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
