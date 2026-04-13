# Findings: SukkoPera/LittleSixteen / LittleSixteen

## FND-00000822: 45 false no_driver ERC warnings from KiCad 5 legacy pin-type misclassification; L7812 topology reported as 'LDO' — it is a fixed linear regulator; Hierarchical multi-sheet parse correctly consolida...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: LittleSixteen.sch.json
- **Created**: 2026-03-23

### Correct
- The top-level LittleSixteen.sch correctly traverses all 14 sub-sheets (cpu, ted, ram, rom, keyboard, datasette, exp_port, misc, pla, joysticks, avout, userport, sid). Component counts (368 total, 35 ICs, 88 caps, 65 resistors, 58 ferrite beads) and 3 crystal circuits are plausible for a Commodore Plus/4 clone. UART detection on rxd_ttl/txd_ttl nets is reasonable.

### Incorrect
- Nets like ~CAS, ~RAS, k0-k7 are flagged as 'no_driver' because the MOS 8360/7501 CPU/TED chips in the KiCad 5 library define their output/bidirectional pins as 'input'. These are global labels driven by the CPU/TED across sheets. 45 of 48 ERC warnings appear to be false positives from legacy library pin type data.
  (signal_analysis)
- The power_regulators detector classifies U7 (L7812, 12V fixed linear regulator) with topology='LDO'. The L7812 is a standard 3-terminal linear regulator, not a low-dropout regulator. This is a misclassification — LDO implies a different architecture (low dropout voltage, often adjustable). Should be 'linear' or 'fixed_linear'.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00000823: Key matrix not detected despite 8 diodes and keyboard controller (MOS 6529) in keyboard.sch

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: keyboard.sch.json
- **Created**: 2026-03-23

### Correct
(none)

### Incorrect
(none)

### Missed
- keyboard.sch contains 8 diodes (keyboard matrix protection), 2 ICs, and a connector in a pattern consistent with a Commodore Plus/4 keyboard matrix. The analyzer returns key_matrices=[] both for the sub-sheet and the full hierarchical parse. This is a missed detection for a clear keyboard matrix circuit.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00000824: PCB analysis correctly captures a large 2-layer THT-dominant retro board

- **Status**: new
- **Analyzer**: pcb
- **Source**: LittleSixteen.kicad_pcb.json
- **Created**: 2026-03-23

### Correct
- Board stats (389x136mm, 366 footprints, 320 THT/12 SMD, 2-layer, 375 nets, fully routed) are accurate for a Commodore Plus/4 clone mainboard. DFM tier='advanced' due to 0.1mm annular ring is plausible. Power net routing and current capacity analysis for +9V and VCC rails look correct. File version 20171130 (KiCad 5) correctly identified.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
