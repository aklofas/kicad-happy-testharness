# Findings: electrostatic-adhesion-plate / 100100mm_Statikplatte

## FND-00002035: N1..N10 detected as a parallel bus — false positive; these are sequential internal nodes; HV net not classified as high-voltage power — classified as plain 'signal'

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: schematic_electrostatic-adhesion-plate_100100mm_Statikplatte.kicad_sch.json
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
- bus_topology reports prefix='N', width=10, range='N1..N10' as a detected bus signal. In this electrostatic adhesion plate design, N1..N10 are internal node names in a diode-capacitor ladder network (10 stages of series Schottky diodes and capacitors forming a voltage multiplier/charge pump for the HV electrode). They are sequential analog nodes, not a parallel digital bus. The same pattern appears in all three variants: 5050mm detects N1..N6 (6-stage version), DINA5 detects N1..N10. The bus detector should exclude single-letter prefixes like 'N' or require a minimum prefix length to avoid this class of false positive.
  (bus_topology)

### Missed
- The HV net is the high-voltage electrode bus of an electrostatic adhesion plate (typically hundreds to thousands of volts). It is classified as 'signal' in design_analysis.net_classification. A net named 'HV' in a design with a 33M discharge resistor and no IC power supplies (only GND as power rail) should ideally trigger a high-voltage or special-power classification. The misclassification could affect any downstream analysis that uses net class to estimate signal integrity or safety margins. The RC filter with R1=33M and C=1nF is correctly detected but the circuit context (HV discharge path) is not recognized.
  (design_analysis)

### Suggestions
(none)

---

## FND-00002036: GND and HV copper zones classified as zone_stitching — they are functional electrodes

- **Status**: promoted
- **Analyzer**: pcb
- **Source**: pcb_electrostatic-adhesion-plate_100100mm_Statikplatte.kicad_pcb.json
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
- thermal_analysis.zone_stitching lists the GND and HV copper zones (each 2382 mm2, F.Cu only, 2 vias each at 0.1 via/cm2). In an electrostatic adhesion plate, these interdigitated copper zones ARE the functional elements — the electrodes that generate the adhesion force. They are not thermal or electrical stitching planes. The 2 vias per zone are for connectivity, not thermal management. The zone_stitching classification implies thermal intent that does not apply to this design type. The via density of 0.1/cm2 is far below any thermal stitching standard, which should have disqualified these as stitching zones.
  (thermal_analysis)

### Missed
(none)

### Suggestions
(none)

---
