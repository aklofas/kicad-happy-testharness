# Findings: Breadboard-power-supply-KiCAD- / Breadboard power supply

## FND-00000415: Bridge rectifier (D1–D4) not detected in bridge_circuits; Spurious RC filter detected between R1 and C2; Net 'V-' misclassified as 'signal' instead of 'power'; design_observations incorrectly repor...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: Breadboard power supply.kicad_sch.json
- **Created**: 2026-03-23

### Correct
(none)

### Incorrect
- The analyzer reports an RC filter with R1 (560Ω) on Vout1→D3A and C2 (47µF) on Vout1→V-. R1 is an LED current-limiting resistor for D5 (D3A net is the LED anode). C2 is the LM7805 output bypass cap. R and C share one node (Vout1) but C2 bypasses Vout1 to ground while R1 routes current to the LED — they do not form a series RC low-pass filter. The reported cutoff_hz of 6.05 Hz is physically meaningless for this topology.
  (signal_analysis)
- V- is the DC negative rail (return path) connecting the bridge rectifier output, all decoupling caps' negative terminals, LED cathodes, regulator GND, and output connector grounds. It is used as a power/ground reference across the entire design and carries 11 pin connections. It should be classified as 'power', not 'signal'.
  (design_analysis)
- The design_observations section reports {"category": "decoupling", "component": "U1", "rails_without_caps": ["Vin"]}. However, C1 (470µF) is directly connected on the Vin net (pin 1 of U1 is Vin, and C1 pin 1 is also on Vin). The ic_pin_analysis for U1 pin 1 itself correctly shows has_decoupling_cap: true with C1 listed. The design_observation is contradictory and incorrect.
  (signal_analysis)
- The assembly_complexity section reports smd_count: 4 and tht_count: 11. Inspection of all footprints shows every component uses a THT package: CP_Radial (C1, C2), D_DO-41 (D1–D4), LED_D5.0mm (D5, D6), R_Axial (R1, R2), PinHeader_2x02 (J1, J2), BarrelJack_CUI (J3), TO-220-3_Vertical (U1), and digikey-footprints:Switch_Slide (SW1). There are no SMD footprints. The smd_count should be 0.
  (assembly_complexity)

### Missed
- D1, D2, D3, D4 are four 1N4007 diodes arranged as a full-wave bridge rectifier fed from J3 (barrel jack). The schematic text annotation 'N2 - Bridge rectifier' confirms this. The signal_analysis.bridge_circuits array is empty — the analyzer failed to recognize the topology.
  (signal_analysis)

### Suggestions
- Fix: Net 'V-' misclassified as 'signal' instead of 'power'

---
