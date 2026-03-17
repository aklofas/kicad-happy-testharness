# Findings: DEVLPR / DEVLPR

## FND-00000238: EMG amplifier (40 components). 0 opamp circuits detected despite 3x OPA187 + 1x OPA2375 (4 active instances). 0 instrumentation amp circuits despite INA821. Dual +/-3V3 supply -3V3 rail decoupling not analyzed.

- **Status**: confirmed
- **Analyzer**: schematic
- **Source**: DEVLPR.sch.json
- **Created**: 2026-03-16

### Correct
(none)

### Incorrect
(none)

### Missed
- Dual +/-3V3 supply: -3V3 rail decoupling not analyzed
  (signal_analysis.decoupling)

### Suggestions
- Detect OPA187/OPA2375 as opamp circuits
- Detect INA821 as instrumentation amplifier
- Analyze negative rail decoupling for dual supply designs

---
