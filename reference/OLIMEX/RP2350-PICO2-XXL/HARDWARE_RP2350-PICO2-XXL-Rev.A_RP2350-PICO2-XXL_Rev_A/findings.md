# Findings: RP2350-PICO2-XXL / HARDWARE_RP2350-PICO2-XXL-Rev.A_RP2350-PICO2-XXL_Rev_A

## FND-00001192: I2C bus detector generates 42 false positive detections — only 2 are real I2C buses; SPI bus not detected despite explicit SPI0/SPI1 net names (GPIO4-7, GPIO9-11); QSPI flash memory interface not d...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: RP2350-PICO2-XXL_Rev_A.kicad_sch
- **Created**: 2026-03-23

### Correct
- Topology, input/output rails, feedback divider, and estimated Vout (3.245 V from R13/R14) are all plausible and consistent with TPS62A02A datasheet (Vref=0.6 V).
- Crystal frequency, load capacitors C20/C21 (both 27 pF), and effective load capacitance calculation are accurate for an 18 pF crystal specification.
- 5.1 kΩ to GND on both CC lines is correct for a USB-C device port (Rd termination). vbus_esd_protection:fail and vbus_decoupling:fail are legitimate observations for this design.
- Pull-up identification with resistance, rail voltage, and has_pull_up=true is accurate for the two real I2C bus lines.
- 82 total components, 5 DNP (C2, C23, C25, R24, U4 confirmed in BOM), 36 unique parts. Missing MPN list reflects Olimex's practice of using value strings instead of formal MPNs.

### Incorrect
- GPIO2/GPIO3 (SDA/SCL) are the only true I2C buses with pull-ups. The detector is matching the alternating even/odd GPIO pin naming pattern of the RP2350B's 48 GPIO pins as SDA/SCL pairs (GPIO0=SDA, GPIO1=SCL, GPIO13=SCL, GPIO14=SDA, etc.), yielding 40 spurious I2C entries without pull-ups. Only the two entries with has_pull_up=true are genuine.
  (signal_analysis)
- spi detections: 0. The net names carry SPI0_RX(MISO), SPI0_TX(MOSI), SPI0_SCK, SPI0_CSn, SPI1_SCK, SPI1_TX, SPI1_CSn, SPI1_RX as substrings. The SPI detector appears to miss these because the net naming uses embedded slash-delimited multiplex labels rather than standalone SPI net names.
  (signal_analysis)
- power_budget shows U4 contributing 10 mA to the +3.3V rail. U4 is marked DNP (do not populate) in the schematic. DNP components should be excluded from power budget calculations.
  (signal_analysis)

### Missed
- memory_interfaces: 0. The design has three QSPI-connected flash/PSRAM ICs (W25Q128 U1, W25Q128 U4 DNP, APS6404L U5) on dedicated QSPI_SD0-3/QSPI_CLK/QSPI_CSn nets driven by RP2350B's QSPI interface. The memory interface detector does not recognize this topology.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00001193: Rev B schematic correctly captures incremental changes vs Rev A: 83 components (+1 resistor R27), same power rail set

- **Status**: new
- **Analyzer**: schematic
- **Source**: HARDWARE_RP2350-PICO2-XXL-Rev.B_RP2350-PICO2-XXL_Rev_B.kicad_sch
- **Created**: 2026-03-23

### Correct
- Rev B adds R27 (27 resistors vs 26 in Rev A), 2 extra wires (456 vs 454), and renames GPIO12 net. Otherwise identical structure including 5 DNP parts, same ICs and crystal.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001194: 4-layer stackup (F.Cu/In1.Cu/In2.Cu/B.Cu), board 29x51 mm, 90 footprints, routing complete; Footprint count matches schematic (90 PCB vs 82 schematic + 8 mechanical/logo items); Mounting holes (MH1...

- **Status**: promoted
- **Analyzer**: pcb
- **Source**: RP2350-PICO2-XXL_Rev_A.kicad_pcb
- **Created**: 2026-03-23

### Correct
- Board dimensions, copper layer count and names, via counts (170), track segments (2799), and routing_complete=true are all consistent. Stackup with 1.578 mm board thickness, 0.035/0.017/0.017/0.035 mm copper layers is plausible.
- PCB has 90 footprints including 6 Logo/Sign items (Logo_OLIMEX_80, Logo_OLIMEX_80-Bot, Logo_OLIMEX_TB, Sign_Antistatic_Small, Sign_CE, Sign_OSHW, Sign_PB-Free, Sign_RecycleBin) not in schematic BOM.

### Incorrect
- drill_classification shows mounting_holes.count=0 but 4 × 2.1mm NPTH holes exist in component_holes. The MH* footprints are mounting holes; the classifier should recognize 2.1mm NPTH as mounting holes, not generic component holes.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001195: Gerber set complete: all 4 copper layers + mask/paste/silk + edge cuts + 2 drill files; Drill classification: 170 vias (156 × 0.4mm + 14 × 0.6mm PTH) and component holes correctly enumerated

- **Status**: new
- **Analyzer**: gerber
- **Source**: Gerbers
- **Created**: 2026-03-23

### Correct
- 11 gerber files + 2 drill files, layer completeness check passes (missing_required=[], missing_recommended=[]), all layers aligned. Board area 1479 mm² matches PCB output.
- Via count matches PCB output (170). 0.4mm and 0.6mm via tools match the PCB's via sizes. T4 (0.8mm, count=0) is an artifact of a defined-but-unused tool, not an error.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001196: Rev B gerber set structurally identical to Rev A: same layer set, board size, completeness

- **Status**: new
- **Analyzer**: gerber
- **Source**: HARDWARE_RP2350-PICO2-XXL-Rev.B_Gerbers
- **Created**: 2026-03-23

### Correct
- Rev B generated with KiCad 7.0.9 vs Rev A's 7.0.11; 260 vs 261 total holes (one fewer via: 169 vs 170). All layers aligned, no missing required layers.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
