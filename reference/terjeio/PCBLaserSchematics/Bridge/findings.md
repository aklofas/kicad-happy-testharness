# Findings: terjeio/PCBLaserSchematics / Bridge

## FND-00001063: Component extraction, net topology, and label parsing all correct; 12V and 3V3 rails classified as 'signal' instead of 'power'

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: Bridge.sch
- **Created**: 2026-03-23

### Correct
- 2 connectors (P1 CONN_02X08, P2 CONN_01X12) with 9 nets (GND, 12V, 3V3, SDA, SCL, LASER, ZSTEP, ZDIR, ZHOME) correctly extracted. Net membership matches label assignments.

### Incorrect
- In Bridge.sch, '12V' and '3V3' are power rail net labels but net_classification assigns them 'signal'. These are clearly power distribution nets (multiple pins, PWR flag symbol on GND). The classifier only promotes nets to 'power' when backed by power symbols; label-only power rails are misclassified.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001064: 30 components, 87 nets, correct IC identification (MSP430, FT232RL, A4988×2); I2C bus on SDA/SCL (MSP430) detected; missing pull-up flagged correctly; UART detection on TxD net is a false positive ...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: Controller_Controller.sch
- **Created**: 2026-03-23

### Correct
- Component counts, types, power rails (+12V, +3V3, +5V, GND), and BOM extraction are all accurate. Power rail net classification (power/ground) is correct for Controller.
- MSP430G2553 P1.4/P1.5 connect to SDA/SCL nets. The bus analysis correctly identifies U2 as the device and correctly notes no pull-up resistors on either line.
- R6 and C5 form a filter from the multi-resistor junction (__unnamed_59) to GND. Cutoff frequency calculation is correct.

### Incorrect
- The UART bus entry lists U1 (FT232RL) on the TxD net via pin CBUS4, which is a configurable I/O pin, not the standard TXD line. The analyzer is matching net-name 'TxD' heuristically without verifying the pin function. MSP430 P3.6 is also not a dedicated UART TX in this schematic's multi-function pin context. The detection should require the pin name to include 'TX' or the component to be a known UART device on a known TX pin.
  (signal_analysis)

### Missed
- The +3V3 rail is sourced from the FT232RL's built-in 3.3V output (USBDP pin tied to +3V3 in the netlist), which serves MSP430, A4988s, and connectors. The power_regulators array is empty; an integrated regulator detection is missing.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00001065: 25 components correctly identified including Q1 (2N7002 NMOSFET) and Q2 (BC547 BJT); False I2C bus detections: GND net and __unnamed_1 flagged as SDA/SCL buses; single_pin_nets observation misident...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: Driver_Driver.sch
- **Created**: 2026-03-23

### Correct
- Transistor types, gate/base/drain/collector/emitter net assignments are accurate. Q2 load_type=resistive is correct. Gate resistor R4 on Q1 is detected.

### Incorrect
- Four I2C bus entries are reported but only one is real. The GND net is flagged as SCL because MCP4725 pin 5 (SCL) is mis-wired to GND in the schematic — the analyzer correctly follows netlist connectivity but should not classify GND as an I2C bus line. Net __unnamed_1 is flagged as SDA because MCP4725 pin 4 (SDA) connects there via a resistor, not to the named SDA net. This is a schematic wiring anomaly but the I2C bus classification itself is misleading.
  (signal_analysis)
- The observation reports U1 pins VOUT (net 'SDA') and VSS (net 'SCL') as single-pin nets. This is because the 'SDA' and 'SCL' named nets connect only to VOUT and VSS respectively (due to the schematic's wiring anomaly), not to the actual I2C pins of MCP4725. The root cause is the schematic's net naming — but the observation is factually misleading.
  (signal_analysis)
- RV1 (value '5K', lib_id 'POT', footprint 'Potentiometer_Bourns_3296Y') is classified as type 'resistor' in both the BOM and component list. The lib_id 'POT' and the RV reference designator prefix clearly indicate a potentiometer and should map to a distinct type.
  (signal_analysis)

### Missed
- Q2 (BC547) emitter is on net __unnamed_25, which contains only C7 pin 1 and Q2 emitter. C7 appears to be a bypass cap — if the other side of C7 is GND, then the emitter is effectively AC-grounded. However the analyzer cannot determine this without checking the other pin of C7. Worth noting as a potential improvement area.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00001066: Single-layer (B.Cu only) PCB with 4 footprints, 9 nets, 71 segments correctly reported

- **Status**: new
- **Analyzer**: pcb
- **Source**: Bridge.kicad_pcb
- **Created**: 2026-03-23

### Correct
- copper_layers_used=1, copper_layer_names=['B.Cu'], track layer_distribution confirms all routing on B.Cu. Footprints on both F.Cu (P1) and B.Cu (P2) are correctly identified. Routing complete with 0 unrouted nets.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001067: Single-layer PCB correctly identified: 34 footprints, 398 track segments, all on B.Cu

- **Status**: new
- **Analyzer**: pcb
- **Source**: Controller_Controller.kicad_pcb
- **Created**: 2026-03-23

### Correct
- Statistics (60×57.5mm board, 13 SMD, 21 THT, 0 vias, routing complete) are plausible. DFM tier 'standard' with min trace 0.25mm is correct.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001068: Driver PCB: 27 footprints, 228 segments on B.Cu, 55×40mm board correctly reported

- **Status**: new
- **Analyzer**: pcb
- **Source**: Driver_Driver.kicad_pcb
- **Created**: 2026-03-23

### Correct
- Single-layer routing with 18 SMD and 9 THT footprints. Statistics are internally consistent.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001069: No gerber files present in repository — gerber analysis not run

- **Status**: promoted
- **Analyzer**: gerber
- **Source**: _home_aklofas_Projects_kicad-happy-testharness_repos_PCBLaserSchematics
- **Created**: 2026-03-23

### Correct
(none)

### Incorrect
(none)

### Missed
- The repo contains only .sch and .kicad_pcb files with no exported gerber/drill files. No gerber output directory exists. This is expected for a design-only repo without manufacturing outputs.
  (signal_analysis)

### Suggestions
(none)

---
