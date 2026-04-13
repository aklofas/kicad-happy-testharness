# Findings: gameinstance/esp32-audio-player / hardware_esp32_pcm56_st-s505

## FND-00002046: LM79L05 negative voltage regulator misclassified as topology='LDO'; AC/DC mains power module (TMLM10105) not detected as an isolation barrier; Parallel PCM bus to PCM56 DAC not detected; Op-amp inv...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: schematic_esp32-audio-player_hardware_esp32_pcm56_st-s505_esp32_pcm56_st-s505.kicad_sch.json
- **Created**: 2026-03-24

### Correct
- The 4570 dual op-amp (U7, Amplifier_Operational:RC4560) is correctly identified in inverting configuration for both left and right channels (units 1 and 2), with accurate gain calculation of -2.061 (6.3 dB), correctly identifying the feedback resistor (R22/R23 at 6.8k) and input resistor (R24/R25 at 3.3k), and identifying the feedback capacitor (C34/C35) for the HF rolloff. Output nets 'DAC Out (L)' and 'DAC Out (R)' are correctly named.

### Incorrect
- U2 (LM79L05_TO92) is a negative-voltage linear regulator from the LM79 family. It takes a negative input rail and outputs a regulated negative voltage (-Vreg). The analyzer classifies it as topology='LDO', which is architecturally misleading — LDO implies a low-dropout positive regulator. The analyzer should recognize LM79xx lib_id prefixes as negative linear regulators and use a distinct topology label (e.g., 'negative_linear') to avoid confusion with positive LDO regulators.
  (signal_analysis)

### Missed
- PS1 is a TMLM10105 from the KiCad library 'Converter_ACDC' — a TRACO POWER isolated AC/DC module with mains input (AC (L), AC (N), 12V AC (L)) producing isolated DC output. The schematic also has raw AC mains nets. The analyzer: (1) classifies PS1 as type='ic' instead of recognizing it as a power converter, (2) leaves isolation_barriers=[] despite a clear mains-to-SELV isolation boundary, and (3) does not flag the presence of mains voltages (AC (L), AC (N)) in the design. This is a safety-relevant omission.
  (signal_analysis)
- The design uses a parallel PCM bus (PCM_CLK, PCM_LE, PCM_CH1, PCM_CH2) to drive two PCM56 16-bit DACs (U5 and U6). This is a well-defined audio interface. The analyzer detects an SPI bus on the SD card (correctly) and a UART, but does not identify the PCM parallel bus at all. PCM_CLK and PCM_LE are named nets clearly indicating a parallel PCM interface. The PCM56 DACs themselves are classified only as generic 'ic' type with no audio-specific annotation.
  (design_analysis)

### Suggestions
(none)

---
