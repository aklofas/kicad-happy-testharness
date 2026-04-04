# Findings: 3.3V-3A-step-down-converter-powered-by-USB-C / KiCad_USB power port

## FND-00000316: rf_matching false positive: bootstrap cap C7 and power inductor L1 misidentified as RF matching network; bridge_circuits false positive: Q5 and Q6 (two N-channel 2N7002s) misdetected as half-bridge...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: KiCad_USB power port.kicad_sch.json
- **Created**: 2026-03-23

### Correct
(none)

### Incorrect
- The rf_matching detector reports C7 (0.1uF capacitor) as an 'antenna' with L1 (3.3uH inductor) as a 'matching component' targeting U1 (TPS54331). This is completely wrong. C7 is the BOOT pin bootstrap capacitor of the TPS54331 switching regulator (connected between the BOOT and PH pins to charge the gate driver), and L1 is the power output inductor in the buck converter stage. There is no RF circuit anywhere in this design — it is a USB-C powered 3.3V/3A buck converter. The proximity of C7 and L1 to U1 has apparently triggered a spurious RF matching network pattern.
  (signal_analysis)
- The bridge_circuits detector reports Q5 (N-channel 2N7002) as the 'high_side' and Q6 (N-channel 2N7002) as the 'low_side' of a half-bridge. A true half-bridge requires a high-side device (typically P-channel or bootstrap-driven N-channel) in series with a low-side N-channel, sharing an output node. Both Q5 and Q6 are N-channel MOSFETs using the AO3400A (N-channel) symbol. They are positioned near the USB CC detection/signaling circuit with test points TP1/TP2 (CC1/CC2), LM358 comparators, and Q4 (another N-channel 2N7002). They are independent logic-level switches for USB CC line control, not a half-bridge power stage. Q4 is absent from the bridge detection despite being of the same type and in the same area.
  (signal_analysis)
- R1 (47k) and C5 (1.5nF) are detected as a 'high-pass' RC filter with cutoff 2.26 kHz. While topologically a series-RC to GND does form a high-pass from the resistor's perspective, R1 and C5 are connected to the COMP pin (pin 6) of U1 (TPS54331). This is a Type II or Type III compensation network for the switching regulator's control loop, not a signal filter. Its purpose is loop stability compensation, not frequency filtering of a signal path. The classification as a generic RC filter (rather than a regulator compensation network) is a functional misclassification.
  (signal_analysis)
- The LM358 (U2) is a dual op-amp. Units 1 and 2 are the actual amplifier stages (correctly detected as comparators). Unit 3 in the KiCad symbol represents the power supply pins (V+ and V-), not an amplifier stage. The analyzer emits a third opamp_circuits entry for U2 unit 3 with configuration 'unknown'. This is a non-functional unit entry that should not appear as an opamp circuit detection. It inflates the opamp_circuits count from 2 (actual comparator stages) to 3.
  (signal_analysis)

### Missed
- The TPS54331 (U1) is a feedback-controlled switching regulator whose output voltage is set by a resistor divider from the +3V3 output rail to the VSNS pin (pin 5). The subcircuit neighbors include R8 (10k) and R9 (3.3K) which form this feedback divider. The analyzer detects 0 feedback_networks despite U1 being a power_regulator with a VSNS pin and associated resistor divider. The voltage divider detector detected R5/R6 (a different divider generating the 0.65V CC reference) but missed the regulator feedback network.
  (signal_analysis)

### Suggestions
- Fix: RC filter R1+C5 classified as high-pass filter; it is the COMP pin compensation network for TPS54331

---
