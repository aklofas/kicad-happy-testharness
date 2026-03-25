# Findings: SparkFun_Red_Vision_Touch_Display_for_Pico / Hardware_SparkFun_Red_Vision_Touch_Display_for_Pico

## FND-00001520: Touch display for Pico (55 components, KiCad 9); component counts and I2C detection correct; I2C pull-ups R3/R4 through JP1 solder jumper missed (has_pullup=False); SPI bus not detected despite GPIO18/SCK, GPIO19/PICO, GPIO16/POCI signals

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: SparkFun_Red_Vision_Touch_Display_for_Pico.kicad_sch.json
- **Created**: 2026-03-23

### Correct
- Total 55 components correctly identified: 22 jumpers, 12 resistors, 6 connectors, 4 fiducials, 4 other, 2 ICs (U1 LCD-TFT, U2 PCA9534PW), 2 capacitors, 1 LED, 1 switch, 1 transistor (Q1). All counts match the design.
- I2C bus correctly detected with two entries for SDA/GPIO4 and SCL/GPIO5 connected to U2 (PCA9534PW I2C GPIO expander). Detection is accurate — PCA9534PW is an I2C-addressed device.
- Q1 (RE1C002UNTCL NMOS) correctly detected as backlight driver switch. Gate driven by DISP_BL signal from U2 (PCA9534PW), source=GND, drain connects to backlight. gate_resistors includes R2 (100k) pull-down.
- 3.3V rail decoupling correctly identified: C1 (10uF bulk) + C2 (0.1uF bypass), total 10.1uF, has_bulk=true, has_bypass=true — accurate.

### Incorrect
- I2C bus entries report has_pullup=False for both SDA/GPIO4 and SCL/GPIO5. However R3 (2.2k) pulls up SDA through JP1 pin C -> JP1 pin B -> 3.3V, and R4 (2.2k) pulls up SCL similarly. Both are genuine I2C pull-ups connected to 3.3V through JP1 (SolderJumper_3_Bridged123, value='I2C'). has_pullup should be True and pullup_resistor should reference R3/R4.
  (design_analysis.bus_analysis.i2c)

### Missed
- SPI bus not detected despite clear SPI signal nets: GPIO18/SCK (clock), GPIO19/PICO (MOSI), GPIO16/POCI/DC (MISO/DC), GPIO17/DISP_CS (display CS), GPIO7/SD_CS (SD card CS). J6 (microSD connector) has CLK/SCK, CMD/SDI, DAT0/SDO pins. Both an SPI LCD display interface and SPI SD card interface should be detected. bus_analysis.spi is empty.
  (design_analysis.bus_analysis.spi)

### Suggestions
- Trace I2C pull-up resistor supply rails through solder jumpers (SolderJumper_* parts with Bridged state) to correctly identify pull-up voltage and set has_pullup=True
- Detect SPI buses by matching net names containing SCK/CLK, PICO/MOSI, POCI/MISO patterns (including slash-delimited aliases like GPIO18/SCK); the slash-delimited naming convention in SparkFun designs contains both GPIO number and function

---

## FND-00001521: Touch display PCB (4-layer, 43.434x9.017mm narrow pico-hat); board dimensions, routing stats, and 3-layer GND zone fill ratio all correct

- **Status**: promoted
- **Analyzer**: pcb
- **Source**: SparkFun_Red_Vision_Touch_Display_for_Pico.kicad_pcb.json
- **Created**: 2026-03-23

### Correct
- 4-layer stackup correctly identified (F.Cu, In1.Cu, In2.Cu, B.Cu). copper_layers_used=4 accurate. Board dimensions 43.434 x 9.017 mm (very narrow pico-hat form factor) correctly parsed from edge cuts.
- routing_complete=true, 426 track segments, 143 vias, unrouted_net_count=0 all correct for this fully-routed 4-layer board.
- 71 PCB nets correctly reflects copper connections (schematic has 91 nets; 20-net difference accounted for by no-connect stub nets and unnamed internal schematic nets that have no copper pads).
- GND zone spanning F.Cu, B.Cu, and In2.Cu (3 copper layers) correctly detected as is_filled=true. fill_ratio=2.512 is physically correct: filled_area=7455.42mm2 is the sum of F.Cu (2521.35) + B.Cu (2102.26) + In2.Cu (2831.81) fill areas, against outline_area=2967.74mm2. Values > 1 are expected for 3-layer zones.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
