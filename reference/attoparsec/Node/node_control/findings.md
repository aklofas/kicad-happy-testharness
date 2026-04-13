# Findings: attoparsec/Node / node_control

## FND-00000990: FTDI1 misclassified as 'fuse' instead of 'connector'; POT1-4 (Device:R_POT_US) classified as 'connector' instead of 'resistor' or 'potentiometer'; RC filter false positive: R16+C3 are not a filter ...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: node.sch.json
- **Created**: 2026-03-23

### Correct
- 66 total components, 58 nets, crystal Y1 with correct 22pF load caps (effective 14pF), ATmega328P and L7805 both identified as ICs. BOM grouping is accurate. Schottky diodes (Bat85) and their clamp circuit topology correctly parsed.

### Incorrect
- FTDI1 has lib_id='Attoparsec:FTDI_header' and footprint='PinHeader_1x06'. Its value string 'FTDI' is apparently triggering a fuse keyword match. Correct type is 'connector'. This also inflates fuse_count to 1 and undercounts connectors.
  (signal_analysis)
- POT1-4 use lib_id='Device:R_POT_US' (standard KiCad potentiometer symbol) with footprint 'Attoparsec:P090S_pot'. They are classified as 'connector' which is wrong. The component_types count shows connector:24 but should be connector:20 with potentiometer/resistor:4.
  (signal_analysis)
- The analyzer detects R16(1K) and C3(100nF) as an RC filter on the RESET net. In reality: R16 is a pull-up from +5V to RESET; C3 is the Arduino auto-reset capacitor connecting FTDI DTR to RESET. C3 pin2 (the 'ground' end in the RC detection) is actually the FTDI DTR line (__unnamed_1 net = FTDI pin 6), not a ground. These components share the RESET net but form two separate functions, not one RC filter.
  (signal_analysis)
- -12V is listed in statistics.power_rails (correctly identified as a power rail symbol) but design_analysis.net_classification maps it to 'signal'. Negative supply rails should map to 'power'. +12V and +5V are correctly classified as 'power'.
  (signal_analysis)
- The L7805 is a well-known fixed 5V linear regulator. The analyzer outputs topology=unknown with no input/output rails. The PCB confirms U2 pins connect to +12V (input) and +5V (output). Likely caused by empty pins[] array for U2 in the legacy .sch parser — 29 of 66 components have empty pins, including both ICs (U1, U2). This prevents rail inference.
  (signal_analysis)

### Missed
- The design has nets MISO_DPIN_12, SCK_DPIN_13, and MOSI_PWM_DPIN_11 — clear SPI signal names on an ATmega328P. bus_analysis.spi is empty. The UART is detected (TX_DPIN_1, RX_DPIN_0) so naming-based detection works for UART but missed SPI. The SPI nets only connect to resistors (not to a clearly identified SPI slave IC), which may explain the miss, but the SPI signals should at least be flagged.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00000991: Decoupling placement falsely reports C3 as decoupling cap for ATmega328P (U1); Board statistics, routing, courtyard overlaps, and DFM analysis are accurate; Edge clearance warnings for J2, FTDI, J4...

- **Status**: promoted
- **Analyzer**: pcb
- **Source**: node_main.kicad_pcb.json
- **Created**: 2026-03-23

### Correct
- 47 footprints (45F/2B), 683 track segments, 38 vias, routing complete (0 unrouted), 2-layer board, 20x110mm (correct for slim Eurorack module). DFM correctly flags >100mm board size. Six courtyard overlaps detected — these appear plausible for a very narrow 20mm-wide PCB. Power net routing (+12V, +5V, GND at 0.4mm width) correctly reported.
- Three connectors (J2 at -12.12mm, FTDI at -10.85mm, J4 at -8.3mm) extend significantly outside the board edge. On a 20mm-wide Eurorack module these are panel-side connectors that presumably extend past the PCB toward a front panel — an intentional design choice, but the analyzer correctly flags it as unusual.

### Incorrect
- C3 (100nF) is reported as a decoupling cap for U1 (ATmega328P) at 4.58mm distance with shared_nets=['RESET']. A RESET net is not a power decoupling net — C3 is the auto-reset capacitor connected to FTDI DTR. The ATmega has no true VCC/GND decoupling cap in this design, but the analyzer misidentifies C3. A proper decoupling cap should share VCC+GND nets.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00000992: No gerber output produced — Node repo has no gerber files

- **Status**: promoted
- **Analyzer**: gerber
- **Source**: .json
- **Created**: 2026-03-23

### Correct
(none)

### Incorrect
(none)

### Missed
- The requested gerber output file does not exist. The Node repo contains only .kicad_pcb files and no exported gerber/drill files. The analyzer correctly produced no output (no files to analyze), but this means gerber completeness and fabrication readiness cannot be assessed for this design.
  (signal_analysis)

### Suggestions
(none)

---
