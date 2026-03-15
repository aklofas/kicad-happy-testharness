# Findings: yardstick / yardstickone_yardstickone

## FND-00000144: YardStick One is a Great Scott Gadgets sub-1GHz RF tool with CC1111 (8051+radio SoC), TX/RX amplifiers (SPF5043Z TX, RX MMIC), SKY13251 SP3T RF switches, LPF filter, and AP7313 3.3V LDO. The analyzer correctly identifies 9 subcircuits, the crystal circuit (48 MHz), AP7313 power regulator, 2 RC filters (33ohm/47pF at 102 MHz), 3 LC filters, and 1 protection device. This is a well-analyzed design with good RF component identification.

- **Status**: confirmed
- **Analyzer**: schematic
- **Source**: repos/yardstick/yardstickone/yardstickone.sch
- **Related**: KH-047
- **Created**: 2026-03-14

### Correct
- CC1111 transceiver correctly identified as subcircuit with neighbor components (capacitors, crystal load caps, etc.)
- TX amplifier (U7, SPF5043Z) and RX amplifier (U4) correctly identified as subcircuits
- SKY13251 SP3T RF switches (U5, U6) correctly identified as subcircuits
- Crystal X1 (48 MHz clock) correctly detected with frequency parsed from value string
- AP7313-33SAG LDO correctly identified as power regulator
- Two 33ohm/47pF RC low-pass filters at 102.6 MHz correctly calculated - these are likely RF signal conditioning
- SSM6L36FE dual MOSFET packages (U3, U8) identified as subcircuits - these are antenna switch driver FETs
- LPF (U9, lowpass filter GSM/CDMA 915MHz) correctly identified in subcircuit list
- VBUS and 3V3 power rails correctly identified with PWR_FLAG

### Incorrect
- All 79 components have category=None despite correct component_types in statistics (35 capacitors, 17 resistors, 9 ICs, 8 connectors, 3 LEDs, etc.)
  (components[*].category)
- Subcircuit neighbor_components include ALL board components for every subcircuit (e.g., AP7313 subcircuit lists crystal load caps C10/C11 as neighbors). The spatial proximity algorithm seems to match everything on this compact board.
  (subcircuits[*].neighbor_components)

### Missed
- No RF chain detection despite having a clear TX chain (CC1111 -> RF switch -> TX amp -> antenna) and RX chain (antenna -> RF switch -> LPF -> RX amp -> CC1111)
  (signal_analysis.rf_chains)
- USB interface not detected. CC1111 has built-in USB that connects through the board connector. Net names and pin types should reveal the USB data lines.
  (design_analysis.bus_analysis)
- TX/RX antenna switching topology not identified. The two SKY13251 SP3T switches with SSM6L36FE driver MOSFETs form the antenna diversity/path selection circuit.
  (signal_analysis.rf_chains)
- No RF matching network detection despite having matching components around the RF switches and amplifiers
  (signal_analysis.rf_matching)

### Suggestions
- RF chain detection should leverage subcircuit data to build signal paths between identified RF ICs
- Subcircuit neighbor algorithm needs distance thresholding to avoid matching entire small boards
- CC1111 is a well-known RF SoC that could be identified by MPN for automatic protocol/frequency annotation

---
