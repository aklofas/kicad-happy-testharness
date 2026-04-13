# Findings: XavierBerger/RotaryEncoderDebounced / hardware_RotaryEncoderDebounced

## FND-00001181: Three RC low-pass debounce filters correctly detected (R1/C1, R2/C2, R3/C3) at 1.59 kHz cutoff; Three pull-up resistors (R4, R5, R6) on 3.3 V correctly identified; 74HC14 Schmitt trigger inverter c...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: RotaryEncoderDebounced.kicad_sch
- **Created**: 2026-03-23

### Correct
- Each encoder channel (A, B) and the push-button switch has an RC filter feeding into the 74HC14 Schmitt trigger. The analyzer correctly identifies all three, computes the correct time constant (100 µs) and cutoff frequency.
- The pull-ups on /Rotary_A, /Rotary_B, and /Rotary_SW to +3V3 are all detected with the correct 10k values and 3.3 V rail voltage.

### Incorrect
- The 74HC14 has six inverters; only three are used. The remaining three have their inputs and outputs left as unnamed single-pin nets (undriven), which the analyzer assigns to '__unnamed_N'. These are not flagged as unused gates with floating inputs — a real design concern. The current representation is technically faithful but loses the semantic meaning.
  (signal_analysis)

### Missed
- The design uses three of the six HC14 inverters as Schmitt triggers (one per channel) to clean up the RC-filtered signals. The signal_analysis section has no entry for Schmitt-trigger usage despite the part being a 74HC14. There is no 'schmitt_trigger_circuits' or equivalent field in the output. This is a meaningful design pattern that should be reported.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00001182: PCB statistics accurate: 16 footprints, 2-layer, 23×20 mm, fully routed; Missing switch label warning for SW2 is a false positive — rotary encoder does not need ON/OFF label; Missing connector labe...

- **Status**: promoted
- **Analyzer**: pcb
- **Source**: RotaryEncoderDebounced.kicad_pcb
- **Created**: 2026-03-23

### Correct
- Component counts, board dimensions, track/via counts, and GND copper pour on B.Cu all match the actual design. Decoupling placement analysis correctly associates C4 (100n) and C5 (1u) as the VCC bypass caps for U3.
- Total nets 19, but 8 are unconnected-(U3-PadN) stubs and 2 are mounting-hole stubs. The analyzer correctly reports routing_complete: true with 0 unrouted connections.

### Incorrect
- The PCB analyzer flags SW2 (a rotary encoder with switch) for missing a switch function label ('Add ON/OFF, RESET, BOOT…'). A rotary encoder is not a mode switch and does not require such a label. The warning inappropriately applies switch-label rules to rotary encoder components.
  (signal_analysis)
- The analyzer flags J1 (5-pin header: GND/VCC/SW/B/A) as lacking silkscreen labels, but the board_texts include individual signal name labels ('GND', 'VCC', 'SW', 'B', 'A') printed next to the connector on F.SilkS. The per-pin labels are present; the heuristic misses them because it only checks for a single text block near the connector, not individual pin-name texts.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---
