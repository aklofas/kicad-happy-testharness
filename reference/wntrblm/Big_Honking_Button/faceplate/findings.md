# Findings: wntrblm/Big_Honking_Button / faceplate

## FND-00000410: U3 AP2112K-3.3 VIN reported on GND net instead of +5V; VOUT on unnamed net instead of +3.3V; U3 AP2112K-3.3 output_rail reported as __unnamed_1 instead of +3.3V; U5 TL072 power supply pins inverted...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: hardware_board_board.sch.json
- **Created**: 2026-03-23

### Correct
(none)

### Incorrect
- The AP2112K-3.3 (U3) has its VIN pin (pin 1) placed at schematic coordinate (2550, 1850) by the Y-mirror transform (matrix 1 0 0 -1), which connects it to the +5V rail. However, the analyzer reports VIN on the GND net and GND (pin 2) on the +3.3V net. VOUT (pin 5) is at (3150, 1850) and connects to the +3.3V net via wire to C6/C8, but the analyzer reports it on __unnamed_1. This is caused by incorrect pin coordinate calculation for the 1 0 0 -1 Y-mirror transform used by all components in this KiCad 5 legacy .sch file. The pin Y offsets are being negated in the wrong direction, causing top/bottom pin swaps.
  (signal_analysis)
- The power_regulators entry for U3 AP2112K-3.3 reports output_rail as __unnamed_1. The VOUT pin connects via wire to a +3.3V power symbol, so it should be reported on the +3.3V net. Because of the pin-coordinate Y-mirror bug, VOUT is placed on an isolated unnamed net instead of the named +3.3V rail. This causes the regulator_caps design observation to incorrectly flag missing output capacitors for U3 (C6 and C8 are 10uF and 1uF on the real +3.3V output).
  (signal_analysis)
- The TL072 dual opamp (U5) has its power supply pins systematically swapped by the Y-mirror pin calculation bug. The library defines V- (negative supply, pin 4) at offset (-100, -300) and V+ (positive supply, pin 8) at (-100, +300). With the Y-mirror transform, both end up at swapped y-positions so the analyzer maps V- to the +12V net and V+ to the -12V net. In reality, V- connects to -12V and V+ connects to +12V, which is how the dual-supply opamp is correctly powered in this Eurorack module.
  (nets)
- The MCP6001 single-supply op-amp (U6) has its V+ and V- power pins swapped by the same Y-mirror coordinate bug. The analyzer reports V+ on GND and V- on +3.3V. In the actual schematic, V+ is connected to +3.3V and V- to GND, which is the standard single-supply op-amp configuration. This causes the power_domains analysis to incorrectly associate U6 with GND as a power rail rather than +3.3V.
  (nets)
- The GD25Q64C SPI flash (U8) has all its pins assigned to wrong nets due to the Y-mirror bug. The SOIC-8 pin layout is vertically symmetric with all data/control pins on opposite sides. After the incorrect Y-mirror transform: VCC (should be +3.3V) lands on GND, GND (should be GND) lands on +3.3V, CLK (should be FLASH_SCK) lands on FLASH_CS, ~CS (should be FLASH_CS) lands on FLASH_SCK, DO/IO1 and DI/IO0 (should be FLASH_MISO/FLASH_MOSI) end up on +3.3V, and IO2/IO3 (tied high to +3.3V) end up on FLASH_MISO/FLASH_MOSI.
  (nets)
- The MMBT3904 NPN transistor (Q1) is at P 10250 1450 with transform 1 0 0 -1. The library defines E (emitter, pin 2) at offset (100, -200) and C (collector, pin 3) at (100, 200). With Y-mirror, E moves to schematic position (10350, 1650) which connects to GND, and C moves to (10350, 1250) which connects to the D2 signal net (gate output driver). The analyzer has them backwards: it reports C on GND and E on D2. This causes the transistor_circuits analysis to classify the circuit incorrectly with collector_is_power=true (collector thought to be on GND, emitter driving signal) when in reality the emitter is grounded and the collector drives the gate output.
  (signal_analysis)
- Multiple GND-named pins of U1 ATSAMD21G18A are reported as being on the +3.3V net: pin 5 (GNDANA), pin 18 (GND), pin 35 (GND), and pin 42 (GND). These are all ground pins and should be on the GND net. The Y-mirror transform causes the VDD/VDDIO pins (which are physically adjacent but on the opposite side) to be swapped with the GND pins. This also inflates the decoupling capacitor count attributed to +3.3V.
  (nets)
- The design_observations section reports that U5 TL072 is missing -12V decoupling capacitors (rails_without_caps: ["-12V"]). In reality, C14 (1uF, 0603) is connected to the -12V net. The false observation arises because the pin inversion bug makes the analyzer think U5's V- pin is on +12V — so it searches for decoupling on +12V (where C13 exists) and finds -12V uncapped. Both C13 and C14 provide proper decoupling for the TL072's dual supply rails.
  (signal_analysis)
- The rc_filters section reports an RC-network with R5 (100k) and C15 (18pF) with cutoff 88.42 kHz. In the schematic, R5 connects between the CV conditioning node (__unnamed_27) and CV_IN. C15 (18pF crystal load cap) connects between __unnamed_27 and the A1 net (MCP6001 output). They share a node at __unnamed_27 but C15 connects to A1, not to GND, so there is no RC filter topology here. C15 is a crystal load capacitor used on the SAMD21 XTAL pins, not a filter capacitor.
  (signal_analysis)
- The rc_filters section reports a low-pass filter with R6 (200k) and two parallel capacitors C10 (0.1uF) + C15 (18pF). C10 connects between GND and VREF_-10, and R6 connects between the CV conditioning node and VREF_-10 — this could form an RC filter. However, C15 connects between the CV conditioning node and A1 (not between VREF_-10 and GND), so it is not in parallel with C10. The parallel-cap grouping logic is incorrectly picking up C15 as a parallel capacitor because both C10 and C15 share a node with R6's output side. The correct RC filter cutoff for R6+C10 alone would be 1/(2π × 200k × 100nF) = 7.96 Hz (coincidentally the same), but C15 should not be included.
  (signal_analysis)

### Missed
- The decoupling_analysis lists +3.3V, +5V, and +12V rails but omits -12V entirely. C14 (1uF, 0603) is connected between the -12V net and GND, serving as a decoupling capacitor for the TL072 negative supply. Because V+ of U5 is misassigned to -12V (due to the pin inversion bug), the analyzer does not recognize -12V as a supply rail for U5, and C14 is never attributed to any decoupling rail. The -12V decoupling coverage observation is therefore missing.
  (signal_analysis)
- The GD25Q64C is an SPI NOR flash chip connected to the ATSAMD21 via labeled nets FLASH_CS, FLASH_SCK, FLASH_MOSI, FLASH_MISO. Because the U8 pin coordinates are wrong (CLK on FLASH_CS net, ~CS on FLASH_SCK net, etc.), the SPI signal pattern is not recognized and memory_interfaces is empty. The single_pin_nets observation further shows incorrect pin-net associations (U8 ~CS said to be on FLASH_SCK, U8 IO2 on FLASH_MISO) which are direct artifacts of the pin swap. The U1 SAMD21 labels match correctly for FLASH_CS but FLASH_SCK/MOSI/MISO labels on U1 are not resolved to U8 because the U8 side has wrong pins.
  (signal_analysis)
- Both op-amps in the design are in active circuits but opamp_circuits is empty. U5 TL072 unit 1 is configured as an audio output buffer/amplifier (R5 input, R6 feedback, C10 compensation). U5 TL072 unit 2 appears in an audio path. U6 MCP6001 is a comparator/buffer for the CV input signal (connected to R7, C15, R5, and producing the A1 output). The pin-coordinate inversion causes all three inputs/output of each unit to appear on the same unnamed net (e.g., unit 2 shows +/- and output all on __unnamed_46), making valid opamp circuit pattern detection impossible.
  (signal_analysis)

### Suggestions
(none)

---
