# Findings: eurorack-kicad / AK4458VN_breakout_AK4458VN_breakout

## FND-00000258: AK4458VN 8-ch DAC breakout (85 components). False parallel cap in RC filter inflates capacitance 10x. I2C config pins falsely detected as bus lines. NE5532 difference amplifiers classified as compensator. I2S/TDM audio interface not detected (no detector exists).

- **Status**: confirmed
- **Analyzer**: schematic
- **Source**: AK4458VN_breakout_AK4458VN_breakout.kicad_sch.json
- **Created**: 2026-03-16

### Correct
- Power regulators correctly detected
- AK4458VN correctly classified as IC

### Incorrect
- RC filter R32(150ohm)+C14(120pF) falsely groups C11(1nF) as parallel — C11 shares only the input node, not the output node. Reported fc=947kHz vs correct 8.84MHz
  (signal_analysis.rc_filters)
- AK4458VN pin 17 'I2C' (mode-select config pin) and pin 15 'CAD0_I2C/CSN/_DIF' (address/CS pin) falsely detected as I2C bus lines
  (signal_analysis.bus_interfaces)
- NE5532 differential-to-single-ended output stages (U4-U7) classified as 'compensator' instead of difference amplifier
  (signal_analysis.opamp_circuits)

### Missed
- I2S/TDM serial audio interface not detected — all 4 AK4458VN data bus signals present (MCLK, BICK, LRCK, SDTI1-4) but no I2S detector exists
  (signal_analysis.bus_interfaces)

### Suggestions
- Parallel-cap detection must verify both caps share the same two terminal nodes
- I2C bus detection should check for actual SDA/SCL bus topology, not just pin name substrings
- Add I2S/TDM audio serial interface detector

---

## FND-00000259: Eurorack switch sequencer with Pico + TL072 (133 components). TMUX4051PWR analog mux falsely classified as isolation barrier.

- **Status**: confirmed
- **Analyzer**: schematic
- **Source**: switch_sequencer_switch_sequencer_switch_sequencer.kicad_sch.json
- **Created**: 2026-03-16

### Correct
- WS2812B addressable LED chain correctly detected
- LDO regulator correctly detected
- TL072 buffer/comparator classifications correct

### Incorrect
- U1 TMUX4051PWR analog multiplexer falsely classified as isolation barrier — it straddles GND/GNDA domains but provides no galvanic isolation; it is a CMOS analog mux
  (signal_analysis.isolation_barriers)

### Missed
(none)

### Suggestions
- Isolation barrier detection should require actual isolation components (optocouplers, transformers, capacitive isolators), not just dual-ground-domain devices

---

## FND-00000260: Teensy 4.0 eurorack DC interface with AK4458VN DAC (143 components). Teensy GPIO pins with I2C-capable names trigger false I2C bus detections.

- **Status**: confirmed
- **Analyzer**: schematic
- **Source**: teensy_dc_interface_teensy_dc_interface.kicad_sch.json
- **Created**: 2026-03-16

### Correct
- NE5532 inverting amp stages correctly identified
- DAC output anti-aliasing RC filters correctly detected
- Legitimate I2C bus (SDA/SCL to AK4458VN) correctly detected

### Incorrect
- 4 spurious I2C entries from Teensy 4.0 multi-function pin names containing SCL1/SDA1/SCL2/SDA2 — these pins used as analog inputs or unconnected in this design
  (signal_analysis.bus_interfaces)

### Missed
(none)

### Suggestions
- I2C detection should require actual bus topology (pull-ups, multiple devices) not just pin name pattern matching

---
