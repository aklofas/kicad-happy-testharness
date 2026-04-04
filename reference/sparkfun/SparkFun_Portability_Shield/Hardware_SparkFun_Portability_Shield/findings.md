# Findings: SparkFun_Portability_Shield / Hardware_SparkFun_Portability_Shield

## FND-00001472: Main schematic component counts correct: 63 total with 17 resistors, 16 capacitors, 6 ICs, 5 jumpers; SPI bus (SHLD_SCK, SHLD_POCI, SHLD_PICO, SHLD_~{CS}) not detected despite clear SPI signal name...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: SparkFun_Portability_Shield.kicad_sch
- **Created**: 2026-03-24

### Correct
- The SparkFun_Portability_Shield.kicad_sch correctly reports 63 components with the correct breakdown of 17 R, 16 C, 6 IC, 5 JP, 4 ST (mounting holes), 4 FID, 4 connectors, 2 SW, 2 LED, 3 other. Power rails 3.3V_P, 5V, GND, VBATT are all correctly identified.
- The power_regulators section correctly identifies U1 (AP2112K-3.3) as LDO with input_rail 5V and output_rail 3.3V_P. The design_observations also include the regulator_voltage category for U1. The decoupling_analysis for 3.3V_P shows 7 capacitors totaling 22.3 uF, correctly pulling in C7, C2, C13, C1, C8, C10, C16.
- The rc_filters section correctly identifies R1 (10k) and C6 (1.0uF) as a low-pass filter on the OLED reset line (input_net 3.3V_P, output_net OLED_~{RESET}, ground_net GND), with cutoff_hz 15.92 Hz and time_constant_s 0.01. The design_observations also correctly identifies the reset_pin observation for U5 with has_pullup: true and has_filter_cap: true.

### Incorrect
(none)

### Missed
- The bus_analysis.spi is empty despite SHLD_SCK, SHLD_POCI, SHLD_PICO, and SHLD_~{CS} being present as net labels — classic SPI clock, POCI (MISO), PICO (MOSI), and chip select signals for an SD card (J1 microSD connector). The net SHLD_~{CS} is correctly classified as chip_select in net_classification, and SHLD_SCK as clock, but these are not aggregated into an SPI bus detection. This is a missed detection of the SPI bus used for microSD card access.
  (design_analysis)
- The bus_analysis.i2c reports has_pull_up: false for both SDA and SCL. However, R15 (2.2k) has pin 2 on SCL and R16 (2.2k) has pin 2 on SDA. Their pin 1 ends connect through JP4 (I2C pullup jumper) to an unnamed net that leads to 3.3V_P. The pullup detector fails because the resistors are not directly connected to a named power rail — the JP4 jumper interrupts the trace from power to the resistor. This is the same class of issue as the OpenScale SDA/SCL missed detection.
  (design_analysis)
- The bus_analysis.i2c SDA net lists devices ['U4', 'U5', 'U5', 'U2'] with U5 (OLED) appearing twice. The OLED (SSD1306-compatible display) has two SDA-capable pins (D1/MOSI/SDA on pin 19 and D2/SDA on pin 20), causing the duplicate. While this is technically correct that both pins connect to SDA, listing U5 twice gives the misleading impression of two separate devices. This minor reporting artifact could be filtered by using unique device references.
  (design_analysis)

### Suggestions
(none)

---

## FND-00001473: MCP73831 LiPo charger (U3) and MAX17048 fuel gauge (U2) not detected as BMS/charging system; Power sheet component counts correct: 24 components including MCP73831, AP2112K-3.3, MAX17048, LM66200; ...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: power.kicad_sch
- **Created**: 2026-03-24

### Correct
- The power sub-sheet correctly reports 24 components: 4 ICs (MCP73831, MAX17048, AP2112K-3.3, LM66200), 5 resistors, 6 capacitors, 3 connectors (JST LiPo, 1x10, 1x09 headers), 2 LEDs (status/charge indicators), 1 switch (SPDT power switch), and 3 jumpers. All component types are correctly classified.
- The power_regulators in the power sub-sheet correctly identifies U1 (AP2112K-3.3) as LDO with input_rail 5V, output_rail 3.3V_P, estimated_vout 3.3. Decoupling analysis correctly groups VBATT (4.8 uF), 5V (4.8 uF), and 3.3V_P (10.1 uF) rail capacitors. The design_observations include all three decoupling_coverage entries with correct bulk/bypass classification.

### Incorrect
(none)

### Missed
- The power.kicad_sch schematic contains U3 (MCP73831, single-cell LiPo charge controller) and U2 (MAX17048, LiPo fuel gauge IC). The bms_systems section is empty and protection_devices is empty. The MCP73831 is a classic single-cell Li-Ion/Li-Po charger that should be identified as a battery management component. The LM66200 (U7, dual ideal diode for power switchover between VBATT and 5V) is also not detected as a protection/power path device.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00001474: PCB footprint count of 103 correct with 54 SMD and 2 THT components on 2-layer board; B.Cu layer incorrectly typed as 'jumper' instead of 'signal'

- **Status**: promoted
- **Analyzer**: pcb
- **Source**: SparkFun_Portability_Shield.kicad_pcb
- **Created**: 2026-03-24

### Correct
- The Portability Shield PCB correctly reports 103 footprints (70 front, 33 back), with 54 SMD and 2 THT components. Board dimensions are 43.18mm x 43.18mm (square). Routing is complete with 425 track segments, 84 vias, 1 copper pour zone. Net count of 62 is consistent with the combined schematic (61 nets in main + multi-sheet design).

### Incorrect
- In the layers array, B.Cu (layer number 31) is assigned type 'jumper' instead of the expected 'signal'. All standard copper layers should be type 'signal'. This is a misclassification — the layer number 31 in KiCad 8.0 is the back copper signal layer, not a jumper layer. This likely occurs when the PCB's layer definition uses a non-standard type assignment internally, but the analyzer should normalize it to 'signal'.
  (layers)

### Missed
(none)

### Suggestions
(none)

---
