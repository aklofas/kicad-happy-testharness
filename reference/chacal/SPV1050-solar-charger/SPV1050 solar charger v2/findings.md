# Findings: chacal/SPV1050-solar-charger / SPV1050 solar charger v2

## FND-00001333: Component counts, BOM, and net extraction are accurate; Voltage dividers correctly detected for MPP and EOC pins; RC filter misidentification: R1/C1 is not a low-pass filter; SPV1050 energy harvest...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: SPV1050 solar charger v2.kicad_sch.json
- **Created**: 2026-03-24

### Correct
- 15 components (1 IC, 3 connectors, 6 resistors, 1 inductor, 4 capacitors), 15 nets, 4 no-connects all match the schematic. Power labels V_PV and BAT correctly extracted.
- Two voltage dividers found: R2/R3 for MPP_SET (pin 2) and R5/R6 for EOC (pin 9). These set the MPPT operating point and end-of-charge threshold respectively. Detection is accurate.
- GND has power_in pins but no PWR_FLAG symbol. This is a real ERC issue in the design. BAT and V_PV no_driver warnings are also correct — they are fed from connectors which lack PWR_FLAG.

### Incorrect
- The analyzer reports R1 (10M) and C1 (4.7uF) as a low-pass filter with 0.00 Hz cutoff. In the SPV1050 circuit, R1 is the solar panel emulation/MPP resistor and C1 is the input bypass cap at V_PV. They share only the V_PV net at one terminal and GND at the other — this is the input decoupling topology, not a signal RC filter. Similarly R4/C3-C4 is the storage capacitor grouping for the STORE pin, not a filter. Both RC filter entries are false positives.
  (signal_analysis)

### Missed
- The SPV1050 is a solar energy harvesting IC with integrated boost converter (inductor L1 connected between IN_LV and L_HV pins), MPPT tracking, and battery charging. The analyzer outputs empty power_regulators and design_observations. It should detect the switching regulator topology from the L1 connection to pin 16 (IN_LV) and pin 19 (L_HV), similar to how it detects TPS61041.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00001334: v1 schematic (14 components, no J3) correctly differentiated from v2 (15 components)

- **Status**: new
- **Analyzer**: schematic
- **Source**: SPV1050 solar charger.kicad_sch.json
- **Created**: 2026-03-24

### Correct
- v1 has 2 connectors vs v2's 3, consistent with absence of the additional J3 header. All other component counts match expectations.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001335: Board dimensions, footprint count, routing completeness correct; Courtyard overlaps correctly flagged on a densely packed board

- **Status**: new
- **Analyzer**: pcb
- **Source**: SPV1050 solar charger v2.kicad_pcb.json
- **Created**: 2026-03-24

### Correct
- 22.9 x 20.15mm board, 15 footprints, 104 track segments, 42 vias, fully routed. Matches the small dense 2-layer SMD design.
- 7 courtyard overlaps detected (J2/R4, C1/U1, J2/U1, U1/C3, C4/C3, C2/R3, R5/R6). This is a small MPPT charger board with a large 20-pin QFN (U1) surrounded by passives, so courtyard overlaps are plausible and worth flagging.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
