# Findings: Bastardkb/Scylla-PCB-thumb-cluster / flex

## FND-00001403: Component counts accurate; Mousebite breakoff tabs correctly classified as 'other'; LED chain detection generates 3 chains with D3 appearing in two chains and D2 as an isolated stub

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: flex.kicad_sch
- **Created**: 2026-03-24

### Correct
- 31 total components: 10 SK6812MINI LEDs, 2 capacitors, 5 diodes (standard 1N4148-style for 5-key matrix), 5 switches, 3 connectors, 2 resistors, 4 Mousebite tabs (breakoff PCB connection points). The 4 Mousebite components correctly appear as type='other' rather than a functional component type. PCB has 33 footprints = 31 schematic + 2 G*** logo footprints, confirmed board_only. Key matrix detection: 1 row × 5 cols = 5 switches with 5 diodes is correct for the thumb cluster.

### Incorrect
- The thumb cluster has 10 SK6812MINI LEDs using the same branching topology as the main plate. The analyzer reports: chain0 (D3,D4,D8,D10,D12), chain1 (D3,D6,D7,D11,D13), chain2 (D2 alone). D3 appears in both chains 0 and 1 (shared start LED). All 10 unique LEDs are covered across the 3 chains (union = {D2,D3,D4,D6,D7,D8,D10,D11,D12,D13}), but reporting 3 separate chains overstates the chain count and incorrectly suggests D2 (chain2, length=1, 60mA) is a standalone chain rather than the chain entry point. The same branching topology issue as the main plate manifests here at smaller scale.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001404: PCB dimensions, DFM standard tier, and courtyard overlap detection are accurate

- **Status**: new
- **Analyzer**: pcb
- **Source**: flex.kicad_pcb
- **Created**: 2026-03-24

### Correct
- Board 74.065x41.455mm is a plausible size for a 5-key thumb cluster plate. DFM tier 'standard' with zero violations is correct: min track 0.16mm and min spacing 0.1687mm are both within standard JLCPCB limits (0.1mm minimum). The 0.15mm annular ring is at the standard threshold (0.125mm limit) and passes. Three courtyard overlaps are flagged between J1/J3 and J2/R2 — these are valid DRC-style warnings for tight connector/component placement on a small PCB. Routing complete with zero unrouted nets.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
