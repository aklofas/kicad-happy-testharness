# Findings: robocup-pcb / boards_on-robot_kicad_kicker-v3.3_kicker

## FND-00000218: Robocup kicker breakbeam sub-sheet (11 components). Correct: Q10 BSS806N MOSFET correctly identified with proper pin mapping and connector load type, R49 pull-up correctly not flagged as divider, power distribution correct. False negative: RV1 500V varistor (PVG3) not detected as protection device. Single-pin net on RV1 pin 1 is expected (NC pin on 3-pin package).

- **Status**: confirmed
- **Analyzer**: schematic
- **Source**: boards_on-robot_kicad_kicker-v3.3_Breakbeam.kicad_sch.json
- **Related**: KH-117
- **Created**: 2026-03-16

### Correct
- Q10 BSS806N N-MOSFET correctly identified with gate=BB_TX, drain→J5, source→GND, load_type=connector
- R49 10k pull-up correctly not flagged as voltage divider (single resistor to supply)
- 0 ERC warnings correctly reported, all connections valid
- BB_TX global label correctly flagged as single-pin net on this sub-sheet (gate drive from parent sheet)

### Incorrect
(none)

### Missed
- RV1 500V varistor (PVG3 package) between +5V and IR LED output not detected as protection device. Varistors should be recognized as TVS/transient protection.
  (signal_analysis.protection_devices)

### Suggestions
- Expand protection device detection to recognize varistors (RV prefix, PVG/MOV/VDR footprints) as transient voltage suppressors

---

## FND-00000221: Robocup kicker HV regulation sub-sheet (48 components, LT3751FE boost converter). Correct: current sense R16 7mohm shunt detected, RC filter R15+C9 gate snubber detected, Q2 IRFS4227 MOSFET correctly identified. False negative: R17(505k)/R18(113k) feedback voltage divider for HV regulation not detected — critical feedback element missed.

- **Status**: confirmed
- **Analyzer**: schematic
- **Source**: boards_on-robot_kicad_kicker-v3.3_HV_-_Regulation.kicad_sch.json
- **Created**: 2026-03-16

### Correct
- R16 7mohm current sense shunt with U3 LT3751FE CSN/CSP pins correctly detected, max current calculations accurate
- R15(22ohm) + C9(220pF) RC filter (32.88MHz cutoff) correctly detected as gate drive snubber for Q2
- Q2 IRFS4227 N-MOSFET correctly identified with gate drive from U3 HVGATE pin
- BOM component counts accurate: 48 total, 12 capacitors, 13 resistors, 1 transistor, 1 diode, 1 IC, 1 transformer

### Incorrect
(none)

### Missed
- R17(505k)/R18(113k) feedback voltage divider from V+ HV rail to U3 FB pin not detected. Ratio=18.3%, critical for boost converter output voltage regulation.
  (signal_analysis.voltage_dividers)

### Suggestions
- Ensure voltage divider detection identifies resistor chains connected to IC feedback pins in power regulation circuits

---
