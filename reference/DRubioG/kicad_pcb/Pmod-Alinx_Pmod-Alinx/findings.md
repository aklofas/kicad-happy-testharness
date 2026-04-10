# Findings: kicad_pcb / Pmod-Alinx_Pmod-Alinx_Pmod-Alinx

## FND-00002361: Pmod connector components (U1-U3) classified as 'ic' type instead of 'connector'; PWR_FLAG warnings incorrectly raised for connector-only passthrough adapter; Pmod connector VCC/GND pins misidentif...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: schematic_kicad_pcb_Pmod-Alinx_Pmod-Alinx_Pmod-Alinx.kicad_sch.json
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
- U1, U2, U3 use footprint 'Pmod:DIP-12_100' and lib_id 'Pmod:Pmod_connector' — these are I/O connectors, not ICs. The analyzer classifies all four components (including the FPGA connector U4 with 'Alinx:DIP-40_100') as type 'ic'. This inflates ic_count and causes spurious decoupling-cap warnings for U1-U3 in design_observations, since connectors don't need local bypass capacitors.
  (statistics)
- The analyzer fires two pwr_flag_warnings (for +3V3 and GND) with 'power_in pins but no power_out or PWR_FLAG'. This design is a pure passthrough adapter: the Alinx FPGA connector (U4) carries +3V3 and GND directly to the three Pmod connectors — there is no MCU or regulator whose ERC needs a PWR_FLAG. The warning is a false positive for connector-only boards where power flows through pins typed 'bidirectional'. The net list shows U4 pins 39/40 typed 'power_in' for VCC_33, and the signal pins of U4 appear as 'bidirectional', which fools the detector.
  (pwr_flag_warnings)
- The power_budget reports only U4 (Alinx_J15) as a power consumer at 10 mA on +3V3, but U1-U3 VCC/GND pins (e.g. pin 1 'VCC' of U1 connected to net 'Pmod2_6') are not on the +3V3 rail at all — they pass FPGA IO signals. The power_budget misses that the Pmod VCC/GND header pins are routed to FPGA IO lines (not to the +3V3/GND power rails). The real +3V3 consumers are the power pins of U1-U3 (pins 6/7 labelled '4'/'5'), which the budget omits.
  (power_budget)

### Missed
(none)

### Suggestions
(none)

---

## FND-00002362: B.Cu correctly identified as 'power' type layer with GND zone and +3V3 tracks

- **Status**: new
- **Analyzer**: pcb
- **Source**: pcb_kicad_pcb_Pmod-Alinx_Pmod-Alinx_Pmod-Alinx.kicad_pcb.json
- **Created**: 2026-03-24

### Correct
- The PCB uses B.Cu exclusively for the +3V3 power distribution (13 segments, 73.98 mm total) and a GND copper pour (fill_ratio 0.637). The analyzer correctly classifies B.Cu as type 'power', identifies the GND zone as filled, and reports power_net_routing with the +3V3 net. Via count of 0 is also correct since all THT pads connect directly between layers.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
