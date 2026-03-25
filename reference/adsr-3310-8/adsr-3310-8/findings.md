# Findings: adsr-3310-8 / adsr-3310-8

## FND-00001977: Multi-sheet parsing: both adsr-3310-8.sch (top) and adsr.sch (sub-sheet) parsed correctly; Eurorack dual-supply rails correctly identified: +12V and -12V; RC filters detected: 680Ω/100nF low-pass a...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: adsr-3310-8.sch.json
- **Created**: 2026-03-24

### Correct
- Analyzer reports sheets_parsed:2 with both sheet files listed. The 43 total components include components from both the top-level sheet (TL074 op-amp sections, connectors, pots) and the sub-sheet (AS3310 ADSR IC with timing caps). This is correct.
- Analyzer reports power_rails: ['+12V', '-12V', 'GND']. This correctly reflects the Eurorack standard ±12V power supply. U1 (TL074) uses both rails as V+ and V-, while U2 (AS3310) uses +12V and a filtered -12V via R20/C10.
- The analyzer correctly detects R20(680Ω)/C10(100nF) as a 2.34kHz low-pass filter on the -12V rail (power supply filtering for AS3310 VEE), and R19(10kΩ)/C6(10nF) as a 1.59kHz high-pass. Both are real signal conditioning filters in this ADSR design.
- signal_analysis.decoupling_analysis correctly identifies +12V with 3 caps (100nF+100uF+100nF, total 100.2uF) and -12V with 2 caps (100nF+100uF, total 100.1uF). Both rails have bulk and bypass capacitors, matching the IDC Eurorack power header layout.
- Analyzer reports ic:2, resistor:21 (includes RV1/RV2/RV3 trim pots counted as resistors and RV8 TIME pot), capacitor:10, connector:6 (J1-J6), test_point:4 (TP1-TP4 for A/D/S/R). Counts are accurate.

### Incorrect
- The analyzer detects three voltage dividers (3k9/1k pairs) producing ratio ~0.204 on ATTACK, DECAY, RELEASE nets. These are resistor dividers that scale CV modulation inputs for the TL074 op-amp summing inputs driving the AS3310. While structurally they are dividers, functionally they are input attenuators for mixing. The detection is technically correct but context is useful.
  (signal_analysis)
- In design_analysis.power_domains, U2 (AS3310) shows power_rails: ['+12V', '__unnamed_23']. The '__unnamed_23' net is actually the filtered -12V supply (R20/C10 low-pass filter output). The analyzer names it as an anonymous net instead of associating it with the -12V rail. The power rail should trace back to -12V.
  (design_analysis)

### Missed
- U1 (TL074) has 4 op-amp sections used as summing/inverting amplifiers for ATTACK, DECAY, SUSTAIN, RELEASE control. signal_analysis.opamp_circuits is empty []. The TL074 has explicit +/- input and output pins (pins 3/2/1, 5/6/7, 10/9/8, 12/13/14 visible in nets). These should be detected as op-amp circuits.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00001978: PCB has 151 footprints — correct for 8× replicated single-channel design; 2-layer board correctly detected with 2 copper layers (F.Cu, B.Cu); routing_complete:true with 0 unrouted nets — matches fu...

- **Status**: new
- **Analyzer**: pcb
- **Source**: adsr-3310-8.kicad_pcb.json
- **Created**: 2026-03-24

### Correct
- The schematic represents 1 ADSR channel (43 components including 1 TL074+1 AS3310). The PCB has 151 footprints (front:151, back:0), confirming an 8-channel replication of the core circuit (8×AS3310 + supporting components + shared connectors). Net names TRIGGER1-8, GATE1-8, CV1-8 confirm the 8-channel topology.
- Analyzer reports copper_layers_used:2 with copper_layer_names: ['F.Cu', 'B.Cu']. This is appropriate for the Eurorack module PCB with mostly THT components and no complex signal routing requirements.
- All 110 nets fully routed across 771 track segments and 58 vias. The board is a completed design ready for manufacture.
- Eurorack 3U panel height is 128.5mm usable; this PCB at 98.5×132.5mm fits within a standard rack panel. The 98.5mm width is slightly under standard panel widths, consistent with a multi-HP Eurorack module.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001979: Layer set complete: 9 gerber layers + 2 drill files for 2-layer board; Correct identification of all-THT board: smd_ratio:0.0, smd_apertures:0; 485 total holes detected, consistent with 151 THT com...

- **Status**: promoted
- **Analyzer**: gerber
- **Source**: plots.json
- **Created**: 2026-03-24

### Correct
- Analyzer reports completeness.complete:true with all 9 expected layers found and no missing layers. gerber_files:9, drill_files:2. This is correct for a KiCad 5 2-layer board.
- pad_summary shows smd_apertures:0 and smd_ratio:0.0. This is correct — all 151 components in the ADSR PCB are THT (resistors, caps, ICs in DIP package, connectors). No SMD components are present.
- statistics.total_holes:485 = 394 component_holes + 54 vias + 37 mounting holes. For 151 THT footprints with varying pin counts (ICs, connectors, caps, resistors) plus 54 vias, this count is reasonable and internally consistent.

### Incorrect
- B.Paste width:0/height:0 and B.SilkS width:0/height:0. For an all-THT board, no back paste is expected. The zero B.SilkS extent is unusual but possible if no back-side silkscreen was generated for this KiCad 5 design. This is a design choice and the analyzer correctly reports what it finds.
  (alignment)

### Missed
(none)

### Suggestions
(none)

---
