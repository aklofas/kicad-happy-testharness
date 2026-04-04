# Findings: Laser_Backplane_DVI / KiCad_LaserBackplane_DVI

## FND-00000859: -12V and -5V nets classified as 'signal' instead of 'power'; Decoupling analysis misses C8/C11 on +12V and C10/C12 on +5V rails; DVI-I connector J2 detected as hdmi_dvi interface; Both LDO regulato...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: KiCad_LaserBackplane_DVI.kicad_sch.json
- **Created**: 2026-03-23

### Correct
- hdmi_dvi_interfaces correctly identifies J2 (value: DVI-I) as an HDMI/DVI connector. Type reported as 'hdmi_connector' which is acceptable for a DVI-I part.
- U2 LT1761-5 input=+12V output=+5V and U3 LT1964-5 input=-12V output=-5V both correctly identified as LDO topology.
- Unit 1 correctly identified as buffer (gain=1). Unit 2 correctly identified as comparator_or_open_loop with feedback capacitor C4 (1.5pF). Unit 3 is the power unit with no signal pins, correctly marked 'unknown'.

### Incorrect
- net_classification shows '-12V': 'signal' and '-5V': 'signal'. These are named negative supply rails that should be classified as 'power'. The analyzer does not recognize negative-voltage power net names.
  (signal_analysis)
- decoupling_analysis only lists C7 for +12V and C9/C13 for +5V. C8, C11 (10n, 0603) and C10, C12 (4.7u, 0805) are on the same rails per BOM but are absent from decoupling_analysis — likely because they connect via unnamed nets rather than directly to the named rail power symbol.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00000860: K1 relay edge_clearance_mm of -16.54 is likely a false positive; Multiple ground domains correctly identified from unconnected DVI GNDA pins

- **Status**: promoted
- **Analyzer**: pcb
- **Source**: KiCad_LaserBackplane_DVI.kicad_pcb.json
- **Created**: 2026-03-23

### Correct
- 3 ground domains: GND (19 components), and 2 unconnected GNDA pads from J2 DVI connector. These appear as intentional no-connect GNDA pins on the DVI-I connector, correctly surfaced as separate ground-like nets.

### Incorrect
- K1 (relay) shows edge_clearance_mm = -16.54, flagging it as extending 16.54mm outside the board edge. Relays and panel connectors are commonly designed to overhang PCB edges intentionally. The warning may be valid but the large negative value warrants verification against the actual footprint/placement.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---
