# Findings: PROGLOG01 / hw_sch_pcb_PROGLOG01

## FND-00002005: Component count of 66 and type breakdown are accurate; TPS22919DCK (U1) misclassified as LDO regulator — it is a load switch; SPI bus cross-domain level-shifter warning is a false positive; SPI bus...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: repos_PROGLOG01_hw_sch_pcb_PROGLOG01.kicad_sch
- **Created**: 2026-03-24

### Correct
- Source has exactly 66 unique placed references (C1-C10, D1-D3, J1-J34, M1-M4, R1-R10, SW1, U1-U4, X1). Analyzer reports 66 with correct breakdown: 10 caps, 33 connectors, 1 diode, 4 ICs, 10 resistors, 2 LEDs, 1 switch, 1 oscillator, 4 other (mounting holes).
- U4 (ICE40UP5K-SG48I) function=FPGA (Xilinx). U2 (MIC5504-1.2YM5) detected as LDO with input_rail=+3V3, output_rail=+1V2, estimated_vout=1.2V (correct, from fixed suffix). U3 (AT25SF081-SSH) detected as SPI flash in memory_interfaces with processor=U4 and 4 shared SPI nets.
- R4 (100R) series with C5 (10uF) and C6 (100nF) in parallel to GND. Total capacitance 10.1uF, cutoff 157.6 Hz. Input net +1V2, output to unnamed decoupling node. Topology matches source schematic.

### Incorrect
- The TPS22919DCK is a 5V/3A single-channel load switch (MOSFET pass element with no voltage regulation). IN=+3V3, OUT=VCCIO_1 — output is simply switched +3V3. Analyzer classifies it topology=LDO. This cascades into a false positive in cross_domain_signals: the analyzer treats VCCIO_1 as a distinct regulated voltage domain rather than recognizing it equals +3V3.
  (signal_analysis)
- cross_domain_signals flags SPI_SI, SPI_SCK, SPI_SS, SPI_SO as crossing +1V2/+3V3 domains with needs_level_shifter=true. This is wrong: U4 (ICE40UP5K) uses VCCIO_1 (= +3V3 via load switch U1) as its SPI I/O bank voltage, not +1V2 (FPGA core). U3 (AT25SF081 SPI flash) also runs at +3V3. Both SPI endpoints are at 3.3V. Root cause is the TPS22919DCK misclassification as LDO.
  (design_analysis)

### Missed
- Net names SPI_SCK, SPI_SI, SPI_SO, SPI_SS unambiguously identify an SPI bus. U4 pins 14-17 and U3 pins 1,2,5,6 all connect to these nets. memory_interfaces correctly identifies 4 shared signal nets between U3 and U4, but bus_analysis.spi remains empty. The SPI bus should appear there.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00002006: PCB footprint count (66) matches schematic component count exactly

- **Status**: new
- **Analyzer**: pcb
- **Source**: repos_PROGLOG01_hw_sch_pcb_PROGLOG01.kicad_pcb
- **Created**: 2026-03-24

### Correct
- 66 footprints matches 66 schematic components, confirming no PCB-only extras and no missing placements. 2-layer, 60.45x40.13mm, fully routed (475 segments, 58 vias). DFM tier=standard, no violations.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00002007: Gerber layer set complete for 2-layer board; empty F.Paste is correct

- **Status**: new
- **Analyzer**: gerber
- **Source**: repos_PROGLOG01_hw_cam_profi_gbr
- **Created**: 2026-03-24

### Correct
- All 9 expected layers present. F.Paste has 0 flashes confirmed correct: PCB footprint analysis shows zero front-side SMD footprints (all 27 SMD parts are on B.Cu). B.Paste has 133 flashes. Board dimensions 60.6x40.28mm from gbrjob closely match PCB output (60.45x40.13mm).

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
