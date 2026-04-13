# Findings: sparkfun/SparkFun_Serial_MP3_Player_Shield-MY1690X / Hardware_Production_SparkFun_Serial_MP3_Player_Shield_MY1690X_panelized

## FND-00001485: Component counts are accurate: 45 total, correct type breakdown; Power rails correctly identified: 3.3V, 3.3V_P, 5V, GND, VCC, VUSB; Protection devices correctly identified: D5 ESD IC and F1 resett...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: Hardware_SparkFun_Serial_MP3_Player_Shield_MY1690X.kicad_sch
- **Created**: 2026-03-24

### Correct
- The analyzer reports 45 total_components matching the 45 unique refs in the components list. The breakdown — 7 resistors, 7 capacitors, 1 IC (MY1690X), 1 transistor (BSS138), 3 diodes, 2 LEDs, 7 jumpers, 6 connectors, 1 fuse, 1 inductor, 1 switch, 4 fiducials, 4 other — all match the source schematic. G1 (OSHW_Logo, in_bom=False) is correctly included in total_components but excluded from the BOM (44 BOM qty vs 45 total_components).
- All six power rails in the schematic are accurately reported. 3.3V_P is the MY1690X internal regulator output, VCC is the 5V input to the IC (via ferrite bead L1), VUSB comes from the USB-C connector through fuse F1, and 5V/3.3V come from the Arduino shield connector. The rail hierarchy is correctly captured.
- D5 (DT1042-04SO) is correctly classified as an esd_ic protecting the USB D+/D- lines, and F1 (6V/0.5A/1A) is correctly classified as a fuse on the VUSB rail. D5 protected_nets correctly includes both D+ and D-.
- Three UART-related nets are detected: MY_TX (U2 TX output), MY_RX (Arduino-side 5V UART RX input), and MY_RX_LV (3.3V-shifted RX going into U2 pin 12 RX). This correctly captures the UART channel between U2 and the Arduino host. The level-shifted signal path (MY_RX -> Q1 level shifter -> MY_RX_LV) is captured as separate nets as designed.
- Three decoupling caps on the 3.3V_P rail (C8 1.0uF, C2 10uF, C3 0.1uF, total 11.1uF) are correctly identified. The design observation correctly flags that U2's VCC rail has no bypass capacitor (the MY1690X VCC pin is powered via ferrite bead L1 with caps only on the 3.3V_P regulator output, not on VCC input). The decoupling_coverage observation correctly reports has_high_freq=false (no sub-100nF cap on 3.3V_P).
- The signal_analysis correctly reports empty lists for voltage_dividers, rc_filters, lc_filters, crystal_circuits, and power_regulators. The MY1690X has an internal regulator (3.3V_P output), and the U2 subcircuit correctly identifies its power rails. None of the external resistor networks form a classical voltage divider — R2/R3 are USB-C CC pull-down resistors, not dividers.

### Incorrect
- The signal_analysis.design_observations entry for net D- sets has_esd_protection=false. However D5 (DT1042-04SO) is a 4-line ESD IC whose pin 3 (I/O2) connects to D-, which is correctly listed in protection_devices[D5].protected_nets=[D+, D-]. The protection_devices section is correct but the design_observation contradicts it. Both D+ and D- are protected by D5.
  (signal_analysis)
- design_analysis.differential_pairs[0].esd_protection=[U2] but U2 is the MY1690X MP3 decoder IC, not an ESD protection device. D5 (DT1042-04SO) is the actual ESD protection IC for the D+/D- pair and should appear in esd_protection. U2 appears here because it shares the D+/D- nets via its DP/DM pins, but it is not ESD protection. D5 is correctly identified as esd_ic in protection_devices but this relationship is not propagated to differential_pairs.
  (design_analysis)
- Q1 (BSS138 N-MOSFET) is a UART level shifter. Its gate (pin 1) is tied directly to the 3.3V_P power rail with no intervening resistor. R1 (2.2k) connects 3.3V_P to MY_RX_LV (the source/pin 2), making R1 a source pull-up resistor, not a gate resistor. The analyzer reports gate_resistors=[{R1, 2.2k}] because R1 is on the 3.3V_P net (same as gate_net), confusing source pull-up for gate resistor. Similarly, gate_driver_ics=[U2] is wrong: U2's MY_RX_LV pin is on the source net, not the gate. The gate is passively biased by 3.3V_P power. The topology=level_shifter identification is correct.
  (signal_analysis)

### Missed
- The board has a Qwiic connector (J3) with SDA and SCL pins connecting to the Arduino shield (B1 A4/SDA and A5/SCL). The nets are named SDA and SCL. However design_analysis.bus_analysis.i2c is empty []. The I2C detector likely requires an IC component with explicitly named SDA/SCL pins rather than connectors. The Qwiic I2C bus should be identified.
  (design_analysis)

### Suggestions
(none)

---

## FND-00001486: PCB basic statistics are accurate: 2-layer board, 35 real electrical components; Routing completeness correctly reported as true with 78 nets fully routed; GND copper zone with via stitching correc...

- **Status**: promoted
- **Analyzer**: pcb
- **Source**: Hardware_SparkFun_Serial_MP3_Player_Shield_MY1690X.kicad_pcb
- **Created**: 2026-03-24

### Correct
- The board is correctly reported as 2-layer (F.Cu and B.Cu), 53.34mm x 59.69mm, fully routed (unrouted_net_count=0), 252 track segments, 45 vias, 1 GND copper zone. The 105 total footprints include 62 decorative board_only kibuzzard items, 7 jumpers with allow_soldermask_bridges, 1 exclude_from_bom, 31 SMD, and 4 through_hole electrical components.
- The PCB output correctly shows routing_complete=true and unrouted_net_count=0. The 78 nets match the schematic net count. The net_count=78 in the PCB matches the schematic's total_nets=78.
- The thermal_analysis correctly identifies a GND zone on F&B.Cu (both layers) covering 3183.9 mm², with 18 stitching vias at 0.3mm drill. The copper_presence warning about unfilled zones is appropriate as is_filled=false in the zone data — the zone outline is present but fill polygons were not generated before saving.
- The decoupling_placement correctly shows U2 (MY1690X) with four nearby caps: C8 (1.0uF, 5.08mm), C7 (2.2uF, 6.35mm), C1 (2.2uF, 6.35mm), C4 (47uF, 8.78mm), all on the same front side. The closest cap at 5.08mm is reasonable for decoupling. All caps share relevant nets (3.3V_P, GND).
- The DFM analysis reports standard tier with min_track_width=0.1524mm (6mil), approx_min_spacing=0.1796mm, min_drill=0.3mm, and zero violations. These values are consistent with the track data showing 0.1524mm as minimum width and 0.3mm via drill. The board uses lead-free HASL finish at 1.6mm thickness, consistent with fab notes on F.Fab layer.

### Incorrect
- The schematic shows R5 as '330' (330 ohm, from SparkFun-Resistor:330_0603) while the PCB file has R5 as '1k'. The PCB output correctly reports R5 value as '1k' per the PCB source file, and the schematic output correctly reports '330' per the schematic source. This is a genuine divergence between the schematic and PCB — the PCB was updated to 1k but the schematic was not updated, or vice versa. The analyzer correctly reflects each file's actual content.
  (footprints)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001487: Panelized board statistics correctly reported: 6x panel with 631 footprints and 40 unrouted nets; Panelized PCB unrouted nets are intentionally unconnected Arduino pins, not real routing errors

- **Status**: promoted
- **Analyzer**: pcb
- **Source**: SparkFun_Serial_MP3_Player_Shield_MY1690X_panelized.kicad_pcb
- **Created**: 2026-03-24

### Correct
- The panelized board (6 copies on a 120.88mm x 203.93mm panel) correctly shows 631 footprints (6 × ~105), 1512 track segments, 270 vias, and 6 zones. The routing_complete=false with 40 unrouted nets is accurate: all 40 unrouted nets are 'unconnected-' prefixed nets representing intentionally unconnected Arduino shield pins (B1), which have multiple pads per panel instance but no routes between them.

### Incorrect
(none)

### Missed
- The 40 unrouted nets in the panelized board all have names matching 'unconnected-(B1-...' pattern, corresponding to Arduino Uno shield pins intentionally left unconnected in the schematic (marked as no_connect). The analyzer reports routing_complete=false which is technically accurate per the ratsnest data, but there is no annotation that these 40 'unrouted' nets are deliberate no-connects rather than missing routes. A note distinguishing intentional no-connects from real routing omissions would improve analysis utility.
  (connectivity)

### Suggestions
(none)

---

## FND-00001488: layer_count reported as 2 but gerbers contain 4 copper layers (GL2 and GL3 are inner layers); gerber_files count is 9 but 11 gerber files are present in the directory; Edge.Cuts correctly flagged a...

- **Status**: promoted
- **Analyzer**: gerber
- **Source**: Hardware_Production
- **Created**: 2026-03-24

### Correct
- The board outline (Edge.Cuts) is truly absent from the Production gerber set. The .GKO file uses the traditional board outline extension but its content has FileFunction attribute 'Soldermask,Bot' — it is actually a duplicate Bottom Soldermask file with a misnamed extension, not a board outline. The analyzer correctly reports missing_required=[Edge.Cuts] and complete=false. The board_dimensions being empty ({}) is also correct since no outline data was parseable.
- The Production directory contains no drill files (.drl, .xln, etc.), confirmed by drill_files=0, total_holes=0, has_pth_drill=false, has_npth_drill=false. While the panelized board has 270 vias in the KiCad PCB (detected as via_apertures=540 in the gerbers), separate drill/Excellon files were not exported. The pad_summary via_apertures=540 is reasonable for a 6-up panel with ~45 vias each. The absence of drill files is a real incompleteness in this gerber set.
- The alignment analysis reports aligned=true with no issues across B.Cu, B.SilkS, B.Paste, B.Mask, F.Cu, F.SilkS, F.Paste, F.Mask. Layer extents are consistent across the panel: copper layers at 111.277 x 186.152mm, masks at 120.88 x 220.136mm (wider due to panel frame coverage). The slight extent differences between layers are normal for a panelized design with breakaway rails.
- The pad_summary reports smd_apertures=738 (x2_aperture_function method), via_apertures=540, smd_ratio=1.0. For a 6-up panel with ~31 SMD components of various pad counts per board, 738 SMD aperture flashes is plausible. Via apertures=540 aligns with roughly 45 vias × 6 panel copies × 2 (front+back copper pads) = 540.

### Incorrect
- The Production directory contains .GL2 and .GL3 files with FileFunction attributes 'Copper,L2,Inr' and 'Copper,L3,Inr' respectively, confirming a 4-layer panelized board. However, the analyzer reports layer_count=2 and found_layers lists only F.Cu and B.Cu (plus non-copper layers). The .GL2 and .GL3 extensions are not recognized by the analyzer's layer detection logic, so two inner copper layers are silently omitted. Note: the underlying PCB KiCad file itself is also defined as 2-layer (copper_layers_used=2), so the panelization process added inner layers to the gerbers that aren't reflected in the KiCad PCB definition.
  (layer_count)
- The analyzer reports gerber_files=9 but the Production directory contains 11 gerber files: GTL, GBL, GTO, GBO, GTP, GBP, GTS, GBS, GKO, GL2, GL3. The .GL2 and .GL3 files (inner copper layers) are not being counted or processed. This undercount is a consequence of the same extension recognition gap that causes the layer_count=2 error.
  (statistics)

### Missed
(none)

### Suggestions
(none)

---
