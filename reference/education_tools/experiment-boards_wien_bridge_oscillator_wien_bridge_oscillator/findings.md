# Findings: education_tools / experiment-boards_wien_bridge_oscillator_wien_bridge_oscillator

## FND-00000013: Wien bridge RC filters detected at 145 MHz and 7.2 MHz — likely false positives since Wien bridge operates at audio frequencies. Op-amp classified as comparator_or_open_loop instead of oscillator.

- **Status**: new
- **Analyzer**: schematic
- **Source**: experiment-boards_wien_bridge_oscillator_wien_bridge_oscillator.kicad_sch.json
- **Created**: 2026-03-13

### Correct
- OP97 detected as op-amp (present on board)

### Incorrect
- R3/C7 at 145 MHz and R9/C7 at 7.2 MHz — these cutoff frequencies are implausibly high for a Wien bridge oscillator. May be picking up unrelated R-C pairs.
  (signal_analysis.rc_filters)

### Missed
- Wien bridge oscillator topology not detected — the positive-feedback loop with frequency-setting RC network is the key feature of this board but has no detector
  (signal_analysis)

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
- OP97 opamp (U1) flagged as ESD protection device on the IN+/IN- "differential pair"
  (signal_analysis.protection_devices)

### Missed
- Wien bridge oscillator topology not detected
  (signal_analysis)
- C7 (22pF) capacitive negative feedback from OUT to IN- not detected — only resistive feedback recognized
  (signal_analysis.feedback_networks)

### Suggestions
- Exclude power nets (V+/V-, VCC/VEE) from diff pair detection. Verify diff pair ICs are actually ESD/protection devices via lib_id. Recognize capacitive feedback paths.

---

## FND-00000022: Both RC filter detections (R3/C7 at 145 MHz, R9/C7 at 7.2 MHz) are false positives — R3 is output termination, R9 is Wien bridge positive feedback, C7 is negative feedback cap. They share the OUT node but serve different functions.

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: experiment-boards_wien_bridge_oscillator_wien_bridge_oscillator.kicad_sch.json
- **Created**: 2026-03-13

### Correct
(none)

### Incorrect
- R3(49.9ohm)/C7(22pF) at 145 MHz — R3 is output series termination, C7 is negative feedback cap. Not an RC filter pair.
  (signal_analysis.rc_filters)
- R9(1k)/C7(22pF) at 7.2 MHz — R9 is Wien bridge positive feedback, C7 is negative feedback. Not an RC filter pair.
  (signal_analysis.rc_filters)

### Missed
(none)

### Suggestions
- RC filter detector should verify R and C form an actual signal path (series or shunt) rather than just sharing a node

---
