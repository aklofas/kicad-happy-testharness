# Findings: hw_projects / DIYosc_diyosc

## FND-00002171: SPI bus detected twice — once from MCU pins, once from AVR-ISP-6 connector pins; 60-LED matrix driven by 4 PNP transistors not recognized as a multiplexed LED display

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: schematic_hw_projects_skadis_clock_kicad_skadis_clock.kicad_sch.json
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
- The bus_analysis.spi list contains two entries for the same physical SPI bus (SCK/MOSI/MISO on the same nets). bus_id=0 comes from U1 (ATtiny2313) pin analysis; bus_id=pin_J1 comes from the AVR-ISP-6 connector (J1) whose pins are literally named MISO/SCK/MOSI. The SPI bus detector triggers once per source of named pins rather than once per unique bus (deduplicated by net). Both entries reference the same nets and the same device.
  (design_analysis)

### Missed
- The design has 60 discrete LEDs (D1-D60) grouped into four segments, each group switched by a PNP BC807 transistor (Q1-Q4) via a common emitter/VCC topology. The transistor_circuits correctly identifies all four as BJT switches with load_type=led. However, signal_analysis.addressable_led_chains and signal_analysis.key_matrices are both empty — the multiplexed LED display pattern (transistor row-enable + resistor current-limit per LED column) is not recognized as a display topology.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00002172: Multi-unit IC (74HC00) generates 5 duplicate subcircuit entries instead of 1

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: schematic_hw_projects_DIYosc_diyosc.kicad_sch.json
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
- U1 is a 74HC00 NAND gate with 4 gate units plus a power unit (5 units total). The subcircuits list contains 5 separate entries all with center_ic=U1, each with an identical neighbor list. The subcircuit builder processes each schematic symbol instance rather than deduplicating by reference. This same bug is confirmed in VGAtest where U5 (74HC02, 5 units) produces 5 subcircuit entries.
  (subcircuits)

### Missed
(none)

### Suggestions
(none)

---

## FND-00002173: SPI and I2C buses not detected despite explicit SPI1_TX/SPI1_SCK/SPI1_CS and I2C1_SDA/I2C1_SCL net labels; I2C bus not detected despite I2C1_SDA and I2C1_SCL net labels

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: schematic_hw_projects_picocalc-pi-zero-2_pizero_adapter.kicad_sch.json
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
(none)

### Missed
- The schematic is a Pi Zero 2 W adapter to a PicoCalc connector. It carries SPI1_TX, SPI1_SCK, ~{SPI1_CS}, I2C1_SDA, and I2C1_SCL net labels alongside UART0_TX/RX (which IS detected). SPI detection requires MOSI/MISO naming conventions; SPI1_TX (vs MOSI) and ~{SPI1_CS} (negated CS) are not matched. I2C1_SDA/SCL labels are also undetected. Only UART0_TX/RX is reported. All three buses coexist on this pure pass-through adapter.
  (design_analysis)
- The adapter carries I2C1_SDA and I2C1_SCL global labels (connecting J1 to J3) but bus_analysis.i2c is empty. The UART detector matches UART0_TX/UART0_RX correctly, so the pattern-based bus detection is active. The I2C1_SDA/I2C1_SCL naming (with numeric suffix) may not match the detector's SDA/SCL patterns.
  (design_analysis)

### Suggestions
(none)

---

## FND-00002174: UART bridge between CH340N and MAX232 not detected — both ICs' UART function identified but no UART bus reported

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: schematic_hw_projects_rs232usb_kicad_rs232usb.kicad_sch.json
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
(none)

### Missed
- The design is a USB-to-RS232 adapter: USB-C -> CH340N (USB-UART IC) -> unnamed nets __unnamed_5/6 -> MAX232 (UART-RS232 IC) -> DE-9 socket. The ic_pin_analysis correctly identifies U1 (CH340N) as 'USB interface' and U2 (MAX232) as 'UART interface', and the pin connections are traced correctly (CH340N TXD pin 6 on __unnamed_5 connects to MAX232 T1IN pin 11). However, design_analysis.bus_analysis.uart is empty because the UART net names are anonymous (__unnamed_5, __unnamed_6), not labeled TX/RX.
  (design_analysis)

### Suggestions
(none)

---

## FND-00002175: USB-C CC1/CC2 compliance failure correctly detected: 1K5 resistors used instead of required 5K1

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: schematic_hw_projects_usbasp_kicad_usbasp.kicad_sch.json
- **Created**: 2026-03-24

### Correct
- J3 is a USB_C_Receptacle_USB2.0_14P with CC1 (pin A5) pulled to GND through R12 (1K5) and CC2 (pin B5) pulled to GND through R13 (1K5). USB-C spec requires Rd = 5.1kΩ ± 10% for a UFP (device). 1.5kΩ is far out of spec. The usb_compliance check correctly reports cc1_pulldown_5k1: fail and cc2_pulldown_5k1: fail. By contrast, the rs232usb design from the same author uses 5K6 resistors (within the allowed 4.59–5.61kΩ tolerance) and passes.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00002176: ESP32 auto-reset circuit correctly detected: two NPN transistors driving BOOT and EN lines

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: schematic_hw_projects_flipperzero_esp_kicad_flipper_esp32.kicad_sch.json
- **Created**: 2026-03-24

### Correct
- Q1 and Q2 are Q_NPN_BCE transistors (SOT-23) forming the classic ESP32 auto-reset circuit. Q2 drives the BOOT net (pulled low to enter bootloader) and Q1 drives the EN net (pulled low to reset). Both have base resistors (R4 and R3) and their emitters to GND. The design_analysis.bus_analysis.uart correctly identifies FP_TX and FP_RX as the UART connection between the Flipper Zero host and the ESP32. transistor_circuits correctly identifies load_type=ic for both transistors.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00002177: VGA interface not detected despite HSYNC, VSYNC, PIXEL, PCLK signals and a 25.175 MHz oscillator; Parallel memory interface (2764 EPROM + 6264 SRAM) not detected

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: schematic_hw_projects_VGAtest_kicad_vga.kicad_sch.json
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
(none)

### Missed
- The VGAtest design generates VGA video using a Xilinx XC9536 CPLD and ATmega16. It has explicit global labels HSYNC, VSYNC, VSYNC_D, HSYNC_D, PIXEL, and PCLK, plus a 25.175 MHz oscillator (the standard VGA 640x480@60Hz pixel clock) and a DE-15 HD (J2 = DE15_Receptacle_HighDensity_MountingHoles, the VGA connector). The signal_analysis.hdmi_dvi_interfaces list is empty. There is no VGA-specific detector, so these signals are completely unrecognized as a VGA interface.
  (signal_analysis)
- The design has U4=2764 (8KB parallel EPROM) and U2=6264 (8KB parallel SRAM), classic 8-bit parallel memory ICs. They share address/data bus signals routed through 74HC245/74AHC244 bus transceivers. signal_analysis.memory_interfaces is empty. The memory interface detector likely targets serial memory protocols (SPI flash, I2C EEPROM); parallel bus memory with unlabeled address/data lines is not detected.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00002178: 327x95mm board correctly identified as exceeding JLCPCB 100x100mm standard pricing tier

- **Status**: promoted
- **Analyzer**: pcb
- **Source**: pcb_hw_projects_skadis_clock_kicad_skadis_clock.kicad_pcb.json
- **Created**: 2026-03-24

### Correct
- The skadis_clock PCB is 327mm × 95mm — a long display board holding 60 LEDs arranged as four 7-segment digit groups. The DFM analysis correctly flags this as a board_size violation: 327.0×95.0mm exceeds the 100×100mm threshold, resulting in a higher fabrication pricing tier at JLCPCB. dfm_tier is reported as 'standard' with violation_count=1.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
