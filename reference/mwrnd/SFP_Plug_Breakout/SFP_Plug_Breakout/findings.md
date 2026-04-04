# Findings: SFP_Plug_Breakout / SFP_Plug_Breakout

## FND-00001290: RX_LOS, TX_FAULT, TX_DISABLE misclassified as UART nets in bus_analysis; SFP I2C management interface (SDA_MOD-DEF2 / SCL_MOD-DEF1) not detected as I2C; Four differential pairs correctly identified...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: SFP_Plug_Breakout.kicad_sch.json
- **Created**: 2026-03-24

### Correct
- differential_pairs contains R_P/R_N, RD_P/RD_N, T_P/T_N, TD_P/TD_N — all four signal pairs in the SFP breakout path (SFP connector side and U.FL connector side). The AC coupling caps (C1-C4) on the differential lines are correctly parsed.

### Incorrect
- bus_analysis.uart lists RX_LOS, TX_FAULT, and TX_DISABLE as UART candidates. These are SFP management signals (open-collector status lines), not UART TX/RX data lines. The name-matching heuristic is triggering on partial matches ('TX', 'RX') rather than actual UART topology.
  (signal_analysis)
- C1-C4 have value 'u01' which the analyzer parsed as 1e-08 F (10nF). The value 'u01' likely means 0.1uF (100nF) — a common shorthand where 'u' is the decimal marker (0u1 = 0.1uF). Parsing as 10nF is incorrect by 10x.
  (signal_analysis)

### Missed
- J1 (SFP+) has SDA (pin 4) and SCL (pin 5) management interface signals. bus_analysis.i2c is empty. These nets are named and typed (SDA=bidirectional, SCL=input) in a way that should be detectable. The R10/R11/R12 10k pull-ups on SDA/SCL/TX_DISABLE are also consistent with I2C but pull-up detection missed them.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00001291: 4-layer board correctly identified with power plane inner layers In1.Cu and In2.Cu

- **Status**: new
- **Analyzer**: pcb
- **Source**: SFP_Plug_Breakout.kicad_pcb.json
- **Created**: 2026-03-24

### Correct
- copper_layers_used=4, copper_layer_names=[B.Cu, F.Cu, In1.Cu, In2.Cu]. Layer types correctly show In1 and In2 as 'power' type. This is consistent with a 4-layer stackup using inner power/ground planes.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
