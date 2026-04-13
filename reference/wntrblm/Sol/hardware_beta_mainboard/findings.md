# Findings: wntrblm/Sol / hardware_beta_mainboard

## FND-00001372: Net table inverts pin names for U1 power pins: GND net contains pin named VDD and vice versa; SPI bus incorrectly duplicated: two SPI bus entries found for a single AD5689R DAC, one with misidentif...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: hardware_breakouts_dac-breakout-ad5689_dac-breakout-ad5689.sch
- **Created**: 2026-03-24

### Correct
- The statistics show 8 total components matching exactly the BOM entries: U1 (AD5689R DAC), C1 (10uF), C2 (100nF), JP1-JP4 (four solder jumpers for GAIN and RESET config), and J1 (8-pin connector). Component types and quantities all verified against the component list.

### Incorrect
- In the legacy KiCad 5 .sch parser, the 'VDD' net entry has U1 pin 4 with pin_name 'GND', and the 'GND' net entry has U1 pin 5 with pin_name 'VDD'. For the AD5689R, pin 4 is GND and pin 5 is VDD, so the net label correctly matches but the stored pin_name within each net is swapped relative to the net name. This means the pin_name field is sourced from the symbol pin definitions rather than the net connection, and the association is inverted. This could indicate a legacy .sch pin-to-net resolution bug where the pin_name stored in the net structure is misassigned for mirrored components (mirror_x: true on U1).
  (nets)

### Missed
- The bus_analysis.spi array contains two entries for what is effectively one SPI interface on U1 (AD5689R). Bus 'pin_U1' maps MOSI to the 'OUTB' net (U1 pin 7, VOUTB — a DAC analog output, not an SPI data pin) and SCK to an unnamed net driving the SCLK and RESET jumpers. This is a false SPI detection: the analyzer confused the DAC's analog output net (OUTB) with an SPI MOSI line. Additionally, the 'SDO' net is labeled on VOUTB which further confuses the SPI detector.
  (design_analysis)

### Suggestions
(none)

---

## FND-00001373: OPA4197 quad op-amp (U8) and OPA388 single op-amp (U4) not detected by opamp_circuits detector; Component count correct at 58 components with accurate type breakdown including SAMD51J MCU, AD5686R ...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: hardware_rev1_mainboard_mainboard.sch
- **Created**: 2026-03-24

### Correct
- The reported 58 components match: 20 capacitors, 21 resistors, 8 ICs (LM1117 LDO, TPS79633 LDO, SAMD51J MCU, OPA388, GD25Q64 flash, AD5686R DAC, SN74AHCT125 level shifter, OPA4197), 3 connectors, 3 test points, 2 diodes, 1 crystal. The 5 power rails (+12V, +3V3, +5V, -12V, GND) are correctly identified. The TPS79633 and LM1117-5.0 regulators and the 32.768kHz crystal circuit are correctly detected.

### Incorrect
(none)

### Missed
- The mainboard schematic has two op-amp ICs: U4 (OPA388, single-channel precision op-amp in SOT-23-5) and U8 (OPA4197, quad precision op-amp in TSSOP-14). Both are powered from ±12V rails (U8 confirmed in ic_power_rails). The signal_analysis.opamp_circuits array is empty. This is a missed detection — the design has an analog output scaling section with four channels of op-amp buffering for DAC_OUT_A/B/C/D through resistor networks (R2/R3/R5/R7/R8/R9/R16-R19 precision 0.1% resistors), exactly the kind of op-amp circuit the detector should identify.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00001374: OPA4197 quad op-amp (U1) not detected in opamp_circuits despite being central to the CV scaler design

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: hardware_breakouts_precision-dac-cv-scaler_precision-dac-cv-scaler.sch
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
(none)

### Missed
- The precision-dac-cv-scaler breakout is built around U1 (OPA4197, quad op-amp) with 14 precision resistors (0.1% tolerance, values like 4.70k, 9.09k, 2.91k, 1k) forming a precision scaling/buffering network for DAC CV outputs. This is a textbook multi-channel inverting amplifier topology. signal_analysis.opamp_circuits is empty. The design also has U2 (TMUX1134, analog mux) and a placeholder U? (OPA197). The op-amp detector is missing active op-amp circuits here due to likely pin naming differences in the custom library symbol (pins show as unnamed outputs rather than standard OUT/IN+/IN- names).
  (signal_analysis)

### Suggestions
(none)

---

## FND-00001375: Board dimensions, layer count, footprint count, and routing status all accurate

- **Status**: new
- **Analyzer**: pcb
- **Source**: hardware_rev1_mainboard_mainboard.kicad_pcb
- **Created**: 2026-03-24

### Correct
- Statistics report 40.0×108.0mm board (a standard 8HP Eurorack module size), 2 copper layers, 59 footprints (57 front, 2 back), 511 track segments, 122 vias, 6 zones, 90 nets, routing complete. The DFM correctly flags the board as exceeding 100×100mm (standard tier). Thermal pad via check correctly identifies TPS79633 (U2 SOT-223-6) has 0 thermal vias on its exposed pad.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001376: Panel PCB correctly reports 0 copper layers used and 0 nets — appropriate for a mechanical/cosmetic front panel

- **Status**: new
- **Analyzer**: pcb
- **Source**: hardware_rev1_panel_panel.kicad_pcb
- **Created**: 2026-03-24

### Correct
- The rev1 panel is a pure mechanical Eurorack front panel with no electrical routing (0 tracks, 0 vias, 0 zones, 0 nets, 0 unrouted). The analyzer correctly reports copper_layers_used as 0 and routing_complete as true. Board dimensions 40.3×128.5mm match a standard 8HP Eurorack panel. The 6 footprints (5 front, 1 back) represent cosmetic markings and mounting hardware.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001377: Beta mainboard footprint split (40 SMD, 8 THT) correctly identified for a mixed-technology board

- **Status**: new
- **Analyzer**: pcb
- **Source**: mainboard.kicad_pcb
- **Created**: 2026-03-24

### Correct
- The beta mainboard (50mm wide vs 40mm in rev1) reports 58 footprints with 40 SMD and 8 THT, consistent with a design that uses through-hole connectors and test points alongside SMD components. The tht_count of 8 is plausible for the Eurorack power connector, audio jacks, and programming headers visible in the net list. Net count of 90 matches rev1 exactly, confirming same logical design with different PCB layout.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001378: Layer set complete (9 gerber files + 1 drill), drill hole counts and tool sizes plausible for the beta mainboard

- **Status**: new
- **Analyzer**: gerber
- **Source**: gerbers
- **Created**: 2026-03-24

### Correct
- All required and recommended layers present (F.Cu, B.Cu, F.Mask, B.Mask, F.Paste, B.Paste, F.SilkS, B.SilkS, Edge.Cuts). 124 total holes: 88 vias at 0.399mm diameter and 36 component/mounting holes across 5 size categories. The paste layer (F.Paste, 188 SMD apertures) is consistent with the 40 SMD footprints in the PCB JSON. Board dimensions 50×108mm in gerbers match the beta PCB.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001379: Alignment flagged as misaligned (17.6mm width variation) but this is a false alarm for a decorative panel with asymmetric copper

- **Status**: promoted
- **Analyzer**: gerber
- **Source**: hardware_rev1_panel_gerbers
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
- The gerber analyzer reports aligned=false with issue 'Width varies by 17.6mm across copper/edge layers'. The Edge.Cuts is 40.3mm wide while B.Cu is only 22.7mm wide. For a Eurorack front panel, the back copper layer typically only has pads for mounting hardware on one side (not spanning the full board width), making this width variation legitimate and expected — not an actual misalignment. The analyzer's heuristic incorrectly treats asymmetric feature placement as a coordinate misalignment.
  (alignment)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001380: Jackboard gerbers correctly identified as THT-dominant (0 SMD apertures, 56 component holes for audio jacks)

- **Status**: new
- **Analyzer**: gerber
- **Source**: hardware_rev1_jackboard_gerbers
- **Created**: 2026-03-24

### Correct
- The jackboard has smd_ratio=0.0 and 56 component holes, consistent with the schematic showing 11 audio jack connectors (likely PJ301M or similar THT 3.5mm jacks), 1 USB-B connector, 1 LED, and 1 switch — all THT. The 18 vias at 0.399mm are reasonable for a 2-layer board with ~13 components. Missing F.Paste layer is correctly noted as 'missing_recommended' (not 'missing_required') since THT boards don't need paste.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
