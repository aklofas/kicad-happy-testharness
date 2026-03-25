# Findings: flipper-zero-backpacks / pcb_Clean_Clean

## FND-00002091: I2C bus falsely detected using 'I2C_PULL_UP' control net as SCL line; BJT transistors Q5–Q8 (MMDT3906 dual PNP) not included in transistor_circuits analysis; microSD SPI interface on IO_35/IO_36/IO...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: schematic_flipper-zero-backpacks_pcb_ESP32_ESP32.kicad_sch.json
- **Created**: 2026-03-24

### Correct
- The usb_compliance section correctly identifies J19 (XUNPU TYPEC-304-ACP16) as a USB Type-C connector and verifies CC1/CC2 pull-down resistors (5.1k each, pass), D+/D- series resistors (pass), and VBUS decoupling (pass). The VBUS ESD protection check correctly fails—no TVS diode, USBLC6, or ESD protection IC appears anywhere in the schematic. This is a genuine design gap.
- The power_regulators section correctly identifies U2 as an AMS1117-3.3 LDO with input rail +5V and output rail LDO_+3.3V at 3.3V, using the fixed_suffix vref method. The RC filter on R9/C4 (10k/10uF, 1.59Hz cutoff) driving the ESP32-S2 EN pin is also correctly detected as a power-on reset delay circuit.

### Incorrect
- The analyzer reports one I2C bus entry with net 'I2C_PULL_UP' classified as an SCL line. In reality, I2C_PULL_UP is a global label that controls a P-channel MOSFET gate (Q3/Q4) to switch power to I2C pull-up resistors. It is not the SCL signal. The ESP32 board has no SDA/SCL named nets—I2C GPIO assignments are not represented as named nets in this schematic. The false detection results in a spurious I2C bus entry with has_pull_up=false and only U1 as a device.
  (design_analysis)

### Missed
- The statistics section correctly counts 12 transistors, but signal_analysis.transistor_circuits contains only 8 entries covering Q1–Q4 and Q9–Q12 (all AO3401A/AO3400A MOSFETs). Q5, Q6, Q7, and Q8 are MMDT2907A-7-F (footprint MMDT3906), dual PNP BJT packages used for power switching (+5V→Ext_+5V, +3.3V→Ext_+3.3V paths). The transistor circuit analyzer handles MOSFETs but silently skips BJTs, leaving 4 BJT-based power switching circuits uncharacterized.
  (signal_analysis)
- The SPI bus detector finds the MOSI/MISO/CLK named nets (which connect to the Flipper Zero debug/GPIO header via J21) and reports a single SPI bus with only U1 as device. However, J24 (Micro_SD_XUNPU__TF-115) is connected via IO_35 (CMD/MOSI), IO_36 (CLK), IO_37 (DAT0/MISO), and CS/SWO (DAT3/CS)—forming a complete SPI interface using GPIO-numbered net names. The SPI detector misses this second SPI instance because the nets are named IO_35/IO_36/IO_37 rather than MOSI/MISO/CLK.
  (design_analysis)

### Suggestions
(none)

---

## FND-00002092: PCF8523 RTC crystal circuit correctly detected with no load caps (RTC has internal load caps)

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: schematic_flipper-zero-backpacks_pcb_Raspberry_Raspberry.kicad_sch.json
- **Created**: 2026-03-24

### Correct
- The crystal circuit analyzer detects Y1 (32.768kHz) connected to the PCF8523T RTC (U1) and reports load_caps=[] (empty). This is correct—the PCF8523 has integrated crystal load capacitors internally, so no external load caps are needed or present in the schematic. The crystal connects directly to OSCI/OSCO pins of the PCF8523.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00002093: PWR_FLAG warnings incorrectly generated for connector-only pass-through boards

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: schematic_flipper-zero-backpacks_pcb_Clean_Clean.kicad_sch.json
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
- The Clean and Protoboard schematics are Flipper Zero backpack pass-through boards consisting entirely of single-pin connectors that route Ext_+3.3V, Ext_+5V, and GND signals from the Flipper Zero header. The analyzer generates PWR_FLAG warnings for all three rails, but these are false positives: power enters via connectors (passive pins), and KiCad ERC would not flag these in practice because the power source is on the parent board. The same pattern appears in Protoboard. Connecting-piece correctly has no warnings.
  (pwr_flag_warnings)

### Missed
(none)

### Suggestions
(none)

---

## FND-00002094: 53 courtyard overlap warnings mostly false positives from ESP32-S2-WROVER module over SMD components; Edge clearance warnings incorrectly flag U1 and J19 as outside board due to complex non-rectang...

- **Status**: promoted
- **Analyzer**: pcb
- **Source**: pcb_flipper-zero-backpacks_pcb_ESP32_ESP32.kicad_pcb.json
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
- The placement_analysis reports 50 courtyard overlaps total, 40 of which involve U1 (ESP32-S2-WROVER). The ESP32-S2-WROVER is an 18x31mm RF module placed on B.Cu, and many small discrete SMD components are placed in the area beneath it on the same layer—this is an intentionally dense layout where the discrete components are on the B.Cu layer under the module footprint area. The large module courtyard causes mass overlap reporting. The 10 non-U1 overlaps (SW1/J23, J22/J23, several J20 overlaps) may be more meaningful real DFM issues.
  (placement_analysis)
- U1 (ESP32-S2-WROVER) reports edge_clearance_mm=-10.23 and J19 (USB-C) reports -2.54, implying they are outside the board. However, both components are positioned within the board's coordinate extent (board x: 99.5–165.9mm, y: 83.6–131.7mm; U1 at x=120.0, y=117.7). The board has a complex U-shaped outline with 20 edges and arcs (cutouts for the Flipper Zero connector tabs at the top), and the edge clearance calculation appears to use the bounding box or a simplified outline rather than the actual board contour, producing false negatives for components near the cutout areas.
  (placement_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00002095: Protoboard with 337 THT pads correctly counted; high density pattern recognized

- **Status**: promoted
- **Analyzer**: pcb
- **Source**: pcb_flipper-zero-backpacks_pcb_Protoboard_Protoboard.kicad_pcb.json
- **Created**: 2026-03-24

### Correct
- The Protoboard is a Flipper Zero backpack protoboard with a 2.54mm grid of plated through-holes. The analyzer correctly reports 337 THT and 18 SMD footprints (the SMD ones are the connector pads). The 358 total footprint count vs 355 (337+18) discrepancy of 3 is unexplained but minor. Board dimensions (66.42x48.1mm), 0 vias, 0 zones, and routing_complete=true are all consistent with a manual proto-pad board with only edge connector routing.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
