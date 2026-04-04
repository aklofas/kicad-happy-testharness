# Findings: I2CADC01 / hw_sch_pcb_I2CADC01

## FND-00000597: LTC2485 falsely identified as RS485 transceiver; LM4041-adj voltage reference (D4) misclassified as diode; R3+C8 reported as RC low-pass filter but is a voltage reference bypass network; I2C bus co...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: hw_sch_pcb_I2CADC01.kicad_sch.json
- **Created**: 2026-03-23

### Correct
- design_analysis.bus_analysis.i2c correctly identifies SCL and SDA nets, both with 10k pull-up resistors (R5 to VCC on SCL, R4 to VCC on SDA), and associates them with U1 (LTC2485).
- Both 10k+100nF low-pass filters on IN+ and IN- paths to the LTC2485 are detected with correct 159 Hz cutoff frequency. These are genuine anti-aliasing filters on the ADC inputs.

### Incorrect
- The LTC2485 is a 24-bit I2C delta-sigma ADC. The bus_analysis.rs485 array lists U1/LTC2485 as an RS485 transceiver, almost certainly because '2485' substring-matches an RS485 keyword pattern. The correct detection (I2C with SCL/SDA pull-ups) is present alongside this false positive.
  (signal_analysis)
- D4 has lib_id 'I2CADC01-rescue:REFERENCE' and value 'LM4041-adj'. The LM4041 is a 3-pin shunt voltage reference IC in SOT-23, not a diode. The analyzer assigns category='diode' based on the symbol's pin topology (A/K plus a third pin) rather than recognizing it as a voltage reference. The lib symbol name 'REFERENCE' is not used as a classification hint.
  (signal_analysis)
- R3 (3K3) connects VCC to net __unnamed_7, where C8 (22nF) goes to GND and D4 (LM4041-adj voltage reference) is the load. The analyzer reports this as a 159 Hz low-pass filter with input_net=VCC. This is not a signal filter path — it is the biasing resistor and bypass cap for the shunt voltage reference. The 'input_net: VCC' for an RC filter is a topological red flag that should suppress the detection.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00000598: ICL8038 waveform generator not recognized as oscillator/function generator; Q1 (S8050-NPN) transistor circuit not detected; R1+C1 reported as low-pass RC filter but R1 is ICL8038 timing resistor; V...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: _home_aklofas_Projects_kicad-happy-testharness_repos_ICL8038_VF_ICL8038_VF.kicad_sch.json
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
