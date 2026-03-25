# Findings: blinkekatze / blinkekatze

## FND-00002283: Gerber alignment flagged as misaligned due to sparse B.Cu extent vs board outline

- **Status**: promoted
- **Analyzer**: gerber
- **Source**: gerber_blinkekatze_fab_Rev2.0_gerbers.json.json
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
- The analyzer reports aligned=False with 'Width varies by 23.1mm' and 'Height varies by 19.5mm' across copper/edge layers. However, on a 83x83mm board the B.Cu layer spans 59.9x63.5mm — components on the back copper layer simply do not cover the full board area, which is completely normal. The Edge.Cuts extent (83x83mm) represents the board boundary, and any copper layer that doesn't fill the board edge-to-edge will trigger this false alarm. The F.Cu layer at 75.3x75.3mm is only 3.85mm from the edge on each side, which is a normal keepout margin. This same false positive also fires on the Rev1.0 gerbers.
  (alignment)

### Missed
(none)

### Suggestions
(none)

---

## FND-00002284: No bus protocol or regulator detections despite ESP32-C3, BQ24295, TPS63001, BQ27546, LIS3DH, SPL06-001

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: schematic_blinkekatze_blinkekatze.kicad_sch.json.json
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
(none)

### Missed
- The top-level blinkekatze schematic aggregates 122 components including an ESP32-C3-MINI-1 (U1, likely I2C/SPI/UART buses), BQ24295 USB charger IC, TPS63001 buck-boost regulator, BQ27546 battery fuel gauge (I2C), LIS3DH 3-axis accelerometer (I2C/SPI), SPL06-001 barometric sensor (I2C/SPI), and LTR-303ALS-01 ambient light sensor (I2C). Despite this rich set of bus-connected and power-regulation ICs, detectors is empty — no voltage_regulators, i2c_buses, spi_buses, or similar detectors fired. This is a KiCad 6+ hierarchical schematic; sheets_parsed=None and sheet_files=None suggest the sub-sheet traversal failed, but the components themselves were parsed from the flat extraction.
  (detectors)

### Suggestions
(none)

---

## FND-00002285: TPS63001 buck-boost regulator not detected in power sub-sheet

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: schematic_blinkekatze_power.kicad_sch.json.json
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
(none)

### Missed
- The power sub-sheet contains a TPS63001 buck-boost converter (U9) with a 2.2uH inductor (L4), four 10uF capacitors, and a 100nF capacitor — a complete switching regulator circuit. The detectors section is empty. This is consistent with the missed TL2575HV-ADJ detection in the bldc repo: the schematic analyzer's switching regulator detector does not match TPS63001 or TL2575HV-ADJ part numbers, suggesting the detector relies on a whitelist that is missing common Texas Instruments regulator families.
  (detectors)

### Suggestions
(none)

---

## FND-00002286: 4-layer board correctly analyzed with comprehensive power net routing for all supply rails

- **Status**: new
- **Analyzer**: pcb
- **Source**: pcb_blinkekatze_blinkekatze.kicad_pcb.json.json
- **Created**: 2026-03-24

### Correct
- The analyzer correctly identifies the 4-layer stackup (F.Cu, In1.Cu, In2.Cu, B.Cu), 134 footprints, 853 track segments, and 226 vias. power_net_routing correctly includes +3V3, +BATT, VBUS, GND, GND1, /Charger/VSYS, /Charger/PWR_ON, and /USB/VBAT — all the supply nets. The DFM tier is correctly classified as 'challenging' due to 0.075mm annular rings below the 0.1mm advanced fab threshold. Decoupling placement analysis correctly identifies nearby caps for the LIS3DH accelerometer.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
