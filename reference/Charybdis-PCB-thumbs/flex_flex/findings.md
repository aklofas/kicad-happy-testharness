# Findings: Charybdis-PCB-thumbs / flex_flex

## FND-00000423: Key matrix not detected despite 3 switches, 3 diodes, and named row/column nets; Addressable LED chain detector reports overlapping/duplicate chains instead of recognizing a parallel branching tree...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: flex_flex.kicad_sch.json
- **Created**: 2026-03-23

### Correct
(none)

### Incorrect
- The 6 SK6812MINI LEDs form a branching parallel topology, not two independent linear chains of 3. Net '__unnamed_0' drives DIN of both D12 and D13 simultaneously; '__unnamed_1' receives DOUT from both D12 and D13 and drives DIN of D10 and D11; '__unnamed_2' receives DOUT from both D10 and D11 and drives DIN of D3 and D2. The analyzer instead reports three addressable_led_chains: [D12,D10,D3], [D12,D11,D2], and [D13] — these overlapping chains with shared start node (D12 appears in two chains) misrepresent the actual topology. The multi_driver_nets section correctly flags '__unnamed_1' and '__unnamed_2' as having multiple drivers, but the chain detector ignores this and produces spurious chains.
  (signal_analysis)
- Vcc and Gnd are used as global labels with 'input' shape throughout this sub-sheet flex PCB. This is a standard practice for hierarchical/flat schematics where power is supplied from a parent sheet via global labels. Flagging them as 'undriven_input_label' is a false positive — the design intentionally uses global labels for power distribution with no PWR_FLAG, which is normal for sub-sheets of a multi-board keyboard design.
  (label_shape_warnings)
- Same issue as Vcc: Gnd is a global label with 'input' shape used for power distribution on this sub-sheet. It is connected to VSS pins of all 6 SK6812MINI LEDs and both decoupling capacitors. Treating it as an undriven signal is incorrect.
  (label_shape_warnings)

### Missed
- The schematic contains a classic keyboard key matrix: 3 switches (SW5, SW9, SW19) each paired with a diode (D5, D9, D19) and wired to a shared row net ('row1') and individual column nets ('col2', 'col4', 'col6'). The signal_analysis.key_matrices array is empty even though all structural hallmarks of a diode-multiplexed key matrix are present.
  (signal_analysis)

### Suggestions
- Fix: Addressable LED chain detector reports overlapping/duplicate chains instead of recognizing a parallel branching tree

---
