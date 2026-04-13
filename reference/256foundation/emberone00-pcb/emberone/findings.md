# Findings: 256foundation/emberone00-pcb / emberone

## FND-00002037: I2C pull-up reported as missing (has_pull_up=false) despite R19 and R20 (4.7k) on SDA/SCL

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: schematic_emberone00-pcb_data.kicad_sch.json.json
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
- design_analysis.bus_analysis.i2c reports has_pull_up=false and pull_ups=[] for both SDA and SCL. However ic_pin_analysis confirms R19 (4.7k) is connected to SDA (pin 2 of TMP1075 U6), and R20 (4.7k) is connected to SCL. The other end of these resistors connects to the '3V3' net, which is used as a regular net label (not a power symbol), so '3V3' does not appear in statistics.power_rails. The pull-up detection algorithm requires the pull resistor's supply end to be on a recognized power rail; because 3V3 is a label-net rather than a power symbol net, the pull-ups go undetected. This is a false negative that will incorrectly suggest missing I2C pull-up resistors.
  (design_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00002038: GND0..GND2 detected as a bus with width=88 — these are separate ground domains, not a parallel bus

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: schematic_emberone00-pcb_asics.kicad_sch.json.json
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
- bus_topology reports prefix='GND', width=88, range='GND0..GND2' in asics.kicad_sch. GND0, GND1, and GND2 are three independent ground domain nets for three ASIC instances. They are not a parallel digital bus. The width=88 is the sum of label occurrences for all GND-prefixed nets across the schematic (each of the 3 nets appears ~29 times on average — once per decoupling capacitor, test point, and power pin). This double error (false bus classification plus inflated width) would mislead any tool consuming bus_topology for interconnect analysis.
  (bus_topology)

### Missed
(none)

### Suggestions
(none)

---

## FND-00002039: Power sequencing correctly identifies 395-component hierarchical design with VDD regulator floating EN warning

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: schematic_emberone00-pcb_emberone.kicad_sch.json.json
- **Created**: 2026-03-24

### Correct
- power_sequencing detects U1's EN2 pin connected to an unnamed floating net and generates a floating_en_warnings entry. The main schematic correctly aggregates 395 components across hierarchical sheets (power, data, asics, and four asic-3up-* instances), with 338 nets and correct power rail identification of GND, VDD, VIN, VIN_M. The USB-C Type-C connector J6 passes cc1/cc2 pulldown, D+/D- series resistor, and VBUS decoupling checks, only failing VBUS ESD protection.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00002040: Gerber alignment flagged as failed due to normal copper setback from board edge

- **Status**: promoted
- **Analyzer**: gerber
- **Source**: gerber_emberone00-pcb_Manufacturing Files_gerbers.json.json
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
- alignment.aligned=false with issues 'Width varies by 7.5mm across copper/edge layers' and 'Height varies by 11.6mm across copper/edge layers'. The Edge.Cuts layer is 128x128mm as expected, while copper layers range from 119-128mm — a normal design margin of 3-5mm per side (copper pours and traces do not extend to the board edge). The PCB placement_analysis separately shows L2 with edge_clearance=-2.2mm (actually outside the board), which is a real issue, but the general gerber alignment flag is a false positive. The alignment check threshold should distinguish between expected copper setback and genuine layer registration errors.
  (alignment)

### Missed
(none)

### Suggestions
(none)

---

## FND-00002041: 6-layer board correctly identified with full stackup, 1010 vias, 36 zones across 128x128mm

- **Status**: promoted
- **Analyzer**: pcb
- **Source**: pcb_emberone00-pcb_emberone.kicad_pcb.json.json
- **Created**: 2026-03-24

### Correct
- The PCB analyzer correctly identifies the 6-copper-layer stackup (F.Cu, In1..In4.Cu, B.Cu), 395 footprints (140 front, 255 back), 3368 track segments, 1010 vias, 36 zones, and 128x128mm board size. DFM correctly flags annular ring at 0.1mm (advanced process tier) and board size exceeding JLCPCB's 100x100mm standard pricing tier. Routing is complete (365 nets, 0 unrouted). The GND zone spans 4 copper layers (F.Cu, In1, In3, In4) with 175 stitching vias — correctly identified as a thermal/ground plane.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
