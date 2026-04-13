# Findings: jago85/Brutzelkarte_PCB / brutzelkarte

## FND-00000433: LD1-LD4 (Device:LED_Small) classified as 'inductor' instead of 'led'; 'led' component type missing entirely from component_types; LEDs counted under 'inductor'

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: fpga.sch.json
- **Created**: 2026-03-23

### Correct
(none)

### Incorrect
- The four LED components LD1, LD2, LD3, LD4 use lib_id 'Device:LED_Small' and value 'LED_Small'. The analyzer classifies them as type 'inductor', causing component_types to show 'inductor': 4 with no 'led' type at all. The same misclassification propagates to brutzelkarte.sch.json (the hierarchical root which aggregates all sheets). The ferrite bead L1 in usb_uart.sch is correctly classified as 'ferrite_bead', so the issue is specific to the 'LED_Small' symbol not being matched by the LED classification rules.
  (statistics)
- fpga.sch contains LD1-LD4 (4 LEDs with LED_SMD:LED_0603_1608Metric footprints). These are not present under a 'led' key in component_types — instead they inflate the 'inductor' count to 4. The same affects the aggregated brutzelkarte.sch output. The correct counts are: led=4, inductor=0.
  (statistics)

### Missed
(none)

### Suggestions
- Fix: LD1-LD4 (Device:LED_Small) classified as 'inductor' instead of 'led'

---

## FND-00000434: crystal_circuits[] empty despite Y1 (32768 Hz crystal) with MCP7940N RTC present; I2C bus falsely detected on unconnected FPGA pin stub nets (__unnamed_63, __unnamed_64); RTC I2C bus (MCP7940N on R...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: brutzelkarte.sch.json
- **Created**: 2026-03-23

### Correct
(none)

### Incorrect
- The bus_analysis i2c section reports two I2C nets: __unnamed_63 (connected only to FPGA U2 pin 125, 'PT22D/SDA/PCLKC0_0') and __unnamed_64 (connected only to FPGA U2 pin 126, 'PT22C/SCL/PCLKT0_0'). Both nets have point_count=1 and no pull-up resistors or other devices. These are isolated, single-pin stub nets on FPGA GPIO pins that happen to include 'SDA'/'SCL' as alternate-function names in the pin label. They are not a real I2C bus. The actual I2C bus (MCP7940N RTC on RTC_SCL/RTC_SDA with 4.7 kΩ pull-ups R16 and R18) is not detected.
  (design_analysis)
- The voltage_dividers list contains two entries for ROM_SCK and BOOT_SCK. Each has a 10 kΩ resistor to +3V3 (R21/R24) and a 10 kΩ resistor to GND (R22/R25), with the mid-point being the SPI clock line and a 100 nF filter capacitor (C34/C32) also at the mid-point. These are not voltage dividers being used to set a bias level; they are SPI clock lines with termination/bias resistors and RC low-pass filters — a common technique to reduce SPI clock edge rates. The ROM_SCK and BOOT_SCK net names make the SPI context clear. The equal 10k/10k ratio and the presence of a filter capacitor are characteristic of this topology rather than a signal-level voltage divider.
  (signal_analysis)

### Missed
- The memory sub-sheet contains a 32768 Hz crystal Y1 (Device:Crystal_Small) with two 6-9 pF load capacitors C23 and C24, connected to the MCP7940N real-time clock U4. The crystal_circuits detector returns an empty list. Y1 is typed correctly as 'crystal' but its pins array is empty (a KiCad 5 legacy parsing limitation), so the crystal circuit cannot be resolved. The detector should still identify the crystal by net topology: C23 and C24 are each on separate unnamed nets with only one pin each, adjacent to Y1.
  (signal_analysis)
- The memory sheet contains an MCP7940N RTC (U4) whose SCL and SDA lines (RTC_SCL, RTC_SDA) each have a 4.7 kΩ pull-up resistor (R18 and R16 respectively) to +3V3. This is a clear I2C bus with pull-ups, but it does not appear in design_analysis.bus_analysis.i2c. The root cause is that U4 has no pins extracted (pins=[]) due to the KiCad 5 legacy parser, so the SCL/SDA net membership for U4 is unknown. Nonetheless, the named nets RTC_SCL/RTC_SDA with 4.7 kΩ pull-ups are detectable by net name pattern alone.
  (design_analysis)
- The design contains three SPI flash chips: U5 and U6 (S25FL256S, 16-pin SOIC with SCK, SI/IO0, SO/IO1, ~WP~/IO2, ~HOLD~/IO3, ~CS pins) and U7 (W25Q_SOIC8 with SCK, DI/IO0, DO/IO1, ~WP~/IO2, ~HOLD~/IO3, ~CS pins). All three are connected on named SPI nets (ROM_SCK, ROM_CS0/CS1, ROM_IO[0..3], BOOT_SCK, BOOT_CS, BOOT_IO[0..3]). No SPI interface is reported in design_analysis.bus_analysis.spi. The SPI flash SCK pins end up on anonymous nets in the parser output (e.g., __unnamed_190, __unnamed_195, __unnamed_198) rather than the named ROM_SCK/BOOT_SCK nets, breaking SPI detection.
  (design_analysis)
- U3 is an IS62WV12816EBLL 128K×16 asynchronous SRAM with a 17-bit address bus (RAM_A[0..16]) and 16-bit data bus (RAM_DQ[0..15]), plus RAM_CE, RAM_WE, RAM_OE, and byte-enable signals. This is a classic parallel memory bus interface. The signal_analysis.memory_interfaces list is empty. Contributing factors include the pin-to-net mapping errors for U3 in the KiCad 5 parser (multiple U3 data and address pins end up on GND/+3V3/wrong nets due to position-based pin matching failures for the 44-pin TSOP package), preventing the analyzer from recognizing the memory bus topology.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00000435: LDO regulator U8 (TLV1117LV) input_rail reported as null instead of USB_VCC

- **Status**: new
- **Analyzer**: schematic
- **Source**: power.sch.json
- **Created**: 2026-03-23

### Correct
- The power_regulators entry for U8 shows input_rail=null. The TLV1117LV in SOT-223 has a non-standard library pinout where pin 1 is named 'GND' (actually the adjust/tab) and pin 3 is named 'VIN'. In this schematic, pin 1 is connected to USB_VCC (the actual input) and pin 3 is on GND (the adjust return path). The analyzer cannot identify USB_VCC as the input because it looks for a pin named VIN to find the input rail, and the pin named VIN is on GND. The input_rail should be USB_VCC.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
