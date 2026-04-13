# Findings: TU-Darmstadt-APQ/SFH203_photodetector / KiCad_SFH203_photodetector

## FND-00001288: Edge.Cuts counted as a copper layer, inflating copper_layers_used to 3

- **Status**: new
- **Analyzer**: pcb
- **Source**: SFH203_photodetector.kicad_pcb
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
- statistics.copper_layers_used is 3 and copper_layer_names includes 'Edge.Cuts'. This board has 2 copper layers (F.Cu and B.Cu); Edge.Cuts is not a copper layer. The same bug appears in the SNES-Userport-Adapter PCB output.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001289: U1 unit 1 misclassified as 'compensator' — it is a transimpedance amplifier (TIA); signal_analysis.power_regulators is empty despite U2 being an LT3032-12 dual LDO; Dual opamp decoupling correctly ...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: SFH203_photodetector.kicad_sch
- **Created**: 2026-03-24

### Correct
- Both V+ (C8=10u, C4=100n, C6=10n) and V- (C5=100n, C9=10u, C7=10n) rail decoupling is correctly identified and attributed to U1's power pins. The 3-cap per rail strategy matches the schematic.
- statistics.total_components=19, correctly counting both units of U1 (ADA4898-2) and both halves of U2 (LT3032-12). BOM groups them correctly as unique_parts=14.

### Incorrect
- opamp_circuits shows U1 unit 1 as 'compensator' with non-inverting input tied to GND, feedback resistor R1=10k and feedback capacitor C3=2p. This is the classic TIA topology: photodiode D1 drives the inverting input, R1||C3 is the transimpedance feedback. 'transimpedance_amplifier' is the correct classification.
  (signal_analysis)
- U2 (LT3032-12) is a dual linear regulator generating ±12V rails (OUTP=V+, OUTN=V-). The ic_pin_analysis correctly identifies it as 'linear regulator' but power_regulators[] is empty — the detector failed to promote it into the signal_analysis section.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---
