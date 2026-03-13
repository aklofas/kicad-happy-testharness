# Findings: education_tools / experiment-boards_op_amp_experimenter_op_amp_experimenter

## FND-00000011: Op-amp circuit detection correctly identifies LM741 inverting config (gain=-100, R2=10k/R12=100ohm) and two LM358 comparator configurations

- **Status**: confirmed
- **Analyzer**: schematic
- **Source**: experiment-boards_op_amp_experimenter_op_amp_experimenter.kicad_sch.json
- **Created**: 2026-03-13

### Correct
- LM741 U2 correctly detected as inverting with gain=-100 (R2=10k, R12=100)
- LM358 U1 units correctly detected as comparator/open_loop
- 1 RC filter detected on the board

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00000020: LM741 U2 classified as inverting amplifier with gain=-100 but R2 does NOT bridge OUT and IN- nets. R2 connects to experimenter socket, not the opamp output.

- **Status**: confirmed
- **Analyzer**: schematic
- **Source**: experiment-boards_op_amp_experimenter_op_amp_experimenter.kicad_sch.json
- **Created**: 2026-03-13

### Correct
(none)

### Incorrect
- U2 classified as inverting (gain=-100, R2=10k feedback, R12=100 input) but R2 does not actually connect between OUT and IN- — it goes to an experimenter connector socket. Detector uses heuristic without verifying actual net bridging.
  (signal_analysis.opamp_circuits)

### Missed
(none)

### Suggestions
- Verify that the feedback resistor actually bridges the opamp output net and inverting input net before classifying as inverting/non-inverting

---
