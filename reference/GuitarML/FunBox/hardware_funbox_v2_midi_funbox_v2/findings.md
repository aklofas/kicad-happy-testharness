# Findings: FunBox / hardware_funbox_v2_midi_funbox_v2

## ?: Guitar effects pedal platform (FunBox v2) with Electrosmith Daisy Seed DSP module (A1), stereo audio I/O through TL074 quad op-amp buffer, L7805 5V regulator, H11L1 optocoupler for MIDI input. Very similar to v3 but uses TL074 instead of MCP6024 and has no MCP6002 expression buffer. Accurate analysis.

- **Status**: confirmed
- **Analyzer**: schematic
- **Source**: hardware_funbox_v2_midi_funbox_v2.kicad_sch.json

### Correct
- Three voltage dividers (R5/R6, R7/R10, R11/R12 all 1M/1M) correctly detected as virtual ground generators (VCC/2) feeding U1 (TL074) non-inverting inputs for audio biasing
- Two anti-aliasing RC low-pass filters R2/C4 and R1/C3 (3.3k/2.2nF at 21.92 kHz) correctly detected on audio output paths
- Four op-amp buffer circuits correctly identified: U1 units 1-4 (TL074) all in buffer configuration with gain=1.0
- U2 (L7805) correctly detected as LDO regulator with input=VCC, output=5V
- A1 (Electrosmith_Daisy_Seed_Rev7) correctly classified as IC (DSP module)
- D1 (1N5817) reverse polarity protection and D2 (1N4148) correctly classified as diodes
- U5 (H11L1 optocoupler) correctly classified as IC for MIDI input isolation
- 65 total components: 4 ICs, 11 connectors, 22 resistors, 18 capacitors, 6 switches, 2 LEDs, 2 diodes
- Design observation correctly flags missing VCC decoupling and L7805 input/output caps

### Incorrect
(none)

### Missed
- H11L1 (U5) optocoupler not detected as an isolation_barrier for MIDI input galvanic isolation.
  (signal_analysis.isolation_barriers)

### Suggestions
- Optocoupler ICs (H11L1, 6N138, etc.) should be detected as isolation barriers.

---
