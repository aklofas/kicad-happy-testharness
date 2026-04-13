# Findings: biomurph/Mouse / Hardware_KiCad_Mouse

## FND-00000936: I2C bus false positive: LEFT and D12 nets classified as SCL/SDA; Cross-domain signal false positive: ADNS_SCK flagged as needing level shifter; USB full-speed differential pair (D+/D-) not detected...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: Hardware_KiCad_Mouse_Mouse.sch.json
- **Created**: 2026-03-23

### Correct
- ATmega32U4 (U3), ADNS2610 optical sensor (U1), quadrature encoder (U2), crystals Y1/Y2, buttons SW1-SW4, USB connector J1, fuse F1, ferrite beads L1/L2, TVS diodes D2/D3, all correctly typed and counted. Multi-sheet parsing (main + MousePlayground sub-sheet) works correctly.
- Y2 (LFXTAL057485Cutt) correctly identified with C9/C10 (18pF each), effective load of 12.0pF calculated correctly using the series formula CL_eff = (18*18)/(18+18) + ~3pF stray. Y1 (24MHz THT crystal with capacitor footprint) correctly flagged without load caps.
- Q1 detected as BJT PNP, collector to GND, emitter drives LED D4 through R14 (1K current limiter). Base resistors R5 (1K) and R4 (100K) correctly identified. led_driver sub-structure correctly populated.

### Incorrect
- The analyzer detected I2C on nets LEFT and D12 because U3 (ATmega32U4) pins PD0 and PD1 have SCL/INT0 and SDA/INT1 in their KiCad pin names. However, these pins are wired to a mouse button (SW2) and a pin header (J5) as GPIO signals, not an I2C bus. No I2C devices exist on these nets. Detection based on pin name strings is over-triggering.
  (signal_analysis)
- The cross_domain_signals analysis flags ADNS_SCK (U3 PF4 to U1 ADNS2610) as needing a level shifter because the two ICs have different supply symbols (__unnamed_1/VCC for U3 vs __unnamed_22/VDD for U1). In reality, both are 5V supplies filtered through ferrite beads L1/L2 from the same +5V rail. The boards are the same logic voltage; no level shifter is needed or present.
  (signal_analysis)
- Net __unnamed_29 in the parsed output contains J1 pin 1 (VBUS), D3 pin 2 (TVS anode), and R3 pin 2 (D- series resistor). This is physically impossible - VBUS and the D- line cannot be the same net. J1 D- (pin 2) appears separately as __unnamed_37. This is a KiCad 5 legacy net wire-tracing bug where adjacent wires near the connector are incorrectly merged.
  (signal_analysis)

### Missed
- The differential_pairs section is empty. The design has a clear USB D+/D- pair: J1 (microUSB) -> 22-ohm series resistors R1/R3 -> U3 ATmega32U4 D+/D- pins. The pair is present and even has ESD TVS diodes D2/D3. Detection fails because the signal passes through three separately-named net segments (e.g., __unnamed_28 -> 'D+' net label -> __unnamed_10 for D+), preventing the pair matcher from tracing it end-to-end.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00000937: Single-component playground sub-sheet (PPH1 104-pin connector) parsed correctly

- **Status**: new
- **Analyzer**: schematic
- **Source**: Hardware_KiCad_Mouse_MousePlayground.sch.json
- **Created**: 2026-03-23

### Correct
- Correctly parsed as 1 component, 106 nets, 86 no-connects. The 104-pin PPH array generates many individual signal nets which is expected.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00000938: PCB structure accurately parsed: 2-layer, 50x90mm, 49 footprints, fully routed; Courtyard overlaps correctly detected (5 overlaps including Y1/U3 at 3.84mm2)

- **Status**: new
- **Analyzer**: pcb
- **Source**: Hardware_KiCad_Mouse_Mouse.kicad_pcb.json
- **Created**: 2026-03-23

### Correct
- 49 footprints (48 front, 1 back), 38 SMD + 10 THT + 1 NPTH mounting, 260 track segments, 44 vias, 4 zones, 137 nets, routing_complete=true all confirmed. Board outline with rounded corners (arcs) correctly detected. Annular ring DFM violation at 0.1mm correctly flagged as requiring advanced process.
- Five courtyard overlaps detected: Y1 vs U3 (3.84mm2 - significant, crystal placed very close to MCU), C3/C4, R11/R14, D4/R14, C8/L2. These are genuine placement issues in the design, not false positives.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00000939: Gerber set complete, aligned, 9 layers + 2 drill files correctly analyzed

- **Status**: new
- **Analyzer**: gerber
- **Source**: Hardware_KiCad_Mouse_plots.json
- **Created**: 2026-03-23

### Correct
- All required layers present (F.Cu, B.Cu, F/B.Mask, F/B.Paste, F/B.SilkS, Edge.Cuts). PTH drill (145 holes) and NPTH drill (6 mounting holes including 4x 4.8mm large NPTH for the mouse optical sensor window) correctly classified. B.Paste is empty (no back-side SMD paste), which is correct as only 1 back-side component exists and it is likely THT.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
