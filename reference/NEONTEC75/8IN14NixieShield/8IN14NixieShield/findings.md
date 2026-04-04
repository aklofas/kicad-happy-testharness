# Findings: 8IN14NixieShield / 8IN14NixieShield

## FND-00000328: 8 WS2812B LEDs in a single daisy chain reported as 8 separate chains of length 1

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: tubes.sch.json
- **Created**: 2026-03-23

### Correct
(none)

### Incorrect
- In tubes.sch, the 8 WS2812B LEDs (D1-D8) are connected in a single daisy chain: NEOPIXEL -> R13 (100 ohm series resistor) -> D1 DIN, then D1 DOUT -> D2 DIN -> D3 DIN -> ... -> D8 DIN via direct wire connections. The wires explicitly connect each LED's DOUT to the next LED's DIN (e.g., wire at y=5900 from x=2100 to x=2650 connects D1 DOUT to D2 DIN, then 3250-3800 for D2->D3, etc.). The analyzer reports 8 separate chains of length 1 each instead of 1 chain of length 8. This is because the WS2812B components use a custom library symbol (8IN14Lib:WS2812B) whose pin data is not resolved in the net list — the chain topology cannot be traced and each LED is treated as an isolated chain. The correct result is addressable_led_chains with 1 entry, chain_length=8, first_led=D1, last_led=D8.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00000329: 8 WS2812B LEDs (aggregated from tubes.sch) reported as 8 chains of length 1 in top-level output

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: 8IN14NixieShield.sch.json
- **Created**: 2026-03-23

### Correct
(none)

### Incorrect
- The top-level 8IN14NixieShield.sch.json aggregates all sub-sheets. The same WS2812B daisy-chain miscount from tubes.sch propagates here: 8 chains of length 1 are reported instead of 1 chain of length 8. The 8 WS2812B LEDs D1-D8 in tubes.sch are explicitly wired in sequence and form one chain driven from the NEOPIXEL signal via a 100-ohm series resistor.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00000330: 8 TLP627 optocouplers not detected as isolation barriers

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: nixie_ctl.sch.json
- **Created**: 2026-03-23

### Correct
(none)

### Incorrect
(none)

### Missed
- nixie_ctl.sch contains 8 TLP627 phototransistor optocouplers (U1-U8) from the Isolator library (lib_id: Isolator:TLP627). These are galvanic isolation devices used to isolate the low-voltage control signals (ACTL_1 through ACTL_8) from the high-voltage anode drive signals. The analyzer reports isolation_barriers: [] despite 8 TLP627 isolators being present. The TLP627 is a well-known optocoupler from Toshiba.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00000331: Boost converter MOSFET (IRF740 Q1) not detected as a transistor circuit

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: boost.sch.json
- **Created**: 2026-03-23

### Correct
(none)

### Incorrect
(none)

### Missed
- boost.sch implements a discrete boost converter using an IRF740 power MOSFET (Q1, lib_id: Transistor_FET:IRF740), a 470uH inductor (L1), a HER106 rectifier diode (D9), a 4.7uF/350V output capacitor (C9), a gate resistor R2 (22 ohm), and a voltage divider (R1=300k / R4=4.7k) for feedback. The analyzer detects the voltage divider correctly but reports transistor_circuits: []. The IRF740 is a well-known TO-220 power MOSFET and this is a straightforward switched-mode boost converter topology that should be detectable as a transistor switching circuit.
  (signal_analysis)

### Suggestions
(none)

---
