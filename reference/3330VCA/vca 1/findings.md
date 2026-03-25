# Findings: 3330VCA / vca 1

## FND-00000318: TL072 opamps (U1, U3) not detected as opamp_circuits; Positive feedback networks on U1 not detected; C1 counted twice in rc_filters due to shared node with R1 and RV1; Decoupling analysis correctly...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: vca 1.sch.json
- **Created**: 2026-03-23

### Correct
- The analyzer correctly detects 3x100nF caps (C14, C12, C16) on +15V and 3x100nF caps (C13, C15, C17) on -15V, each totaling 0.3µF. The observation that bulk capacitance is absent is accurate — this is a Eurorack module that relies on the rack PSU for bulk filtering.

### Incorrect
- C1 (220nF) is physically one capacitor connected at net __unnamed_18 where both R1 (100K) and RV1 wiper (100k pot) meet. The analyzer reports two separate RC filters: R1+C1 (7.23 Hz) and RV1+C1 (7.23 Hz). These represent one RC network with a parallel resistor path (R1 in parallel with RV1 wiper resistance), not two independent filters. This inflates the rc_filters count by 1.
  (signal_analysis)

### Missed
- The schematic contains two TL072 dual opamps: U1 (2 stages as CV signal processors/buffers) and U3 (2 stages as unity-gain output buffers after the AS3330 VCA outputs). All 4 opamp stages are undetected. opamp_circuits is reported as 0. This is likely because the legacy KiCad 5 TL072 symbol lib_id ('TL072') is not recognized by the opamp detector.
  (signal_analysis)
- U1 unit 1 has R12 (100K) connecting output (pin 1) back to the non-inverting input (pin 3) via net __unnamed_25/__unnamed_35. U1 unit 2 has R28 (100K) connecting output (pin 7) back to the non-inverting input (pin 5) via net __unnamed_37/__unnamed_36. Both form positive feedback configurations. feedback_networks is 0 in the output.
  (signal_analysis)

### Suggestions
(none)

---
