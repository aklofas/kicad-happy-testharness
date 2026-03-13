# Findings: moteus / hw_c1_moteus_c1

## FND-00000049: OUTX motor output falsely classified as UART

- **Status**: new
- **Analyzer**: schematic
- **Source**: hw_c1_moteus_c1.kicad_sch.json
- **Related**: KH-022
- **Created**: 2026-03-13

### Correct
(none)

### Incorrect
- 27-pin net on DRV8323 matched by UART detector. OUTX is a motor phase output, not a UART signal.
  (signal_analysis.bus_protocols)

### Missed
(none)

### Suggestions
- Exclude high-pin-count nets and motor driver outputs from UART detection

---

## FND-00000050: Current sense shunts (2mOhm) not detected

- **Status**: new
- **Analyzer**: schematic
- **Source**: hw_c1_moteus_c1.kicad_sch.json
- **Created**: 2026-03-13

### Correct
(none)

### Incorrect
(none)

### Missed
- 3x R4/R5/R6 with Kelvin connections and anti-alias RC filters feeding DRV8323 integrated CSA. current_sense=[]. 2mOhm shunt resistors not detected.
  (signal_analysis.current_sense)

### Suggestions
- Detect very low value resistors (< 100mOhm) as current sense shunts, especially when connected to CSA/sense amplifier inputs

---

## FND-00000051: Three-phase bridge nets all identical (OUTX, GHX, GLX, SPX_Q)

- **Status**: new
- **Analyzer**: schematic
- **Source**: hw_c1_moteus_c1.kicad_sch.json
- **Related**: KH-026
- **Created**: 2026-03-13

### Correct
(none)

### Incorrect
- h_bridge.kicad_sch instantiated 3x but nets not namespaced per instance. All three phases share identical net names OUTX, GHX, GLX, SPX_Q instead of phase-specific names.
  (nets)

### Missed
(none)

### Suggestions
- Namespace nets per hierarchical sheet instance to distinguish phase A/B/C

---

## FND-00000052: DRV8323_SCLK miscategorized as I2C (SCL substring)

- **Status**: new
- **Analyzer**: schematic
- **Source**: hw_c1_moteus_c1.kicad_sch.json
- **Created**: 2026-03-13

### Correct
(none)

### Incorrect
- DRV8323_SCLK matched as I2C SCL due to substring match. SCLK is an SPI clock signal, not I2C.
  (signal_analysis.bus_protocols)

### Missed
(none)

### Suggestions
- Use word-boundary matching for SCL to avoid matching SCLK (SPI clock)

---

## FND-00000053: CAN_RX/CAN_TX categorized as UART in test_coverage

- **Status**: new
- **Analyzer**: schematic
- **Source**: hw_c1_moteus_c1.kicad_sch.json
- **Related**: KH-022
- **Created**: 2026-03-13

### Correct
(none)

### Incorrect
- CAN_RX/CAN_TX nets matched by UART detector due to RX/TX naming pattern. These are CAN bus signals.
  (signal_analysis.bus_protocols)

### Missed
(none)

### Suggestions
- Exclude nets with CAN prefix from UART RX/TX pattern matching

---

## FND-00000054: SXX_P/SXX_N current sense nets falsely detected as differential pair

- **Status**: new
- **Analyzer**: schematic
- **Source**: hw_c1_moteus_c1.kicad_sch.json
- **Related**: KH-018
- **Created**: 2026-03-13

### Correct
(none)

### Incorrect
- Current sense nets with _P/_N suffix matched as differential pairs. These are single-ended sense lines from shunt resistors, not differential signaling.
  (signal_analysis.differential_pairs)

### Missed
(none)

### Suggestions
- Verify differential pair candidates are actually used for differential signaling, not just named with _P/_N suffix

---

## FND-00000055: VBAT_SENSE classified as power rail

- **Status**: new
- **Analyzer**: schematic
- **Source**: hw_c1_moteus_c1.kicad_sch.json
- **Created**: 2026-03-13

### Correct
(none)

### Incorrect
- VBAT_SENSE is an ADC sense net but matches VBAT power pattern and is classified as a power rail.
  (signal_analysis.power_rails)

### Missed
(none)

### Suggestions
- Exclude nets with _SENSE/_FB/_ADC suffix from power rail classification

---

## FND-00000056: DRV8323 gate driver not characterized (bootstrap caps, CSA)

- **Status**: new
- **Analyzer**: schematic
- **Source**: hw_c1_moteus_c1.kicad_sch.json
- **Created**: 2026-03-13

### Correct
(none)

### Incorrect
(none)

### Missed
- DRV8323 is a three-phase gate driver with bootstrap capacitors and integrated current sense amplifier. Not characterized as a gate driver circuit.
  (signal_analysis)

### Suggestions
- Add gate driver detection for DRV83xx family and similar motor driver ICs

---

## FND-00000057: CAN 120-ohm termination not linked to CAN bus detection

- **Status**: new
- **Analyzer**: schematic
- **Source**: hw_c1_moteus_c1.kicad_sch.json
- **Created**: 2026-03-13

### Correct
(none)

### Incorrect
(none)

### Missed
- CAN bus 120-ohm termination resistor present but not linked to CAN bus protocol detection.
  (signal_analysis.bus_protocols)

### Suggestions
- When detecting CAN bus, also identify termination resistors (120 ohm between CANH/CANL)

---

## FND-00000058: NTC thermistor not recognized in voltage divider

- **Status**: new
- **Analyzer**: schematic
- **Source**: hw_c1_moteus_c1.kicad_sch.json
- **Created**: 2026-03-13

### Correct
(none)

### Incorrect
(none)

### Missed
- NTC thermistor in voltage divider configuration for temperature sensing not recognized as a thermistor circuit.
  (signal_analysis)

### Suggestions
- Detect NTC/PTC thermistors in voltage divider circuits as temperature sensing

---
