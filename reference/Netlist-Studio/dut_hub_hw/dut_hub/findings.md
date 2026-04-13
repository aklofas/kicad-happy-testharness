# Findings: Netlist-Studio/dut_hub_hw / dut_hub

## FND-00002027: Top-level hierarchical schematic: 158 total components across 8 parsed sheet instances (5 unique sheet files; dut.kicad_sch instantiated 4 times for DUT1–DUT4); Four crystal oscillator circuits det...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: 
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
- Top-level hierarchical schematic: 158 total components across 8 parsed sheet instances (5 unique sheet files; dut.kicad_sch instantiated 4 times for DUT1–DUT4)
  (statistics)
- Four crystal oscillator circuits detected (Y1–Y4), one per DUT slot, each with two 27pF load caps giving 16.5pF effective load
  (signal_analysis)
- PAC1954x-x4MX four-channel power monitor (U1 in power sheet) not detected as current_sense despite four R_Shunt resistors (R11–R14) on DUT power rails
  (signal_analysis)
- Net classifier correctly labels per-DUT JTAG/SWD signals (TCK{slash}SWCLK=clock, TMS{slash}SWDIO=debug, TDI/TDO=debug) and bus protocols (SPI_SCK0=clock, I2C_SDA2=data)
  (design_analysis)
- Four BSS138 N-channel MOSFETs (Q1–Q4) correctly detected as open-drain reset drivers, one per DUT slot, each gate driven by TXU0102QDCURQ1 level translator
  (signal_analysis)
- 100x155mm 4-layer board (F.Cu, In1.Cu, In2.Cu, B.Cu), fully routed (0 unrouted nets), all 158 footprints on front side, 523 vias
  (statistics)
- Six edge clearance warnings: mounting holes H2 and H4 at 0.16mm from board edge (below typical 0.2mm minimum), connectors J11/J14/J8/J5 at 0.34–0.66mm
  (placement_analysis)
- PCB net count (282) substantially exceeds schematic net count (187) due to hierarchical sheet expansion — expected for 4-DUT replicated hierarchy
  (statistics)
- KiCad 5 legacy .sch keyboard PCB: 175 components — 77 switches (75 MX-NoLED + RE0 + SW1), 69 diodes (1N4148W), 8 capacitors, 6 mounting holes, 6 resistors, 3 inductors, 2 ICs, 2 connectors, 1 crystal, 1 fuse
  (statistics)
- Three decorative graphic symbols misidentified as power rails: 'Logo_Open_Hardware_Small', 'OSHW-Text-Logo', 'mini-eLiXiVy-Logo' appear in statistics.power_rails
  (statistics)
- Key matrix reports switches_on_matrix=130 and estimated_keys=130, but actual matrix is 5 rows x 15 cols = 75 keys; BOM confirms 75 MX-NoLED switch instances
  (signal_analysis)
- WE-TVS-82400102 (U2) correctly detected as ESD IC protecting USB_D+, USB_D-, MCU_D+, MCU_D-; fuse F1 (500mA) on VCC correctly detected as fuse protection
  (signal_analysis)
- 302x93mm 2-layer keyboard PCB, 175 footprints (155 front / 20 back), 77 THT positions matching 77 switch-type components, standard DFM
  (statistics)
- Gerber set complete for 2-layer board: 7 files (F.Cu, B.Cu, F/B.Mask, F/B.SilkS, Edge.Cuts) plus PTH and NPTH drill files; only missing recommended F.Paste
  (completeness)
- rev.1.1 identical layer structure to rev.1; 2 fewer vias (27 vs 29); same flashes and board dimensions
  (statistics)
- NRF52840-based IoT board: 78 total components — 28 capacitors, 15 resistors, 6 ICs, 5 switches, 4 WS2812 LEDs, 4 mounting holes, 2 transistors, 2 ferrite beads, 2 diodes, plus misclassified: 5 LEDs reported as inductors and 1 tactile switch reported as relay
  (statistics)
- 32MHz crystal X2 (Q22FA12800025, EPSON FA-128) classified as 'connector' type, causing crystal_circuits to be empty — NRF52840 USB clock crystal entirely missed
  (signal_analysis)
- Five 0603 white LEDs (LD1–LD5, value '0603White light_C2290') classified as 'inductor'; tactile switch KEY1 (TS-1003S-07026) classified as 'relay'
  (statistics)
- NRF52840 2.4GHz RF matching network (L1=4.7nH, L2=2.2nH, C1=1.0pF, C2=1.2pF) detected as generic lc_filters at 2.1–3.1GHz but not as rf_matching
  (signal_analysis)
- LDO XC6206P332MR correctly detected (VBUSnRF->+3V3), WS2812 4-LED chain correctly detected (240mA estimated), PRTR5V0U2X USB ESD correctly detected
  (signal_analysis)
- Q2 (2N7002) used as open-drain level converter with gate tied to +3V3; analyzer incorrectly lists XC6206 LDO (U4) and SHT40 sensor (U5) as gate_driver_ics
  (signal_analysis)
- 64.95x54.0mm 2-layer board, 85 footprints (84 front / 1 back), DFM tier 'challenging': 0.1mm tracks and 0.075mm annular ring below advanced process minimum
  (dfm)
- Two DFM violations: 0.1mm track width requires advanced process (standard min 0.127mm); 0.075mm annular ring is below even advanced process minimum (0.1mm)
  (dfm)

### Missed
(none)

### Suggestions
- Fix: 32MHz crystal X2 (Q22FA12800025, EPSON FA-128) classified as 'connector' type, causing crystal_circuits to be empty — NRF52840 USB clock crystal entirely missed
- Fix: Five 0603 white LEDs (LD1–LD5, value '0603White light_C2290') classified as 'inductor'; tactile switch KEY1 (TS-1003S-07026) classified as 'relay'

---
