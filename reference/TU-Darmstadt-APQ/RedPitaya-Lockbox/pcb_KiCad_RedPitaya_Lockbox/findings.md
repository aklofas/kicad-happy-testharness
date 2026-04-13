# Findings: TU-Darmstadt-APQ/RedPitaya-Lockbox / pcb_KiCad_RedPitaya_Lockbox

## FND-00001243: LT1236-10 misclassified as LDO with estimated_vout=1.0V; LT3045/LT3094 positive/negative linear regulators detected; Hierarchical sheet references (110 components, 3 sheets) correctly parsed; -12V ...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: RedPitaya_Lockbox.kicad_sch
- **Created**: 2026-03-24

### Correct
- U1 (LT3045EMSE) and U2 (LT3094EMSE) correctly detected as linear regulators with input/output rails and inverting flag. LT8610 switching regulator (U6) correctly detected with feedback divider and switching topology.
- Main schematic correctly aggregates all components from 3 sub-sheets (Supply_Ref, Input_Output_Module, plus main). 110 total components, 72 no-connects, 11 opamp circuits, 4 power regulators all detected. kicad_version=8.0 correctly identified.

### Incorrect
- LT1236-10 is a precision 10V voltage reference, not an LDO regulator. The analyzer assigns topology='LDO' and estimated_vout=1.0V (parsed from the '-10' suffix as 1.0 instead of 10.0V). The output rail is +10V_ref. Both the topology classification and the Vout estimate are wrong. The vout_net_mismatch (1.0V vs 10.0V, 90% difference) is generated but stems from this fundamental misclassification.
  (signal_analysis)
- Same issue as IntStab: in design_analysis.net_classification, '-12V' and '-15V' are classified as 'signal'. These are negative power supply rails from linear regulators. The pattern repeats across both repos confirming a systematic analyzer limitation with negative-polarity power nets.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001244: Lockbox Supply_Ref LT3032-12 also absent from power_regulators

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: Supply_Ref.kicad_sch
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
(none)

### Missed
- Same issue as IntStab: LT3032-12 is present as ic_pin_analysis entry with function='linear regulator' but produces no entry in signal_analysis.power_regulators. The dual +/-15V outputs are not captured.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00001245: Lockbox PCB 110 footprints, 2-layer, fully routed, DFM violation correct

- **Status**: new
- **Analyzer**: pcb
- **Source**: RedPitaya_Lockbox.kicad_pcb
- **Created**: 2026-03-24

### Correct
- 110 footprints, 160x100mm 2-layer board. Routing complete with 0 unrouted nets. DFM board_size violation flagged correctly. min_track_width=0.2mm, min_drill=0.3mm extracted. GND pour on both layers with 244 vias.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
