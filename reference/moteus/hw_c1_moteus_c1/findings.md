# Findings: moteus / hw_c1_moteus_c1

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
