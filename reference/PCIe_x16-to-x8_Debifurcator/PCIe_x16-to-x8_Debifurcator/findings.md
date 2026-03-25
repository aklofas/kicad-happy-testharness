# Findings: PCIe_x16-to-x8_Debifurcator / PCIe_x16-to-x8_Debifurcator

## FND-00001070: Component counts, BOM, DNP flag, power rails all correct; assembly_complexity reports all 8 components as SMD with 0 THT — wrong; pwr_flag_warnings fires on +12V and +3.3VA — false positives for PC...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: PCIe_x16-to-x8_Debifurcator.kicad_sch.json
- **Created**: 2026-03-23

### Correct
- 8 total components (4 TP, 2 PCIe connectors, 1 cap, 1 resistor DNP) correctly parsed. Power rails +12V, +3.3V, +3.3VA, GND identified. Empty signal_analysis is correct for a passive PCIe lane passthrough with no active circuitry.

### Incorrect
- The 4 test points (TP1-TP4) use PinHeader_1.00mm footprints (THT), and the 2 PCIe connectors are PCB-edge type. PCB output confirms 4 THT and 2 SMD. The schematic assembly_complexity analyzer is not recognizing PinHeader footprints as THT, inflating SMD count and zeroing THT count.
  (signal_analysis)
- +12V and +3.3VA are supplied by the PCIe x16 edge connector (J2), which is a passive connector pin, not a power source in the schematic sense. These warnings are expected for pass-through PCIe designs and are not real ERC issues.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001071: PCB statistics correct: 4-layer, 8 footprints (4 THT, 2 SMD, 2 excluded), 98 nets, fully routed

- **Status**: new
- **Analyzer**: pcb
- **Source**: PCIe_x16-to-x8_Debifurcator.kicad_pcb.json
- **Created**: 2026-03-23

### Correct
- 4 copper layers (F.Cu, In1.Cu, In2.Cu, B.Cu) correctly detected. 933 track segments, 126 vias, 1 zone. Footprint types correctly classified: TP1-TP4 as through_hole, R1/C1 as smd, J1/J2 as exclude_from_pos_files (PCIe edge). Board 28.55 x 85.6mm.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
