# Findings: MFOS-NoiseToaster / PCB_Noise Toaster PCB

## FND-00000849: B+ and B- misidentified as differential signal pair; B+ and B- not detected as power rails despite being the only supply nets in sub-sheets

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: PCB_vco.kicad_sch.json
- **Created**: 2026-03-23

### Correct
(none)

### Incorrect
- In this analog synthesizer design, B+ and B- are the bipolar power supply rails (+9V and -9V), not a differential signal pair. The differential pair detector fires because both net names contain +/- suffixes and they share components (decoupling resistors/caps to those rails). The ps.kicad_sch confirms B+ and B- are supply outputs from a battery connector. This false positive affects vco.kicad_sch, vclpf.kicad_sch, and the top-level schematic.
  (signal_analysis)

### Missed
- In all sub-schematics (vco, vclpf, lfo, etc.), B+ and B- carry the analog supply rails but are classified only as 'signal' in net_classification. There are no power symbols for them (they use hierarchical labels instead), so power_rails in statistics is empty for these sheets. The analyzer correctly picks up GND via the power:GND symbol but misses the positive and negative supply nets entirely, leaving IC power rail analysis incomplete for the LM324 and other ICs.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00000850: Bleed resistors R37/R42 misidentified as RC high-pass filters

- **Status**: new
- **Analyzer**: schematic
- **Source**: PCB_ps.kicad_sch.json
- **Created**: 2026-03-23

### Correct
(none)

### Incorrect
- The power supply sheet has R37 and R42 (4.7k bleeder resistors) paired with C23 (470uF bulk cap). The analyzer classifies these as 'high-pass' RC filters with 0.07 Hz cutoff. In reality these are bleed resistors for safely discharging the supply caps — an RC power filter topology, not a signal high-pass filter. The 'high-pass' classification is misleading and the component is a power conditioning circuit.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00000851: B+ and B- copper fill zones not included in power_net_routing; Board dimensions, DFM tier, and component counts are accurate

- **Status**: promoted
- **Analyzer**: pcb
- **Source**: PCB_Noise Toaster PCB.kicad_pcb.json
- **Created**: 2026-03-23

### Correct
- 137 footprints (133 THT, 0 SMD), 2 copper layers, 132x69mm board, correct DFM violation flagged for exceeding 100x100mm JLCPCB threshold. Routing reported complete with 507 track segments. All values match expectations for a through-hole analog synthesizer board.

### Incorrect
(none)

### Missed
- The PCB uses B+ (F.Cu zone) and B- (B.Cu zone) as full-board copper pours — the entire front copper layer is the B+ supply and the entire back copper layer is B-. These are correctly identified in zones[], but power_net_routing only reports GND. B+ and B- are clearly major power distribution nets (B-: 129mm, B+: 42mm of routed segments plus the fill zones) and should appear in power net routing analysis.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00000852: Layer completeness and drill classification are accurate

- **Status**: new
- **Analyzer**: gerber
- **Source**: PCB_Gerber Files.json
- **Created**: 2026-03-23

### Correct
- All 9 expected layers found (F.Cu, B.Cu, F/B Mask, F/B Paste, F/B SilkS, Edge.Cuts), PTH and NPTH drill files present, 296 total holes, 11 gerber files. Complete=true is correct. The back silkscreen and back paste are intentionally empty (all THT, no back silkscreen markings) — not flagged as anomalies, which is correct behavior.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
