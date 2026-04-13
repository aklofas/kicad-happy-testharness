# Findings: OLIMEX/BB-ADS1220 / HARDWARE_BB-ADS1220_Rev.A_bb-ads1220

## FND-00000382: REFP label not merging U1 REFP0 pin into REFP net; REFN label not merging U1 REFN0 pin into REFN net; AVSS label not merging U1 AVSS pin into AVSS net; SPI bus not detected despite clear SCLK/DIN/D...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: HARDWARE_BB-ADS1220_Rev.A_bb-ads1220.sch.json
- **Created**: 2026-03-23

### Correct
(none)

### Incorrect
- The net classification assigns 'chip_select' to the AVSS net. AVSS is the analog supply ground (negative supply) of the ADS1220 — a power/ground rail, not a chip select signal. The name 'AVSS' (Analog Voltage Negative Supply) is a standard power rail name. It should be classified as 'ground' or 'power' rather than 'chip_select', which is presumably triggered by the presence of 'SS' in the net name.
  (design_analysis)

### Missed
- The schematic uses a text label 'REFP' at coordinate (5500,2850) to connect U1 pin 9 (REFP0) to the REFP net. The analyzer correctly identifies the REFP net (containing P1 pin 7) and the label, but fails to merge U1 pin 9 (REFP0) into it — placing that pin in an isolated unnamed net '__unnamed_8' with point_count=1. The REFP label at the U1 end should unify these into a single net containing both U1/REFP0 and P1/P7.
  (nets)
- The schematic uses a text label 'REFN' at coordinate (5800,2850) to connect U1 pin 8 (REFN0) to the REFN net. The analyzer correctly identifies the REFN net (containing P1 pin 6) and the label, but fails to merge U1 pin 8 (REFN0) into it — placing that pin in an isolated unnamed net '__unnamed_7' with point_count=1. The REFN label at the U1 end should unify these into a single net containing both U1/REFN0 and P1/P6.
  (nets)
- The schematic uses a text label 'AVSS' at coordinate (4600,4500) to connect U1 pin 5 (AVSS) to the AVSS net. The AVSS net contains C2 pin 2, P1 pin 3, and P2 pin 1, but U1 pin 5 (AVSS) is isolated in unnamed net '__unnamed_4' with point_count=1. The label should have unified U1/AVSS into the same net.
  (nets)
- The ADS1220 is a 24-bit SPI ADC. The schematic wires U1 pin 1 (SCLK) to P2 pin 5, U1 pin 2 (CS#) to P2 pin 4, U1 pin 15 (DOUT/DRDY#) and pin 16 (DIN) to P2 — all canonical SPI signal names. The analyzer returns bus_analysis.spi as an empty array, missing this SPI interface entirely.
  (design_analysis)
- C1, C2, and C3 are all 100nF bypass/decoupling capacitors placed on U1's power rails (AVDD, AVSS/GND, and the DVDD/output side). The signal_analysis.decoupling_analysis array is empty, missing all three. C2 is explicitly on the AVSS supply node, C3 is on the DVDD output pin of U1, and C1 is on the CLK/reference side.
  (signal_analysis)
- The subcircuit for U1 (ADS1220) lists only C3, P1, and P2 as neighbor components. C1 and C2 are also directly associated with U1 — C2 is connected to the AVSS node of U1 (or should be, once the label connectivity bug is resolved) and C1 is placed on the power/CLK side of U1. All three capacitors form U1's local decoupling network and should appear as neighbors.
  (subcircuits)

### Suggestions
(none)

---
