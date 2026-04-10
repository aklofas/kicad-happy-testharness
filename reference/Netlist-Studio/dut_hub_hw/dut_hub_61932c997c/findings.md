# Findings: Netlist-Studio/dut_hub_hw / dut_hub_dut_hub

## FND-00002561: Top-level hierarchical schematic contains 158 total components across 8 parsed sheet instances (5 unique sheet files, dut.kicad_sch instantiated 4 times for DUT1-DUT4)

- **Status**: ?
- **Analyzer**: schematic
- **Source**: ?

### Correct
(none)

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00002562: Four crystal oscillator circuits detected (Y1, Y2, Y3, Y4), one per DUT slot, all with 27pF load caps giving 16.5pF effective load

- **Status**: ?
- **Analyzer**: schematic
- **Source**: ?

### Correct
(none)

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00002563: PAC1954x-x4MX four-channel power monitor (U1 in power sheet) not detected as current_sense despite having four R_Shunt resistors (R11-R14) on DUT power rails

- **Status**: ?
- **Analyzer**: schematic
- **Source**: ?

### Correct
(none)

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00002564: Bus signals include JTAG/SWD per-DUT signals (DUT1_TCK/SWCLK, DUT2_TMS/SWDIO, etc.) and analog measurement nets (AN0-AN19, P200-P915) correctly classified as clock/debug/signal

- **Status**: ?
- **Analyzer**: schematic
- **Source**: ?

### Correct
(none)

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00002565: Four BSS138 N-channel MOSFETs (Q1-Q4) correctly detected as open-drain reset drivers, one per DUT slot, all driven by TXU0102 level translators

- **Status**: ?
- **Analyzer**: schematic
- **Source**: ?

### Correct
(none)

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00002566: 100x155mm 4-layer board, fully routed (0 unrouted nets), all 158 components on front side only, 523 vias

- **Status**: ?
- **Analyzer**: schematic
- **Source**: ?

### Correct
(none)

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00002567: Six edge clearance warnings: two mounting holes (H2, H4) at 0.16mm from board edge, connectors J11/J14/J8/J5 between 0.34-0.66mm from edge

- **Status**: ?
- **Analyzer**: schematic
- **Source**: ?

### Correct
(none)

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00002568: PCB net count (282) substantially exceeds flattened schematic net count (187) due to hierarchical sheet expansion — expected for 4-DUT replicated hierarchy

- **Status**: ?
- **Analyzer**: schematic
- **Source**: ?

### Correct
(none)

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00002569: KiCad 5 legacy .sch keyboard PCB: 175 components — 77 key switches (MX-NoLED), 69 diodes (1N4148W), 8 capacitors, 6 mounting holes, 6 resistors, 3 inductors, 2 ICs, 2 connectors, 1 crystal, 1 fuse

- **Status**: ?
- **Analyzer**: schematic
- **Source**: ?

### Correct
(none)

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00002570: Three decorative graphic symbols misidentified as power rails: 'Logo_Open_Hardware_Small', 'OSHW-Text-Logo', 'mini-eLiXiVy-Logo' appear in statistics.power_rails

- **Status**: ?
- **Analyzer**: schematic
- **Source**: ?

### Correct
(none)

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00002571: Key matrix detection reports switches_on_matrix=130 and estimated_keys=130, but the actual matrix is 5 rows x 15 cols = 75 switches; there are only 75 MX-NoLED components in the BOM

- **Status**: ?
- **Analyzer**: schematic
- **Source**: ?

### Correct
(none)

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00002572: WE-TVS-82400102 (U2) correctly detected as ESD IC protecting USB_D+, USB_D-, MCU_D+, MCU_D- — full USB signal chain protected

- **Status**: ?
- **Analyzer**: schematic
- **Source**: ?

### Correct
(none)

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00002573: 302x93mm 2-layer keyboard PCB, 175 footprints (155 front / 20 back), 77 THT switch positions, standard DFM except board size exceeding 100x100mm

- **Status**: ?
- **Analyzer**: schematic
- **Source**: ?

### Correct
(none)

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00002574: Gerber set complete for 2-layer board: 7 gerber files (F.Cu, B.Cu, F.Mask, B.Mask, F.SilkS, B.SilkS, Edge.Cuts) plus PTH and NPTH drill files. Only missing recommended F.Paste.

- **Status**: ?
- **Analyzer**: schematic
- **Source**: ?

### Correct
(none)

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00002575: rev.1.1 gerber set identical layer structure to rev.1 with 2 fewer vias (27 vs 29) and identical flashes/draws counts

- **Status**: ?
- **Analyzer**: schematic
- **Source**: ?

### Correct
(none)

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00002576: NRF52840-based IoT board: 78 total components — 28 capacitors, 15 resistors, 7 inductors (2 real + 5 LED misclassifications), 6 ICs, 5 switches, 4 LEDs (WS2812), 4 mounting holes (HDR type), 2 transistors, 2 ferrite beads, 2 diodes, 1 relay (tactile switch), 1 fuse

- **Status**: ?
- **Analyzer**: schematic
- **Source**: ?

### Correct
(none)

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00002577: 32MHz crystal X2 (Q22FA12800025, EPSON FA-128) classified as 'connector' type instead of 'crystal', causing it to be absent from crystal_circuits detection

- **Status**: ?
- **Analyzer**: schematic
- **Source**: ?

### Correct
(none)

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00002578: Five 0603 white LEDs (LD1-LD5, value '0603White light_C2290') misclassified as 'inductor' type; one tactile switch KEY1 (TS-1003S-07026) misclassified as 'relay'

- **Status**: ?
- **Analyzer**: schematic
- **Source**: ?

### Correct
(none)

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00002579: NRF52840 RF matching network (L1=4.7nH, L2=2.2nH, C1=1.0pF, C2=1.2pF) detected as lc_filters at 2.1-3.1GHz but not as rf_matching or rf_chains

- **Status**: ?
- **Analyzer**: schematic
- **Source**: ?

### Correct
(none)

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00002580: LDO XC6206P332MR correctly detected (VBUS->VBUSnRF->+3V3 path), WS2812 4-LED addressable chain detected, PRTR5V0U2X USB ESD protection detected

- **Status**: ?
- **Analyzer**: schematic
- **Source**: ?

### Correct
(none)

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00002581: Q2 transistor circuit incorrectly lists U4 (XC6206 LDO), U5 (SHT40 sensor) as gate_driver_ics because its gate is tied to +3V3 power rail

- **Status**: ?
- **Analyzer**: schematic
- **Source**: ?

### Correct
(none)

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00002582: 64.95x54.0mm 2-layer board, 85 footprints (84 front/1 back), DFM tier 'challenging' due to 0.1mm tracks and 0.075mm annular ring below advanced process minimum

- **Status**: ?
- **Analyzer**: schematic
- **Source**: ?

### Correct
(none)

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00002583: DFM violations: 0.1mm track width requires advanced process (standard min 0.127mm) and 0.075mm annular ring is below advanced process minimum (0.1mm)

- **Status**: ?
- **Analyzer**: schematic
- **Source**: ?

### Correct
(none)

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
