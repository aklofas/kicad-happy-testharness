# Findings: sparkfun/SparkFun_XRP_Controller / Hardware_Production_SparkFun_XRP_Controller

## FND-00001892: Component inventory and statistics are accurate; Crystal circuit (Y1 12MHz) correctly detected with load capacitors; WS2812B addressable LED chain (D4) correctly detected; USB-C compliance checks p...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: Hardware_SparkFun_XRP_Controller.kicad_sch.json
- **Created**: 2026-03-24

### Correct
- total_components=184 correctly counts unique physical parts (the components list has 188 entries because Q1/Q3/Q5/Q7 are dual-unit BCM857BS BJTs appearing as 2 units each; 188-4=184). Component types are all classified correctly: 49 resistors, 45 capacitors, 9 transistors, 9 ICs, 14 jumpers, 19 connectors, etc. Power rails (1.1V, 3.3V, 5V, GND, VBATT, VIN, VRAW, VSYS, VUSB) are all correctly identified.
- Crystal Y1 (12MHz) detected with C17=15pF and C18=15pF as load caps. Effective load capacitance computed as 10.5pF (7.5pF series + 3pF stray), which is within the typical RP2350 crystal specification range. The 'in_typical_range': True flag is correct.
- D4 (WS2812B) detected as a single-element addressable LED chain on GPIO37/NEOPIXEL, protocol 'single-wire (WS2812)', estimated 60mA current. Data input net correctly identified.
- J2 (USB_C_Receptacle) checks: CC1 5.1k pull-down (R29) pass, CC2 5.1k pull-down (R28) pass, DP/DM series resistors (R4/R5 27ohm each) pass, USB ESD IC (D5 DT1042-04SO) pass, VBUS ESD protection pass. One expected fail: VBUS decoupling (no bulk cap directly on VUSB rail at connector). All 6 passes and 1 fail are correct.
- U5 (RT9080-3.3, lib SparkFun-Regulator:RT9080-3.3) detected as LDO, input_rail=VSYS, output_rail=3.3V, estimated_vout=3.3, vref_source=fixed_suffix. All fields are accurate per the RT9080 datasheet (600mA LDO, 3.3V fixed output).
- protection_devices correctly lists D5 as type=esd_ic protecting USB_D+ and USB_D- nets. F1 (16V/2.5A PTC fuse) protecting VBATT and F2 (6V/0.75A PTC fuse) protecting VUSB are also correctly categorized.
- All 9 transistors in the power management circuit are detected: Q2, Q4, Q6, Q8, Q9 (DMG2305UX P-MOSFET) and Q1, Q3, Q5, Q7 (BCM857BS dual-PNP BJT). Each has correct gate/base nets, source/drain/emitter/collector nets, and associated gate resistors. This is a complex multi-MOSFET power multiplexer with BJT gate drivers.
- The feedback divider R8=180k (top) / R9=33k (bottom) from 5V to FB pin of U4 is correctly detected as a feedback network with ratio=0.155. Back-calculating: Vout = Vref/ratio = 0.8V/0.155 = 5.16V, which matches the 5V rail. The is_feedback=True flag and FB pin connection to U4 pin 3 are correct.

### Incorrect
- U4 (AP63357DV-7, 3.5A adjustable buck regulator, lib_id=SparkFun-IC-Power:AP63357DV-7) is NOT listed in signal_analysis.power_regulators, which contains only U5 (LDO). U4 converts VRAW to 5V via the detected feedback network. The regulator detector appears to match only the 'SparkFun-Regulator:' library prefix, missing the 'SparkFun-IC-Power:' prefix used for this buck regulator. U5 uses 'SparkFun-Regulator:RT9080-3.3' and is found; U4 uses 'SparkFun-IC-Power:AP63357DV-7' and is missed.
  (signal_analysis)
- design_analysis.bus_analysis.i2c reports has_pull_up=False for all four I2C buses (GPIO4/SDA0, GPIO5/SCL0, GPIO38/SDA1, GPIO39/SCL1). In reality, pull-ups are present but routed through solder jumpers: R16 (2.2k) on SDA0 and R17 (2.2k) on SCL0 pass through JP6 (I2C0 jumper) to 3.3V; R14 (2.2k) on SDA1 and R15 (2.2k) on SCL1 pass through JP5 (I2C1 jumper) to 3.3V. The bus analyzer requires a direct resistor connection from I2C net to power net and cannot trace one hop through a 3-pin jumper.
  (design_analysis)
- design_analysis.differential_pairs reports the USB_D+/USB_D- pair with has_esd=False even though D5 (DT1042-04SO) appears in shared_ics=['D5', 'J2'] for that pair. Separately, usb_compliance.connectors[0].checks.usb_esd_ic='pass' and signal_analysis.protection_devices correctly identifies D5 as an ESD IC protecting USB_D+. The differential_pairs detector shares the component list but fails to check whether any shared IC is an ESD type, creating an internal inconsistency.
  (design_analysis)

### Missed
- U2 (W25Q128JVPIM, 16MB QSPI Flash) and U3 (APS6404L-3SQR-ZR, 8MB QSPI PSRAM) are connected to U1 (RP2350B) via a shared QSPI bus (nets QSPI_D0, QSPI_D1, QSPI_D2, QSPI_D3, QSPI_CLK, FLASH_CS). The memory_interfaces list is empty in all schematic outputs including core.kicad_sch where these ICs reside. Both ICs appear in subcircuits with appropriate descriptions but the SPI/QSPI memory interface topology is not detected.
  (signal_analysis)
- design_analysis.bus_analysis.spi is empty in all schematic outputs. The RP2350B (U1) drives U2 (W25Q128) and U3 (APS6404L) via QSPI with nets named QSPI_CLK, QSPI_D0-D3, FLASH_CS. The LSM6DSOX (U6) has optional SPI aux port (pins SDO_Aux, CS). The SPI detector appears to not match these net naming conventions.
  (design_analysis)

### Suggestions
(none)

---

## FND-00001893: RP2350B microcontroller and RF module (RM2/CYW43) correctly classified and placed in subcircuits; ADC VREF RC filter (R1=200Ω, C13=4.7µF) correctly detected

- **Status**: new
- **Analyzer**: schematic
- **Source**: Hardware_core.kicad_sch.json
- **Created**: 2026-03-24

### Correct
- U1 (RP2350B) classified as type=ic and appears in subcircuits as the central MCU. U9 (RM2, Raspberry Pi CYW43 WiFi/BT module) correctly appears as a subcircuit with its description. The RM2 module description 'Radio module from Raspberry Pi using the CYW43 supporting WiFi and Bluetooth/BLE' is faithfully reproduced from the library.
- RC low-pass filter detected: R1=200Ω and C13=4.7µF with output_net=ADC_VREF, cutoff_hz=169.31Hz. This is the ADC voltage reference filter for the RP2350B's internal ADC. The R2=33Ω/C14=4.7µF filter at 1.03kHz is also detected (this filters the VREG_VOUT path). Both detections are accurate.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001894: LSM6DSOX 6-DoF IMU (U6) and DRV8411A motor drivers (U7, U8) correctly classified; User button RC filter (R21=100k, C31=0.1µF) correctly detected as 15.92Hz debounce filter

- **Status**: new
- **Analyzer**: schematic
- **Source**: Hardware_peripherals.kicad_sch.json
- **Created**: 2026-03-24

### Correct
- U6 (LSM6DSOX) detected as '6-DoF IMU' subcircuit with all surrounding decoupling caps and I2C/SPI connections. U7 and U8 (DRV8411A motor drivers) correctly identified as 'Motor Driver' subcircuits with current sense jumpers (JP8, JP9, JP10-JP13) and motor output connectors. Both DRV8411A instances have 4 test points each (TP5-TP12) correctly included in their subcircuit neighbor lists.
- RC low-pass filter R21=100kΩ / C31=0.1µF detected on GPIO36/USER_BUTTON net with cutoff=15.92Hz. This is correct: it is a hardware debounce/anti-glitch filter for the USER button (SW4). The 15.92Hz cutoff at ~10ms time constant is appropriate for a push-button debounce.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001895: Voltage divider for VIN measurement (R22/R23) correctly detected; BCM857BS PNP BJT emitter nets differ between standalone sheet and hierarchical analysis

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: Hardware_power.kicad_sch.json
- **Created**: 2026-03-24

### Correct
- Voltage divider R22=100k / R23=33k from VIN to GND with ratio=0.248 detected. Mid-point connects to JP14 (VIN_MEAS jumper) which routes to an ADC pin (GPIO46/VIN_MEAS). The ratio 33/(100+33)=0.248 scales VIN for ADC measurement, correct for a 3.3V ADC measuring up to ~13.3V. This is a correctly identified measurement divider.

### Incorrect
- In power.kicad_sch standalone output, Q5 emitter=VUSB and Q1 emitter=VBATT. In the main hierarchical output, Q5 emitter=VSYS and Q1 emitter=VRAW. The functional power topology is: VBATT→Q2(PMOS)→VRAW→Q1/Q3(PNP guard)→VRAW; VUSB→Q4/Q6(PMOS)→VSYS→Q5/Q7(PNP gate drive). The hierarchical analysis (main schematic) has the correct net resolution since global labels are resolved across sheets; the standalone power sheet analysis uses local unresolved net names. The hierarchical values are functionally correct.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001896: 6-layer board stack correctly identified: F.Cu, In1-In4.Cu, B.Cu; Thermal pad via stitching correctly detected for U1, U2, U7, U8; U4 (AP63357DV-7 PowerVFDFN-13) thermal pad not detected

- **Status**: promoted
- **Analyzer**: pcb
- **Source**: Hardware_SparkFun_XRP_Controller.kicad_pcb.json
- **Created**: 2026-03-24

### Correct
- statistics.copper_layers_used=6, copper_layer_names=['B.Cu', 'F.Cu', 'In1.Cu', 'In2.Cu', 'In3.Cu', 'In4.Cu']. Board dimensions 63.5×53.975mm. footprint_count=387, via_count=510, zone_count=57, routing_complete=True, unrouted_net_count=0. All correct.
- thermal_analysis.thermal_pads lists: U1 (RP2350B QFN-80 3.4×3.4mm EPAD) with 24 thermal vias, U2 (Flash WDFN-8) with 9 thermal vias, U7 and U8 (DRV8411A) each with 9 thermal vias. All thermal pads are on GND net. The via counts are consistent with the PCB layout strategy for heat dissipation.

### Incorrect
(none)

### Missed
- U4 (AP63357DV-7, PowerVFDFN-13 package) has an exposed pad that should have thermal via stitching. It is not included in thermal_analysis.thermal_pads. The four detected parts (U1, U2, U7, U8) are correct but U4 with its power package is missed. This may be due to the package name 'PowerVFDFN-13' not matching the thermal pad detection heuristic.
  (thermal_analysis)

### Suggestions
(none)

---

## FND-00001897: Panelized PCB reports routing_complete=False with 22 unrouted nets, but all are intentional no-connect pads

- **Status**: promoted
- **Analyzer**: pcb
- **Source**: Hardware_Production_SparkFun_XRP_Controller_panelized.kicad_pcb.json
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
- The panelized PCB shows routing_complete=False and unrouted_count=22. However all 22 'unrouted' nets are 'unconnected-' net names (e.g. unconnected-(J2-NC-PadA8), unconnected-(SW1-PadMT1)) — these are pads explicitly marked as no-connect in the schematic. Each appears 6 times because the panel contains 6 copies of the board. The individual (non-panelized) PCB correctly shows routing_complete=True with 0 unrouted nets. The panelized PCB analysis incorrectly flags intentional no-connects as routing failures.
  (connectivity)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001898: layer_count=6 correctly inferred from drill file metadata despite inner layers not parsed; GKO edge cuts file correctly identified as Edge.Cuts despite wrong X2 FileFunction attribute; Inner copper...

- **Status**: promoted
- **Analyzer**: gerber
- **Source**: Hardware_Production_.json
- **Created**: 2026-03-24

### Correct
- The drill file (SparkFun_XRP_Controller_panelized.drl) has FileFunction=MixedPlating,1,6 indicating a 6-layer board. The analyzer correctly reports layer_count=6 based on this metadata. The 8 gerber files (F.Cu, B.Cu, masks×2, silk×2, paste, edge cuts) with 4 inner copper layers (GL2-GL5) present in the directory are not parsed as copper layers.
- The GKO file has X2 attribute FileFunction=Copper,L5,Inr (wrong — this is a KiCad panelizer bug where the GKO file got an inner copper layer function). The analyzer correctly overrides this and identifies it as layer_type=Edge.Cuts based on the aperture function (Profile) and the .GKO extension. This is the correct behavior.

### Incorrect
- alignment.aligned=False with issues 'Width varies by 30.7mm across copper/edge layers' and 'Height varies by 25.8mm across copper/edge layers'. This is expected for a panelized board: the Edge.Cuts (GKO) layer covers the full panel (6 copies arrayed), making it larger than the individual board copper extents. The alignment check does not account for panelization and raises a false alarm. The individual (non-panelized) board copper layers would be aligned; the panel outline is intentionally larger.
  (alignment)

### Missed
- The Production directory contains GL2, GL3, GL4, GL5 inner copper layer gerber files (X2 FileFunction Copper,L2,Inr through Copper,L5,Inr respectively). These files are not included in the analyzer's gerbers list and are absent from completeness.found_layers. The completeness check reports complete=True based on outer layers only, missing the 4 inner copper layers. A 6-layer board completeness check should verify all 6 copper layers are present.
  (completeness)

### Suggestions
(none)

---
