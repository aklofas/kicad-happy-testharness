# Findings: 6IN14NixieShield / 6IN14NixieShield

## FND-00000323: 6 WS2812B LEDs detected as 6 separate single-LED chains instead of one daisy-chain of 6; Boost converter transistor circuit (Q1 IRF740 MOSFET) not detected; Discrete boost converter not detected as...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: 6IN14NixieShield.sch.json
- **Created**: 2026-03-23

### Correct
(none)

### Incorrect
- In design_analysis.power_domains, U8 (K155ID1 Soviet-era BCD-to-decimal decoder) is listed with power_rails=['+5V', 'DRV_C']. DRV_C is a BCD digit-select input pin (equivalent to the 'C' bit input of the BCD decoder), not a power supply pin. The K155ID1 is driven by a 4-bit BCD code on inputs DRV_A, DRV_B, DRV_C, DRV_D to select which Nixie cathode to drive. The analyzer appears to have mistakenly added DRV_C to the power rail list for this IC.
  (design_analysis)

### Missed
- In tubes.sch, D1 through D6 (WS2812B) are wired as a single serial daisy-chain: the NEOPIXEL net enters D1's DIN, D1's DOUT feeds D2's DIN, D2's DOUT feeds D3's DIN, etc. The analyzer reports 6 chains of chain_length=1 rather than 1 chain of chain_length=6. The data_in_net is empty for all 6 entries, confirming the chain linkage between the DIN/DOUT connections across the tube positions was not traced.
  (signal_analysis)
- boost.sch contains Q1 (IRF740 N-channel power MOSFET) acting as the switching element for the high-voltage boost converter. It is driven via gate resistor R8 (22Ω) from the PWM net, with its drain connected to inductor L1 and its source to GND. The analyzer reports transistor_circuits=0, missing this switching transistor that is the heart of the +HV Nixie power supply.
  (signal_analysis)
- boost.sch implements a complete discrete boost converter producing ~170V for Nixie tubes: L1 (470uH inductor), Q1 (IRF740 MOSFET switch), D7 (HER106 fast rectifier), C7 (4.7uF/350V output cap), R7/R10 feedback divider, R9 (100k), R8 (22Ω gate resistor), F1 (1A polyfuse). The +HV rail is explicitly used as the Nixie anode supply. The analyzer reports power_regulators=0, missing this boost converter entirely.
  (signal_analysis)
- nixie_ctl.sch contains 7 TLP627 optocouplers (U1-U7), each providing galvanic isolation between the 3.3V/5V Arduino control domain and the high-voltage Nixie tube anode drive domain. Each TLP627 has CTL_A1..CTL_A6 and CTL_Adots on its LED input side and ANODE_1..ANODE_6 and ANODE_dots on its phototransistor output side switching the high voltage. The analyzer reports isolation_barriers=0.
  (signal_analysis)
- boost.sch uses R9 (100k) connected between the PWM input net and the gate of Q1 (via R8=22Ω), forming a simple RC-style gate drive path. Additionally, the feedback network with R7/R10 and the FB output connects back through JP1. While the voltage divider R7/R10 is detected, the associated RC snubber or filter aspects of the gate drive (R8+parasitic) are not captured. The analyzer reports rc_filters=0 and snubbers=0.
  (signal_analysis)

### Suggestions
- Fix: K155ID1 BCD decoder has DRV_C incorrectly listed as its power rail

---
