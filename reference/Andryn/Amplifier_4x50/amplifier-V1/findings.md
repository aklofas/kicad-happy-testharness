# Findings: Andryn/Amplifier_4x50 / amplifier-V1

## FND-00000365: LC power supply filter not detected; IC1 (LA47516) Vcc supply pins not linked to +12V power domain; Audio amplifier circuit (BTL 4-channel) not recognized in signal analysis; RC filter ground_net i...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: amplifier.sch.json
- **Created**: 2026-03-23

### Correct
- The detected RC filter (R1=10K, C1=1uF, cutoff 15.92 Hz) has ground_net reported as 'IN1', which is actually an audio signal net, not ground. R1 and C1 form a network where one end connects to the IC's IN_RL and ON_TIME pins and the other end connects to the IN1 audio signal net via P2 connector routing. This is not a low-pass filter to ground — the RC topology is incorrect. The ground_net field should reflect the actual reference net, and here the analyzer has incorrectly inferred IN1 as the filter ground.

### Incorrect
(none)

### Missed
- L1 (INDUCTOR) feeds +12V from the input connector (P1) into C2 (2200uF) and C3 (0.022uF), forming a classic LC EMI/bulk supply filter. The lc_filters array is empty. The decoupling_analysis correctly lists C2 and C3 on +12V, but the presence of L1 in series with the supply rail is not captured as an LC filter network. This is the primary power conditioning circuit for a 4x50W amplifier.
  (signal_analysis)
- IC1 has power pins Vcc1/2 (pin 6) and Vcc3/4 (pin 20) which appear as isolated unnamed nets (__unnamed_22 and __unnamed_27) in the output rather than being connected to the +12V rail. The power_domains section lists IC1's power rail only as __unnamed_26 (the VREF decoupling net), completely omitting +12V as the chip's supply. In the schematic the +12V symbol connects via the IC's custom symbol to these Vcc pins. This means the design_analysis.power_domains is inaccurate for the main IC.
  (design_analysis)
- IC1 is the LA47516, a 4-channel BTL audio power amplifier. The four BTL output pairs (OUT1+/OUT1-, OUT2+/OUT2-, OUT3+/OUT3-, OUT4+/OUT4-) are correctly identified as differential pairs, but the design is not recognized as an audio amplifier circuit. The buzzer_speaker_circuits list is empty and there is no amplifier_circuits or audio_amplifier category. Connectors P3-P6 labeled Rear R, Front R, Rear L, Front L are speaker output terminals. The analyzer has no detector for integrated audio power amplifiers feeding speaker loads.
  (signal_analysis)

### Suggestions
(none)

---
