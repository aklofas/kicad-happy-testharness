# Findings: mfkiwl/KiwiSDR_PCB / KiwiSDR_kiwi

## FND-00000274: KiwiSDR SDR receiver (KiCad 5, 173 components). Core RF path well detected: 6 LC filter pairs in 30MHz anti-alias chain, LTC6401-20 ADC driver, TCXO, 4 power regulators. Two KiCad 5 legacy pin-swap bugs: LMR10530Y fb_net='SW1' instead of 'FB', and LTC6401-20 +IN/-IN and +OUT/-OUT systematically swapped.

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: KiwiSDR_kiwi.sch.json
- **Related**: KH-101
- **Created**: 2026-03-16

### Correct
- LTC2248 ADC and RF lowpass filter chain with 6 LC pairs at correct frequencies
- 16.368MHz TCXO correctly classified as active_oscillator
- 4 power regulators correct: LMR10530Y buck 1.0V, LP5907 LDOs 1.8V and 3.3V
- SAW filter, SE4150L GPS LNA, Artix-7 FPGA correctly classified

### Incorrect
- LMR10530Y (U701) fb_net='SW1' instead of 'FB' — KiCad 5 legacy pin-position-matching swaps SW (pin 7/8) and FB (pin 5) due to close y-coordinates
  (signal_analysis.power_regulators)
- LTC6401-20 (U405) +IN/-IN and +OUT/-OUT pins systematically swapped — same KiCad 5 pin-position bug, paired pins swap
  (signal_analysis.opamp_circuits)

### Missed
(none)

### Suggestions
- Verify KH-101 fix covers multi-pin ICs with close pin spacing
- Detect XO/oscillator components (lib_id='XO') as crystal_circuits

---

## FND-00000275: KiwiSDR active antenna combiner (144 components). RF amplifier chain with 8 JFET/BJT transistors well detected. JFETs misclassified as 'mosfet'. P-channel JFET J271 has is_pchannel=false. 2-emitter BJTs (NPN_2E/PNP_2E) have emitter_net=null. Bridge rectifier not detected.

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: active_antenna_comb_comb.sch.json
- **Created**: 2026-03-16

### Correct
- All 8 transistors detected with gate/base connections captured
- TPS7A4501 and LM2941 LDOs correctly identified
- L202+C218 LC filter at 25.3Hz for power ripple correctly identified
- Q201 MMBT4401 capacitance multiplier with base RC filter correctly detected
- 5 RC snubber networks at bridge rectifier correctly detected

### Incorrect
- J310 N-JFETs and J271 P-JFET (Q501/Q502/Q507) typed as 'mosfet' — lib_id clearly indicates N_JFET/P_JFET
  (signal_analysis.transistor_circuits)
- Q502 J271 P_JFET has is_pchannel=false — 'p_jfet' not in P-channel detection patterns
  (signal_analysis.transistor_circuits)
- Q503-Q506 (NPN_2E/PNP_2E 2-emitter BJTs) have emitter_net=null — pin detector looks for 'E'/'EMITTER' but these use 'E1'/'E2'
  (signal_analysis.transistor_circuits)

### Missed
- Bridge rectifier D201 (BR 0.5A 400V) not detected in bridge_circuits — detector focuses on H-bridge FETs, not diode bridges
  (signal_analysis.bridge_circuits)

### Suggestions
- Add JFET vs MOSFET distinction based on lib_id containing 'jfet'
- Add 'p_jfet' to P-channel detection patterns
- Extend emitter pin detection to include 'E1'/'E2' for multi-emitter BJT packages
- Detect diode bridge rectifier topology in bridge_circuits

---
