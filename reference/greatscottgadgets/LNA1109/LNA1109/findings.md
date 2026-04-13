# Findings: greatscottgadgets/LNA1109 / LNA1109

## FND-00000137: LNA1109 is a Great Scott Gadgets low noise amplifier board for 1090 MHz (ADS-B). Uses BGB741L7ESD LNA, FAR-F5QA SAW filter, two GRF6011 RF switches, TVS protection diodes, and SMA connectors. The analyzer correctly detects the RF chain (1 amplifier + 1 filter), 5 LC filters with resonant frequencies around 73 MHz, RF matching network from SMA to switch, and 2 TVS protection devices. However, the LNA is falsely classified as a power regulator, and crystal circuits falsely fire on 4 entries.

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: repos/LNA1109/LNA1109.sch
- **Related**: KH-016
- **Created**: 2026-03-14

### Correct
- RF chain correctly identifies U3 (LNA/BGB741L7ESD) as amplifier and U4 (SAW/FAR-F5QA) as filter - the two key active RF components
- RF matching network from SMA connector P1 to RF switch U2 correctly identified with 47pF caps and 100nH inductor
- TVS protection diodes D1 and D2 correctly identified as protection devices on the RF input paths
- Decoupling analysis correctly identifies VCC rail with 3 capacitors (1uF bulk + 100pF bypass) with self-resonant frequencies
- LC filter resonant frequencies around 73 MHz correctly calculated for 100nH/47pF pairs (close to but not at the 1090 MHz operating frequency, as these are bias/decoupling networks)
- LED indicator (D4 LNALED) correctly detected in component list

### Incorrect
- U3 (LNA, BGB741L7ESD) falsely classified as power_regulator with topology=unknown. This is the core low-noise amplifier, not a voltage regulator. The fb_net assignment to an RF signal net is incorrect.
  (signal_analysis.power_regulators)
- 4 false positive crystal circuits detected. The LNA1109 has no crystals or oscillators - all active components are RF switches and an amplifier. The crystal detector is likely matching on capacitor-inductor networks near ICs.
  (signal_analysis.crystal_circuits)
- All 25 components have category=None. On a 25-component board, accurate categorization is especially important for design understanding.
  (components[*].category)
- U1 and U2 (SWITCH/GRF6011) are RF SPDT switches but have no classification identifying them as RF switches. Their value is just SWITCH with no further context.
  (components)
- RF chain shows 0 connections between the amplifier and filter, meaning the signal path U1->U3->U4->U2 is not traced
  (signal_analysis.rf_chains.connections)

### Missed
- Complete RF signal path not traced: SMA_IN -> TVS -> RF_switch_U1 -> matching -> LNA_U3 -> SAW_U4 -> RF_switch_U2 -> SMA_OUT. Only fragments detected.
  (signal_analysis.rf_chains)
- The bypass/enable path controlled by R1 (3k) and R2 (470) for the LNA bias is not identified as an LNA bias network
  (signal_analysis)
- Operating frequency of 1090 MHz (ADS-B) not inferred from the SAW filter FAR-F5QA part number or from the matching network component values
  (signal_analysis.rf_chains)

### Suggestions
- Power regulator detector should not match components whose lib_id or description contains LNA, amplifier, or RF amplifier keywords
- Crystal circuit detector should verify the presence of actual crystal/oscillator component values or footprints before classifying
- RF chain connection tracing should follow nets between identified RF components to build the complete signal path

---
