# Findings: tushroy/NodePilot / NodePilot

## FND-00000967: PC817 optocouplers and B0505S isolated DC-DC not detected as isolation barriers; Transistor circuits (Q1/Q2/Q4 2N3904) correctly detected with base resistors; RC filters correctly identified includ...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: NodePilot.kicad_sch.json
- **Created**: 2026-03-23

### Correct
- All three BJT circuits detected with correct base_net, base_resistors, and load_type classification. Q1 has R1 (2.2k base), Q2 has R8 (1k base), Q4 has R10 (1k base).
- Seven RC networks detected across multiple ranges (3.39 Hz to 2.25 MHz). The high-pass filter with RV1 (10k pot) + C3 (4.7uF) at 3.39 Hz is reasonable for an audio-path mic circuit.

### Incorrect
(none)

### Missed
- U1 and U2 are PC817 optocouplers (lib_id: Isolator:PC817) and U3 is a B0505S-1WR2 isolated DC-DC converter. The design has two isolated ground domains (AGND1 vs RIGGND). isolation_barriers[] is empty. The analyzer should detect Isolator: library ICs and isolated DC-DC converters as isolation barriers.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00000968: Empty PCB correctly reported with zero footprints and zero tracks

- **Status**: new
- **Analyzer**: pcb
- **Source**: NodePilot.kicad_pcb.json
- **Created**: 2026-03-23

### Correct
- NodePilot.kicad_pcb is a KiCad 9.0 file with no layout data (footprint_count=0, track_segments=0). The analyzer correctly reports an empty board rather than crashing. Silkscreen warnings about missing board name/revision are appropriate.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
