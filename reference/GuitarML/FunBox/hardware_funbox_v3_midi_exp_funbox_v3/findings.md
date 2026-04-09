# Findings: GuitarML/FunBox / hardware_funbox_v3_midi_exp_funbox_v3

## FND-00002556: Guitar effects pedal platform (FunBox v3) with Electrosmith Daisy Seed DSP module (A1), stereo audio I/O through MCP6024 quad op-amp buffer, MCP6002 expression pedal buffer, L7805 5V regulator, H11L1 optocoupler for MIDI input, and 3 footswitches. Thorough and largely accurate analysis.

- **Status**: confirmed
- **Analyzer**: schematic
- **Source**: hardware_funbox_v3_midi_exp_funbox_v3.kicad_sch.json

### Correct
- Three voltage dividers (R5/R6, R7/R10, R11/R12 all 1M/1M) correctly detected as virtual ground generators (VCC/2) feeding U1 (MCP6024) non-inverting inputs at pins 12, 5, and 10 for audio biasing
- Two anti-aliasing RC low-pass filters R2/C4 and R1/C3 (3.3k/2.2nF at 21.92 kHz) correctly detected on AUDIO_OUT_BUFFER_LEFT and AUDIO_OUT_BUFFER_RIGHT output paths
- Six op-amp buffer circuits correctly identified: U3 units 1,2 (MCP6002) and U1 units 1,2,3,4 (MCP6024) all in buffer configuration with gain=1.0
- U2 (L7805) correctly detected as LDO regulator with input=VCC, output=5V
- A1 (Electrosmith_Daisy_Seed_Rev7) correctly classified as IC (DSP module)
- D1 (1N5817) and D2 (1N4148) correctly classified as diodes; D1 provides reverse polarity protection on VCC input
- U5 (H11L1 optocoupler) correctly classified as IC for MIDI input isolation
- 64 total components: 5 ICs, 11 connectors, 20 resistors, 18 capacitors, 6 switches, 2 LEDs, 2 diodes
- Design observation correctly flags missing decoupling caps on VCC rail for A1 and U2
- Design observation correctly flags missing input/output caps for L7805 regulator

### Incorrect
(none)

### Missed
- H11L1 (U5) optocoupler not detected as an isolation_barrier. The H11L1 is a phototransistor optocoupler specifically used for MIDI input galvanic isolation, which is a textbook isolation barrier.
  (signal_analysis.isolation_barriers)

### Suggestions
- Optocoupler ICs (H11L1, 6N138, PC900, etc.) should be detected as isolation barriers when used in MIDI or other isolation circuits.

---
