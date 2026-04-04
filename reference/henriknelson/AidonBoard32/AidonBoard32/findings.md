# Findings: AidonBoard32 / AidonBoard32

## FND-00000364: Q4 incorrectly identified as LED driver; U2 (CP2102N) incorrectly listed as gate driver IC for Q1 PMOS

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: AidonBoard32.sch.json
- **Created**: 2026-03-23

### Correct
(none)

### Incorrect
- Q4 (MMBT3904) has collector tied to GND and emitter on UART_RX — it is a signal inverter/level-shifter for the HAN_OUT→UART_RX path, not a LED driver. The analyzer associates it with LED D4 via the led_driver field, but D4/R8 are connected from +3.3V to a net that is not in Q4's collector path. The load_type should not be 'led' and led_driver should be null for Q4.
  (signal_analysis)
- The analyzer lists U2 (CP2102N) in Q1's gate_driver_ics because U2's SUSPEND output pin connects to the VBUS net, which is also Q1's gate net. However, SUSPEND is an output pin that happens to land on VBUS; U2 is not intentionally driving Q1's gate for switching. Q1's gate is at VBUS potential via the VBUS rail, with R1 (100K) to GND for bias — no IC is driving the gate as a switch.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---
