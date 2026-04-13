# Findings: Kotbenek/geiger-counter / sensor_board

## FND-00000212: 16-channel photodiode sensor board using BPW34 photodiodes with AP331A comparators and BC849C BJT signal conditioning. The analyzer correctly identified the 32 transistor circuits, voltage reference divider, and 66 RC filter stages. It missed the comparator-based signal discriminator topology and the MMTL431B voltage reference function.

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: sensor_board_sensor_board.kicad_sch.json
- **Created**: 2026-03-15

### Correct
- Voltage divider R99 (4k7) / R100 (1k) correctly detected feeding Vref net to all 16 comparator non-inverting inputs (U1-U16 AP331A pin 3) with bypass caps
- 32 BC849C BJT transistor circuits correctly analyzed with base resistors (2M2 for input stages, 220k for cascade stages), emitter resistors (1k), and correct base/collector/emitter net assignments
- 66 RC filter stages correctly detected including 16 low-pass filters (220k + 100nF, ~7.23 Hz) for sensor biasing, 16 high-pass filters (10k + 100nF, ~159 Hz) for AC coupling, and 16 RC-networks (4k7 + 100nF) for collector pull-up filtering
- 16 BPW34 photodiodes correctly classified as diode type (D1-D16)
- 16x AP331A comparators correctly classified as IC type
- Decoupling analysis correctly identified 16x 100nF caps on Vcc rail (1.6uF total, bypass only, no bulk)
- 16 SHIELD connectors (J1-J16) correctly classified as connector type for photodiode shield connections

### Incorrect
(none)

### Missed
- U17 MMTL431B is a shunt voltage reference/regulator generating the 18V bias rail but is not detected in power_regulators. The TL431 family are programmable shunt regulators commonly used for voltage regulation.
  (signal_analysis.power_regulators)
- The 16 AP331A comparators (U1-U16) are used as signal discriminators for the photodiode channels but are not detected in opamp_circuits. While comparators are distinct from op-amps, they share the same topology and the analyzer should recognize comparator-based circuits.
  (signal_analysis.opamp_circuits)

### Suggestions
- Add TL431/MMTL431 family to power_regulators detection as shunt voltage reference/regulator
- Detect comparator ICs (AP331A, LM339, LM393, etc.) in opamp_circuits section with configuration=comparator
- Consider adding photodiode detection for BPW34 and similar parts (more specific than generic diode classification)

---
