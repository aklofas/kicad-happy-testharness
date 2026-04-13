# Findings: zaoyun/ICL8038_VF / ICL8038_VF

## FND-00000600: ICL8038 waveform generator not recognized as oscillator/function generator; Q1 (S8050-NPN) transistor circuit not detected; R1+C1 reported as low-pass RC filter but R1 is ICL8038 timing resistor; V...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: ICL8038_VF.kicad_sch.json
- **Created**: 2026-03-23

### Correct
- The R4 (12K) / R5 (15K) resistor divider from VCC to GND, with midpoint connected to IC1 pin 1 (duty cycle adjustment), is correctly identified as a voltage divider with ratio 0.556.

### Incorrect
- R1 (15K) connects VCC to IC1 pin 1 (SINE_ADJ1/timing) with C1 (100nF) to GND. The analyzer detects this as a 106 Hz low-pass filter with input_net=VCC. This is a timing/bias network for the ICL8038, not a signal filter. The VCC-as-input-net pattern is again a false positive indicator for RC filter detection.
  (signal_analysis)
- IC1 (ICL8038) uses a custom symbol where all pins are type 'passive', so the analyzer cannot identify VCC/GND rails for the IC. The power_domains.ic_power_rails dict is empty and domain_groups is empty. This is a correct behavioral result given the symbol data, but it means no power domain analysis is performed for the only IC in the design.
  (signal_analysis)

### Missed
- IC1 is an ICL8038 precision waveform generator with SINE_OUT, TRIANGLE_OUT, SQUARE_OUT outputs and a TIMING_CAP pin. The analyzer produces no oscillator, waveform generator, or function generator detection for this IC. The signal_analysis has no relevant category; crystal_circuits and feedback_networks are both empty.
  (signal_analysis)
- Q1 is an S8050 NPN transistor connected on nets __unnamed_3 (collector via R15), __unnamed_14 (base via R14/R13 divider), and __unnamed_16 (emitter via R17). The transistor_circuits list is empty. This is likely because all ICL8038 pins are typed 'passive', causing net classification to fail for base/collector/emitter identification.
  (signal_analysis)

### Suggestions
(none)

---
