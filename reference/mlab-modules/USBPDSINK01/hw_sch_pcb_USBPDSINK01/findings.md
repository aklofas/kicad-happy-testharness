# Findings: USBPDSINK01 / hw_sch_pcb_USBPDSINK01

## FND-00001757: Component count of 53 correct with accurate type breakdown; LDO regulator U2 correctly detected with input VBUS and output +3V3; I2C bus correctly detected on SDA and SCL nets with pull-up resistor...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: USBPDSINK01.kicad_sch.json
- **Created**: 2026-03-24

### Correct
- 53 total components correctly detected: 2 ICs (STUSB4500QTR PD controller + NCV4274CST33T3G LDO), 7 connectors, 21 resistors, 5 LEDs, 7 capacitors, 3 jumpers, 3 fiducials, 4 mounting holes, 1 transistor. All match the source schematic.
- NCV4274CST33T3G (mapped via Regulator_Linear:LM2936-3.3 lib) correctly classified as LDO topology with input_rail=VBUS, output_rail=+3V3, estimated_vout=3.3V using fixed_suffix method. This is accurate — the NCV4274CST33T3G is a fixed 3.3V LDO powered from VBUS.
- I2C bus correctly identified: SDA net with R13 (4k7 pull-up to VCC) and SCL net with R14 (4k7 pull-up to VCC), both connecting to STUSB4500QTR (U1). The bus_analysis.i2c has two entries and design_observations includes i2c_bus observations for both lines.
- The usb_compliance check correctly flags cc1_pulldown_5k1=fail and cc2_pulldown_5k1=fail. CC1 and CC2 connect directly from J1 (USB-C connector) to U1 (STUSB4500QTR pins CC1/CC1DB and CC2/CC2DB) with no external pull-down resistors. The STUSB4500 integrates internal CC termination, so external 5.1k pull-downs are absent by design. The compliance check correctly flags this as a fail per standard external resistor check.
- R11 (100R) and C4 (100nF) form an RC network with cutoff_hz=15915 (~16kHz). The connections: R11 between unnamed nets, C4 between unnamed net and VDC rail. The detection and cutoff frequency calculation are arithmetically correct (1/(2π×100×100n) = 15.9kHz).

### Incorrect
- Q2 uses symbol MLAB_T:IRF7469PbF with ki_keywords 'transistor PMOS P-MOS P-MOSFET simulation' and ki_description 'P-MOSFET transistor, drain/source/gate, 40V, 9A, 12mOhm'. The actual value IRF9317TRPBF is also a P-channel MOSFET. The transistor_circuits analyzer reports is_pchannel=False, which is wrong. This likely means the analyzer is not reading the ki_keywords or ki_description fields to determine channel type, and the lib_id 'MLAB_T:IRF7469PbF' does not match the N-channel name pattern heuristics.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001758: PCB footprint count, via count, and routing completeness correct; Component placement correctly identifies 12 front-side and 41 back-side components

- **Status**: new
- **Analyzer**: pcb
- **Source**: USBPDSINK01.kicad_pcb.json
- **Created**: 2026-03-24

### Correct
- 53 footprints, 2-layer board (F.Cu + B.Cu), 322 track segments, 48 vias, routing_complete=true, 0 unrouted nets. Board dimensions 45.49 x 52.95 mm. Consistent with the schematic component count.
- Front (F.Cu): 12 connectors and jumpers (J2-J7, JP1, JP3, M1-M4). Back (B.Cu): 41 components including the two ICs (U1 STUSB4500, U2 LDO), all SMD passives, LEDs, and USB-C connector J1. The smd_count=40 and tht_count=12 match the layer assignments (back SMD - JP2 excluded_from_pos, front THT headers).

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
