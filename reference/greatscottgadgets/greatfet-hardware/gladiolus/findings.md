# Findings: greatscottgadgets/greatfet-hardware / gladiolus

## FND-00000118: GreatFET One (Gladiolus) is an SDR/USB security research board with AD8330 VGA, AD9283 ADC, THS4520 diff amp, AD9704 DAC, and analog switches. The analyzer correctly identifies 7 subcircuits, 10 RF matching networks, 7 voltage dividers, 4 RC filters, and 17 LC filters. However, crystal_circuits falsely identifies 74LVC1G3157 SPDT analog switches as active oscillators, and all 138 components have category=None despite component_types being correctly classified in statistics.

- **Status**: confirmed
- **Analyzer**: schematic
- **Source**: repos/greatfet-hardware/gladiolus/gladiolus.sch
- **Related**: KH-016
- **Created**: 2026-03-14

### Correct
- RF matching networks correctly identified around inductor/capacitor networks near SMA connectors and analog switches
- 7 subcircuits correctly centered on the key ICs: AD8330 VGA, AD9283 ADC, THS4520 diff amp, LMH6643 opamp, AD9704 DAC, and two 74LVC1G3157 switches
- LC filter resonant frequencies calculated correctly (73.41 MHz for 100nH/47pF pairs matches expected RF front-end filtering)
- Voltage divider R7/R8 (3.24k/1.74k, ratio 0.349) correctly identified as VCC bias divider with decoupling cap on midpoint
- Bus analysis correctly detects I2C, SPI, UART, and CAN protocols from net naming
- Power rails correctly identified: GND, VCC, VBUS, VBAT, PWR_FLAG

### Incorrect
- U6 and U7 (74LVC1G3157, SPDT analog switches) falsely classified as crystal_circuits/active_oscillator. These are analog signal routing switches used for RX/TX path selection, not oscillators.
  (signal_analysis.crystal_circuits)
- All 138 components have category=None in the component objects despite statistics.component_types correctly classifying them. The per-component category field is never populated.
  (components[*].category)
- U3 (LNA, BGB741L7ESD) falsely identified as a power_regulator with topology=unknown. This is an RF low-noise amplifier, not a voltage regulator.
  (signal_analysis.power_regulators)
- Subcircuits have empty neighbor_components arrays for all 7 ICs, meaning the analyzer found no nearby passives associated with these ICs. On an RF board like this, every IC has extensive decoupling and matching networks.
  (subcircuits[*].neighbor_components)

### Missed
- No USB interface detection. GreatFET is fundamentally a USB device (the LPC4330 on the main board communicates via USB through the neighbor connectors), but the USB data paths through the neighbor connectors are not identified.
  (design_analysis.bus_analysis)
- The differential signal paths (THS4520 diff amp IN+/IN- to AD9283 differential ADC inputs) are not identified as differential pairs despite being critical to the analog signal chain.
  (design_analysis.differential_pairs)
- No RF chain detection. The board has a clear RF receive chain: SMA -> matching -> analog switch -> LNA/filter -> VGA -> ADC, but rf_chains is empty (only LC filters and RF matching found as fragments).
  (signal_analysis.rf_chains)

### Suggestions
- Crystal circuit detector should check lib_id or description for switch/mux keywords before classifying as oscillator
- Power regulator detector should not match amplifier ICs - check description for LNA/amplifier keywords
- Subcircuit neighbor detection needs improvement for legacy .sch files where connectivity may be impaired by KH-016

---
