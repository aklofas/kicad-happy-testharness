# Findings: hackclub/OnBoard / projects_Trail-Laser-Tag_src_DevIos-Sensor

## FND-00000105: Simple IR receiver board with two TSOP38438 IR receivers, a decoupling cap, and a current limiting resistor. Minimal design correctly analyzed.

- **Status**: confirmed
- **Analyzer**: schematic
- **Source**: repos/OnBoard/projects/Trail-Laser-Tag/src/DevIos-Sensor/DevIos-Sensor.kicad_sch
- **Created**: 2026-03-14

### Correct
- Two TSOP38438 IR receivers correctly identified as IC type
- Two 3-pin connectors for signal output correctly classified
- RC filter detected (R1 100R + C1 100nF) which is the recommended TSOP power supply filtering
- GND power rail correctly detected

### Incorrect
- C1 is typed as C_Polarized (Device:C_Polarized) but value 100nF suggests it is likely a ceramic capacitor, not polarized. However this is the schematic symbol choice, not an analyzer error.
  (bom)

### Missed
(none)

### Suggestions
- The two IR receivers with outputs combined on one net could be noted as a design observation about redundant/multi-zone IR sensing

---
