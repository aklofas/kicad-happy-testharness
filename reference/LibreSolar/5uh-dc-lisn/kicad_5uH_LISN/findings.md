# Findings: LibreSolar/5uh-dc-lisn / kicad_5uH_LISN

## FND-00000320: RC filters R8/C6 and R9/C6 misclassified as high-pass instead of low-pass; LC filter formed by L6 (1mH) and C5 (0.47µF) in the LISN measurement branch not detected; MEAS1 (Radiall R141426 BNC conne...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: kicad_5uH_LISN.sch.json
- **Created**: 2026-03-23

### Correct
- The analyzer correctly identifies three resistor pairs (R3/R4, R6/R7, R10/R11) as voltage dividers. In this LISN design, these form a precision resistive impedance-matching network (not traditional signal voltage dividers) that synthesizes the LISN's 50Ω measurement port impedance. The detections are structurally valid (topology matches voltage divider pattern), so this is an accuracy observation rather than a bug. No code change needed.

### Incorrect
- The analyzer detected two RC filters (R8=430Ω+C6=0.47µF and R9=430Ω+C6=0.47µF) and labeled both as 'high-pass'. In the LISN measurement network, R8 and R9 are series resistors from the signal net (__unnamed_13) to the C6 shunt capacitor to GND. With the resistor in series and capacitor shunting to GND (output_net: GND), this is a low-pass configuration, not high-pass. A high-pass filter would have the capacitor in series and resistor to GND.
  (signal_analysis)
- MEAS1 uses the symbol 'R141426' (Radiall part number for a BNC connector, as confirmed by the schematic text note 'BNC connector: Radiall R141426161'). The analyzer categorized it as type 'other' because the symbol name looks like a resistor part number. It should be classified as a connector. The BNC connector is the RF measurement output port of the LISN.
  (statistics)

### Missed
- L6 (1mH Coilcraft 1008PS, value labeled '1m') is the primary inductive element of the LISN measurement impedance network, forming a shunt LC with C5 (0.47µF). This L6+C5 pair resonates at approximately 7.3 kHz and is the fundamental network element defining the LISN's 50Ω measurement impedance characteristic. The analyzer detected only two LC filters (L1+C1||C2 at ~29kHz and L5+C3 at ~480kHz) but missed L6+C5. Only 2 lc_filters are reported; the LISN measurement LC should be a third.
  (signal_analysis)
- The LISN power path consists of five 1.1µH inductors (L1-L5) connected in series between the input banana connector (J1) and the DUT output (J3), forming a 5-stage LC ladder with input capacitors C1 (4.7µF) and C2 (22µF). The analyzer only detected one LC filter pairing (L1 with C1||C2), missing the four additional series inductors (L2, L3, L4, L5 connected in series chain) that are part of the same distributed LC filter. L2, L3, L4 are entirely absent from lc_filter detections. This is architecturally significant for a LISN.
  (signal_analysis)

### Suggestions
- Fix: RC filters R8/C6 and R9/C6 misclassified as high-pass instead of low-pass
- Fix: MEAS1 (Radiall R141426 BNC connector) classified as 'other' instead of 'connector'

---
