# Findings: hackrf / hardware_hackrf-one_hackrf-one

## FND-00000293: hackrf-one PCB: copper_layers_used includes F.SilkS (non-copper layer), SMD count may be slightly inflated, no RF/impedance analysis for this RF-heavy board

- **Status**: new
- **Analyzer**: pcb
- **Source**: hardware_hackrf-one_hackrf-one.kicad_pcb.json
- **Related**: KH-154
- **Created**: 2026-03-17

### Correct
- Footprint count (321) matches visual inspection of the hackrf-one board
- Track segment count (4403) and via count (1173) consistent with dense 4-layer RF design
- Board dimensions 120.9mm x 74.8mm match known hackrf-one form factor
- DFM tier correctly identified for this production board
- Power net routing analysis captures major power rails

### Incorrect
- copper_layers_used=5 includes F.SilkS which is not a copper layer. hackrf-one is a 4-layer board (F.Cu, In1.Cu, In2.Cu, B.Cu)
  (statistics.copper_layers_used)

### Missed
- No RF impedance analysis despite this being an SDR (Software Defined Radio) board with critical 50-ohm RF traces
  (rf_analysis)
- No differential pair analysis despite USB and RF differential signaling
  (differential_pairs)

### Suggestions
- Filter copper_layers_used to only include layers matching *.Cu pattern
- Add RF impedance analysis for boards with SMA/RF connectors
- Add differential pair detection for USB and high-speed signals

---
