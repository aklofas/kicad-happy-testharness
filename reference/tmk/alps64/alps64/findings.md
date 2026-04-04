# Findings: alps64 / alps64

## FND-00001959: 86 KEYSW keyboard switches misclassified as 'relay' instead of 'switch'; Key matrix shows switches_on_matrix=0 despite 86 KEYSW components in the matrix; 8x8 key matrix correctly detected with 64 d...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: alps64.sch.json
- **Created**: 2026-03-24

### Correct
- The analyzer correctly identifies the keyboard matrix as 8 rows and 8 columns (row0-7, col0-7) using the net_name detection method. It correctly finds 64 diodes (D00-D77) on the matrix. The estimated_keys=64 matches the keyboard's actual key count. The crystal (X1) and its 10pF load capacitors (C3, C4) are also correctly detected.
- X1 (XTAL_GND, a 16MHz crystal for ATMega32U2) is detected with its two 10pF load capacitors C3 and C4. The effective load capacitance is computed as 8pF (series combination plus stray). This is a standard USB HID keyboard crystal circuit and is correctly identified.
- The analyzer correctly identifies USB D+ and D- nets with R2 and R1 (22-ohm series resistors for USB signal integrity) connected to J1 (USB-C receptacle). The observation correctly notes no ESD protection, which matches the schematic — there are no TVS diodes or dedicated ESD protection ICs on the USB lines.
- The decoupling analysis correctly finds three capacitors on the +5V rail: C1 (4.7uF bulk), C5 and C6 (0.1uF bypass). Total capacitance is 4.9uF. C2 (1uF) appears to be on a different net. This is correct decoupling for an ATMega32U2 USB keyboard controller.

### Incorrect
- The alps64 matrix.sch contains 86 KEYSW components (keyboard switches with refs K00-K77 plus split-key variants like K30_1, K40_1, etc.). The analyzer assigns them component_type='relay' rather than 'switch'. The schematic stats confirm: relay=86, switch=1 (where the 1 switch is SW100, a separate reset/boot button). KEYSW is a keyboard switch symbol from the keyboard_parts library and should be typed as 'switch'. This misclassification causes switches_on_matrix=0 in the key matrix analysis.
  (statistics)
- The key matrix detector correctly identifies an 8x8 matrix via row/col net names, and correctly finds 64 diodes. However switches_on_matrix=0 because KEYSW components are typed as 'relay' instead of 'switch', so the matrix scanner does not count them. The actual number of key switch positions is 64 standard plus additional split-key variants (86 total KEYSW refs). The estimated_keys=64 from the 8x8 grid is correct for the logical key count.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001960: PCB correctly identified as fully routed with 196 footprints, 2 copper layers, 57 vias; Board size DFM violation correctly flagged (285x95.7mm exceeds 100x100mm JLCPCB tier)

- **Status**: new
- **Analyzer**: pcb
- **Source**: alps64.kicad_pcb.json
- **Created**: 2026-03-24

### Correct
- The alps64 is a reversible PCB design where each key position has footprints on both F.Cu and B.Cu sides (hence 196 footprints for ~64 key positions plus diodes and controller components). track_segments=1205, via_count=57, routing_complete=True, net_count=99 all match expectations for a complete keyboard PCB. Board dimensions 285x95.7mm are correct for a 65% keyboard form factor.
- The keyboard PCB at 285x95.7mm exceeds the 100x100mm standard tier threshold for low-cost PCB fabs. The analyzer correctly flags this as a board_size DFM violation. This is expected for a full-size keyboard PCB.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
