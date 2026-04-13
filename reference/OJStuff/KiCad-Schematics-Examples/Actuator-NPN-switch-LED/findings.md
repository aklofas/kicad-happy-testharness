# Findings: OJStuff/KiCad-Schematics-Examples / Actuator-NPN-switch-LED

## FND-00002200: Non-inverting amplifier (gain=10x) misclassified as 'transimpedance_or_buffer'

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: schematic_KiCad-Schematics-Examples_OPamp-noninverting_OPamp-noninverting.kicad_sch.json
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
- The OPamp-noninverting schematic has R1 (1k) from the inverting input to GND and R2 (9k) from the inverting input to the output — a textbook non-inverting configuration with gain = 1 + R2/R1 = 10. The analyzer classifies it as 'transimpedance_or_buffer' instead of 'non_inverting'. The 'transimpedance_or_buffer' label implies either unity gain (voltage follower) or a transimpedance topology, neither of which applies here.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00002201: Parallel LC tank circuit not detected in lc_filters; spurious RC high-pass filter reported instead; Spurious 'high-pass' RC filter reported for R1+C1 in a parallel RLC tank circuit

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: schematic_KiCad-Schematics-Examples_LC-Parallell-resonance_LC-Parallell-resonance.kicad_sch.json
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
- The rc_filters detector reports a high-pass filter (R1=10Ω, C1=1μF, fc=15.9 kHz) for the LC parallel resonance circuit. In this topology, C1 is part of the parallel LC tank between 'In' and 'Out', while R1 is a series damping resistor — not an RC high-pass filter. The out→GND path through R1 is mistaken for an RC filter because the detector only checks pairwise R+C connectivity without considering whether an inductor is also bridging the same nodes.
  (signal_analysis)

### Missed
- The schematic is a parallel RLC tank: L1 and C1 are both connected between the 'In' net and 'Out' net in parallel, with R1 as the series damping resistor. The lc_filter detector only looks for an L and C sharing a single internal node (series topology), so it finds nothing. Instead, the rc_filters detector incorrectly reports a high-pass filter from R1+C1 (cutoff 15.9 kHz), ignoring the inductor entirely. The schematic's own annotation notes f0 = 159 kHz, which is the parallel resonant frequency. The LC-Series-resonance schematic (same component values, series topology) correctly triggers lc_filters with resonant_hz = 159.15 kHz.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00002202: simulation_readiness marks SPICE VDC/VSIN sources as 'needs_model', giving falsely low simulatable_percent; Inverting amplifier configuration correctly identified with accurate gain calculation

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: schematic_KiCad-Schematics-Examples_OPamp-inverting_OPamp-inverting.kicad_sch.json
- **Created**: 2026-03-24

### Correct
- The OPamp-inverting schematic is correctly detected as 'inverting' configuration. The gain is reported as -10.0 (gain_dB=20.0), matching the actual R2/R1 ratio of 10k/1k = 10. The feedback_resistor (R2=10k) and input_resistor (R1=1k) are correctly identified.

### Incorrect
- The OPamp-inverting schematic has 6 components: U1 (OPAMP), R1, R2, V1 (VDC=15V), V2 (VDC=-15V), V3 (VSIN). The simulation_readiness section reports only 3 as 'likely_simulatable' (50%) and flags V1, V2, V3 as 'needs_model'. However, all three are from the Simulation_SPICE library (Simulation_SPICE:VDC, Simulation_SPICE:VSIN) which are built-in ngspice primitives requiring no external model files. The same issue affects many schematics in this corpus: OPamp-freerunning shows 20% (4 of 5 flagged including VDC/VSIN sources plus LM741 from Amplifier_Operational, not Simulation_SPICE), OPamp-adding shows 37.5%, and others. The detector should recognize Simulation_SPICE:VDC and Simulation_SPICE:VSIN as inherently simulatable.
  (simulation_readiness)

### Missed
(none)

### Suggestions
(none)

---

## FND-00002203: Summing (adding) amplifier classified as plain 'inverting' — multiple input resistors not recognized

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: schematic_KiCad-Schematics-Examples_OPamp-adding_OPamp-adding.kicad_sch.json
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
- The OPamp-adding schematic is a summing/adding amplifier: three resistors (R1, R2, R3) all connect to the inverting input of U2, and R3 also serves as the feedback resistor. The analyzer detects it as a plain 'inverting' configuration using only R1 and R3 (input and feedback), missing that R2 is a second input resistor feeding the same summing node. A summing amplifier is a distinct topology (output is weighted sum of inputs) that warrants its own 'summing_inverting' or 'summing' configuration label and gain formula.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00002204: R1/R2 voltage divider bias network for NPN base not detected as voltage_divider

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: schematic_KiCad-Schematics-Examples_NPN-Amplifier-CE_NPN-Amplifier-CE.kicad_sch.json
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
(none)

### Missed
- In the NPN common-emitter amplifier, R1 (48k) connects from Vdc to node Ub, and R2 (7.2k) connects from Ub to GND — a classic resistor divider setting the base bias voltage. The voltage_dividers list is empty. The transistor_circuit entry does correctly capture R1 and R2 as base_resistors and notes base_pulldown=R2, but the explicit voltage divider analysis section does not fire because Vdc is not recognized as a power rail (it's a named signal net, not a power symbol). The divider output feeds the base input, which is a recognized bias topology.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00002205: LM741 open-loop comparator-like schematic classified as 'comparator_or_open_loop' when it is a voltage follower/buffer test circuit

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: schematic_KiCad-Schematics-Examples_OPamp-freerunning_OPamp-freerunning.kicad_sch.json
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
- The OPamp-freerunning schematic has an LM741 with its inverting input (pin 2) tied to GND and a 1MΩ feedback resistor from output to inverting input. With only R1 (1MΩ) as feedback from output to inverting input and a VSIN source at non-inverting input, this is an almost-unity-gain non-inverting amplifier (or freerunning simulation). The analyzer reports 'comparator_or_open_loop' because pin 1 (+) is on the non-inverting input going to In, while pin 2 (-) connects to GND via the feedback network. The configuration should more accurately be 'non_inverting' with very high gain (approaching open loop due to 1MΩ feedback).
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00002206: Zener-referenced constant current source not recognized as a power regulator or current source topology

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: schematic_KiCad-Schematics-Examples_Constant-current-NPN-Zener_Constant-current-NPN-Zener.kicad_sch.json
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
(none)

### Missed
- The schematic is a classic NPN constant-current source: Zener diode D1 (BZX84C5V6, 5.6V) sets the base voltage via R1 (1k), and R2 (80Ω emitter resistor) sets the constant collector current Ic ≈ (Vz - Vbe)/R2 ≈ 60mA. The analyzer detects the transistor circuit correctly (with base_resistors=[R1] and emitter_resistor=R2) but reports zero current_sense entries and zero power_regulators. The Zener diode's role in establishing the reference voltage for the base bias is not captured anywhere in the output.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00002207: NPN LED driver transistor circuit fully characterized with LED load correctly identified

- **Status**: new
- **Analyzer**: schematic
- **Source**: schematic_KiCad-Schematics-Examples_Actuator-NPN-switch-LED_Actuator-NPN-switch-LED.kicad_sch.json
- **Created**: 2026-03-24

### Correct
- The transistor_circuits entry for Q1 correctly identifies the BJT type, emitter_is_ground=true (switch configuration), load_type='resistive', and the led_driver sub-object with D1 (LED), current_resistor Rk1 (150Ω), and base_resistor Rb1 (1k). This is accurate for an NPN transistor switch driving an LED.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00002208: Cascaded high-pass + low-pass RC stages not identified as a bandpass filter

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: schematic_KiCad-Schematics-Examples_RC-Bandpass_RC-Bandpass.kicad_sch.json
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
(none)

### Missed
- The RC-Bandpass schematic connects a high-pass stage (R1=1k, C1=1μF, fc=159 Hz) in series with a low-pass stage (R2=10Ω, C2=1μF, fc=15.9 kHz). Together they form a bandpass filter with passband 159 Hz–15.9 kHz. The analyzer correctly identifies both individual stages as separate rc_filters entries, plus an additional spurious 'RC-network' entry. However, there is no 'bandpass' type entry that synthesizes the two cascaded stages into a single bandpass topology — the fact that a high-pass and low-pass with compatible cutoffs are chained is not flagged as a bandpass.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00002209: Empty PCB file (placeholder only, 78 bytes) correctly analyzed as having zero footprints and zero tracks

- **Status**: new
- **Analyzer**: pcb
- **Source**: pcb_KiCad-Schematics-Examples_Constant-current-NPN-Zener_Constant-current-NPN-Zener.kicad_pcb.json
- **Created**: 2026-03-24

### Correct
- The .kicad_pcb file for Constant-current-NPN-Zener is an empty stub file containing only the version header (78 bytes total, no footprints). The analyzer correctly reports footprint_count=0, track_segments=0, via_count=0, and routing_complete=true. No false positives or crashes.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
