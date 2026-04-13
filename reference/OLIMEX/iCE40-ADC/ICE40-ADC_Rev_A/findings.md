# Findings: OLIMEX/iCE40-ADC / ICE40-ADC_Rev_A

## FND-00002139: SR1 (TLV431 shunt voltage reference) misclassified as 'switch'; SIG_IN1 (BNC connector) also misclassified as 'switch'; Decoupling analysis empty for U1 (ADC08100) because all its supply pins conne...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: schematic_iCE40-ADC_ICE40-ADC_Rev_A.sch.json.json
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
- SR1 has lib_id 'TLV431BSN1T1G(SOT23-3)' and value 'NA(TLV431BSN1T1G(SOT23-3))'. The TLV431 is a precision programmable shunt voltage reference (3-pin: REF, CATHODE, ANODE), used here to set the ADC reference voltage. It is classified as type 'switch' because the library ID does not match any recognized IC or reference voltage patterns, and it falls through to the switch category. SIG_IN1 (BNC-JD11-50-LF) is the RF input connector for the ADC signal input, but is also classified as 'switch'. Both should be classified as 'connector' or a dedicated 'voltage_reference' type.
  (components)

### Missed
- U1 (ADC08100CIMTCX) is an 8-bit 100MSPS ADC with multiple supply pins (VA, AGND, DRVD, DRGND) all connecting to unnamed nets (__unnamed_2, __unnamed_4, __unnamed_7, __unnamed_8, etc.) that are filtered from the main +3.3V and GND rails by ferrite beads L1 and L2. Decoupling caps C3, C5, C6, C7 are correctly placed on these supply nets in the schematic, but the decoupling_analysis array is empty because the detector only searches for caps by matching named rail names. No decoupling coverage warning is generated for U1, and the design_observations only warn about U2 (buffer IC). This is a systematic limitation when ferrite-bead power filtering creates unnamed local supply domains.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00002140: F.SilkS extends 13.9mm beyond the board edge outline but is not flagged as an alignment issue

- **Status**: promoted
- **Analyzer**: gerber
- **Source**: gerber_iCE40-ADC_Gerbers.json.json
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
(none)

### Missed
- The Edge.Cuts outline is 30.0 x 50.0mm but F.SilkS extents are 43.893 x 57.575mm — roughly 14mm wider and 7.5mm taller than the board boundary. This indicates silkscreen text or graphics outside the board outline (likely pin labels on the IDC connector headers that hang off the edge). The alignment checker reports aligned=True with no issues. The same overflow occurs in both iCE40-DAC Rev A and Rev A1 gerbers (F.SilkS 43.893 x 56.813mm vs 30 x 50mm board). The gerber analyzer should flag silkscreen layers that significantly exceed Edge.Cuts dimensions.
  (alignment)

### Suggestions
(none)

---

## FND-00002141: DFM correctly identifies challenging-tier annular ring (0.075mm) in this 30x50mm 2-layer ADC board

- **Status**: promoted
- **Analyzer**: pcb
- **Source**: pcb_iCE40-ADC_ICE40-ADC_Rev_A.kicad_pcb.json.json
- **Created**: 2026-03-24

### Correct
- The PCB analyzer correctly identifies 52 footprints (all SMD), 2 copper layers, and flags the 0.075mm annular ring as below the advanced process minimum of 0.1mm, requiring the 'challenging' fabrication tier. Net count is 53 in the PCB vs 85 in the schematic — the discrepancy arises because many schematic nets are unnamed bus signals that are wired by position in the legacy .sch format rather than by net label.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
