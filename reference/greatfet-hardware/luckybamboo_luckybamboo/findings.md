# Findings: greatfet-hardware / luckybamboo_luckybamboo

## FND-00000124: GreatFET Lucky Bamboo is a 2.4 GHz 802.15.4 radio board with four ADF7242 transceivers, SKY13322 SP4T RF switch, BGA7H1N6 LNA, eight ADF7242 balun/filter modules, and three HHM2293A1 diplexers. The analyzer finds 21 crystal circuits but zero RF chains, zero RF matching networks, and empty neighbor_components for all subcircuits. The crystal circuit detector correctly finds the four XTAL4PIN crystals with 18pF load caps (CL_eff=12pF), but also generates 17 false positives from the balun/diplexer/switch ICs.

- **Status**: confirmed
- **Analyzer**: schematic
- **Source**: repos/greatfet-hardware/luckybamboo/luckybamboo.sch
- **Related**: KH-016
- **Created**: 2026-03-14

### Correct
- Four crystal circuits (X1-X4) correctly detected with XTAL4PIN value and proper 18pF load cap pairs, effective load capacitance calculated as 12pF
- 8 differential pairs detected, likely corresponding to the differential antenna/RF connections between ADF7242 transceivers and their baluns
- Component types correctly classified in statistics: 17 ICs, 83 capacitors, 33 connectors, 11 resistors, 4 crystals, 1 inductor
- Power rails correctly identified: GND, VCC, VBUS, VBAT, PWR_FLAG

### Incorrect
- 17 false positive crystal circuits from balun modules (U8-U17, ADF7242_balun), diplexers (U6-U7, U12 HHM2293A1), LNA (U13 BGA7H1N6), and RF switch (U5 SKY13322). These are all RF components, not oscillators.
  (signal_analysis.crystal_circuits)
- All 153 components have category=None despite correct component_types in statistics
  (components[*].category)
- All 17 subcircuit entries have empty neighbor_components arrays
  (subcircuits[*].neighbor_components)

### Missed
- No RF chain detection despite this being a pure RF design with four ADF7242 transceivers, baluns, diplexers, an LNA, and an SP4T antenna switch
  (signal_analysis.rf_chains)
- No RF matching networks detected despite extensive RF frontend with baluns and matching components
  (signal_analysis.rf_matching)
- ADF7242 transceivers not identified as RF transceivers in any signal analysis section. These are 802.15.4 radios critical to understanding the design.
  (signal_analysis.rf_chains)
- SKY13322 SP4T switch not identified in RF chain despite being the antenna routing switch
  (signal_analysis.rf_chains)
- No SPI bus detection for ADF7242 control interface despite SPI being the primary control bus
  (design_analysis.bus_analysis)

### Suggestions
- Crystal circuit detector needs to filter out RF components (baluns, filters, switches, LNAs) by checking lib_id/description for RF keywords
- RF chain detector should identify transceiver ICs by description keywords like TXRX, transceiver, 802.15.4
- Legacy .sch connectivity issues (KH-016) may explain empty subcircuit neighbors and missing RF chain connections

---
