# Findings: education_tools / experiment-boards_wien_bridge_oscillator_wien_bridge_oscillator

## FND-00000013: Wien bridge RC filters detected at 145 MHz and 7.2 MHz — likely false positives since Wien bridge operates at audio frequencies. Op-amp classified as comparator_or_open_loop instead of oscillator.

- **Status**: new
- **Analyzer**: schematic
- **Source**: experiment-boards_wien_bridge_oscillator_wien_bridge_oscillator.kicad_sch.json
- **Created**: 2026-03-13

### Correct
- OP97 detected as op-amp (present on board)

### Incorrect
(none)

### Missed
(none)

### Suggestions
- Consider adding oscillator detection (Wien bridge, phase-shift, Colpitts, etc.) as a signal type. The positive feedback around op-amp + matched RC network is a recognizable pattern.

---

## FND-00000021: Differential pair detector matches any X+/X- net name pattern, producing FPs on V+/V- power rails and IN+/IN- opamp inputs. ESD detector then flags opamps as ESD devices.

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: experiment-boards_wien_bridge_oscillator_wien_bridge_oscillator.kicad_sch.json
- **Created**: 2026-03-13

### Correct
(none)

### Incorrect
- IN+/IN- opamp input labels detected as differential pair; V+/V- power rails detected as differential pair
  (signal_analysis)

### Missed
- C7 (22pF) capacitive negative feedback from OUT to IN- not detected — only resistive feedback recognized
  (signal_analysis.feedback_networks)

### Suggestions
- Exclude power nets (V+/V-, VCC/VEE) from diff pair detection. Verify diff pair ICs are actually ESD/protection devices via lib_id. Recognize capacitive feedback paths.

---
