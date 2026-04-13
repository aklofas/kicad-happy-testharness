# Findings: kadonotakashi/KiCAD_PRJ / DFSDM_DFSDM_144

## FND-00001677: Empty schematic correctly parsed with zero components

- **Status**: new
- **Analyzer**: schematic
- **Source**: DFSDM_144.sch.json
- **Created**: 2026-03-24

### Correct
- DFSDM_144.sch is an empty KiCad 5 schematic (72 bytes, no $Comp entries). The analyzer correctly reports total_components=0, zero nets, zero wires, and empty signal analysis.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001678: Empty PCB correctly parsed with zero footprints

- **Status**: new
- **Analyzer**: pcb
- **Source**: DFSDM_144.kicad_pcb.json
- **Created**: 2026-03-24

### Correct
- DFSDM_144.kicad_pcb is a stub file (51 bytes). The analyzer correctly reports footprint_count=0 and all other counts as 0.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001679: total_components=7 but raw schematic has 10 non-power components; SPI bus correctly detected for TFT LCD interface

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: DFSDM_PDM_MIC_ARRAY_PDM_MIC_ARRAY.sch.json
- **Created**: 2026-03-24

### Correct
- The analyzer correctly identifies two SPI busses: one for the TFT LCD (LCD_SCK, LCD_MOSI, half-duplex with CS) and one for a touchscreen (TP_MISO, TP_MOSI, TP_SCK, full-duplex with CS). Both are correctly detected from the TFT_LCD_SPI component pin names.

### Incorrect
- The raw PDM_MIC_ARRAY.sch contains 10 non-power components: U1, U3, U2, U4 (4x AE_SPM0405HD4H), U? (TFT_LCD_SPI), J1 (Conn_01x05), J? (Conn_01x03), J? (Conn_01x05), J? (Conn_01x05), J? (Conn_01x04). The output reports total_components=7 and bom reflects only 4 entries (merging duplicate refs). The components list correctly shows 10 entries, but total_components stat undercounts by collapsing duplicate unannotated references. The BOM also omits three of the four J? connectors (only showing Conn_01x05 once), losing the Conn_01x03 and Conn_01x04 variants.
  (statistics)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001680: Empty stub PCB correctly parsed with zero footprints

- **Status**: new
- **Analyzer**: pcb
- **Source**: DFSDM_PDM_MIC_ARRAY_PDM_MIC_ARRAY.kicad_pcb.json
- **Created**: 2026-03-24

### Correct
- PDM_MIC_ARRAY.kicad_pcb is a stub file (51 bytes, KiCad 6+ format with no content). The analyzer correctly reports footprint_count=0.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001681: total_components=2 but schematic has 4 non-power components (3 J? plus 1 U?); SPI bus correctly detected on ESP32 NodeMCU-32S

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: ESP32_LCD_ESP32_LCD.sch.json
- **Created**: 2026-03-24

### Correct
- The NodeMCU-32S has SCK and MOSI pins connected to named nets (SCK and MOSI), and the analyzer correctly identifies a half-duplex SPI bus with chip-select count=1.

### Incorrect
- The raw ESP32_LCD.sch contains 4 non-power components: Conn_01x04 (J?), Conn_01x07 (J?), Conn_02x05_Odd_Even (J?), NodeMCU-32S (U?). The output reports total_components=2 and the BOM only shows Conn_01x04 (missing Conn_01x07 and Conn_02x05_Odd_Even), because unannotated duplicate J? references are collapsed to the first encountered value. The component_types also only shows connector=1 when there are actually 3 connectors.
  (statistics)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001682: Empty stub PCB correctly parsed with zero footprints

- **Status**: new
- **Analyzer**: pcb
- **Source**: ESP32_LCD_ESP32_LCD.kicad_pcb.json
- **Created**: 2026-03-24

### Correct
- ESP32_LCD.kicad_pcb is a stub file (51 bytes). The analyzer correctly reports footprint_count=0.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001683: Component count correctly parsed: 74 components of 10 types; Opamp circuits correctly detected (6 instances from U4/U5 dual opamps); RC filters correctly detected: 7 instances from output filter ne...

- **Status**: new
- **Analyzer**: schematic
- **Source**: PCM5102_PCM5102.sch.json
- **Created**: 2026-03-24

### Correct
- PCM5102.sch contains 74 components including connector(4), diode(1), capacitor(27), ic(5), resistor(19), jumper(1), test_point(10), led(1), mounting_hole(4), ferrite_bead(2). All counts are correct.
- The PCM5102 board uses dual opamp ICs (U4 and U5, likely NJM2068 or similar) for I/V conversion and output filtering. The analyzer correctly detects 6 opamp circuits (3 per opamp IC, corresponding to multiple unit instantiations of the dual opamp symbol).
- The PCM5102 audio DAC board uses multiple RC filter stages in the output path. The analyzer correctly identifies 7 RC filter networks.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001684: PCB footprint count matches schematic component count (74); 2-layer PCB correctly identified with complete routing

- **Status**: new
- **Analyzer**: pcb
- **Source**: PCM5102_PCM5102.kicad_pcb.json
- **Created**: 2026-03-24

### Correct
- The PCB has 74 footprints matching the schematic's 74 components. Routing is complete (291 track segments, 29 vias, 11 zones, 2-layer board, 99x74mm).
- The analyzer correctly identifies 2 copper layers (F.Cu, B.Cu), complete routing (routing_complete=true, unrouted_net_count=0), 291 track segments, and 29 vias.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001685: Component count correctly parsed: 104 components including inductors; Voltage dividers correctly detected: 4 instances in output attenuation network

- **Status**: new
- **Analyzer**: schematic
- **Source**: PCM5122_PCM5122.sch.json
- **Created**: 2026-03-24

### Correct
- PCM5122.sch contains 104 components including 5 inductors (10uH), 32 capacitors, 5 ICs, 27 resistors, 3 LEDs, 22 test points, and 4 mounting holes. The inductor type is correctly classified.
- The PCM5122 board uses voltage divider networks in the output path for level adjustment. The analyzer correctly identifies 4 voltage dividers.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001686: PCB footprint count matches schematic (104), fully routed 2-layer board

- **Status**: new
- **Analyzer**: pcb
- **Source**: PCM5122_PCM5122.kicad_pcb.json
- **Created**: 2026-03-24

### Correct
- The analyzer correctly identifies 104 footprints, 523 track segments, 44 vias, 18 zones on a 2-layer board (99.6x72.6mm). Routing is complete.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001687: total_components=2 but schematic has 5 distinct components (4x AE-SPM0405HD4H + 1 J?); PDM microphone components correctly parsed with 4 SPM0405HD4H instances

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: PDM_PDM_PDM.sch.json
- **Created**: 2026-03-24

### Correct
- The components list correctly enumerates all 5 component instances (4x AE-SPM0405HD4H U? microphones and 1x Conn_01x05 J? connector). The VDD and GND power rails are correctly identified. The BOM correctly identifies the SPM0405HD4H as the primary device.

### Incorrect
- The raw PDM.sch has 20 $Comp entries: 4x AE-SPM0405HD4H (all ref=U?) and 1 Conn_01x05 (J?), plus 15 power symbols. The output reports total_components=2 (unique refs only) and the BOM shows only 2 entries (Conn_01x05 qty=1, AE-SPM0405HD4H qty=1) instead of qty=4 for the microphone. The components list correctly shows 5 entries, but the statistics misrepresent the actual design density.
  (statistics)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001688: Empty stub PCB correctly parsed with zero footprints

- **Status**: new
- **Analyzer**: pcb
- **Source**: PDM_PDM_PDM.kicad_pcb.json
- **Created**: 2026-03-24

### Correct
- PDM.kicad_pcb is a stub file (51 bytes). The analyzer correctly reports footprint_count=0.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001689: Component count correct: 74 including 17 LEDs, 29 resistors, 2 transistors; transistor_circuits=0 despite 2 uPA2753 transistor array ICs present; Voltage dividers correctly detected: 4 bias network...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: RingLight_RingLight.sch.json
- **Created**: 2026-03-24

### Correct
- RingLight.sch has 74 components: transistor(2), ic(2), resistor(29), capacitor(7), connector(3), jumper(1), led(17), mounting_hole(4), test_point(9). All component types are correctly classified.
- The RingLight uses R+R voltage divider networks to set bias for the uPA2753 transistor gate (G pin). The analyzer correctly identifies 4 voltage dividers (one per transistor channel), each with R_top=1k and R_bottom=20 ohm.
- The RingLight design uses RC low-pass filters (R=1k, C=100nF) for smoothing PWM control signals. The analyzer correctly identifies 4 RC filters at approximately 1.59 kHz cutoff.

### Incorrect
(none)

### Missed
- RingLight has Q1 and Q2, both uPA2753 NPN transistor arrays (SOIC-8), correctly typed as 'transistor' and with pin data available (pins 1/2/3S/5/6/7/8/G/D). However, the analyzer reports transistor_circuits=[] (0 entries). The uPA2753 uses non-standard pin names (3S, G, D) that do not match the BJT/MOSFET/JFET patterns expected by the transistor circuit detector. This is a false negative - the design does have transistor switching circuits.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00001690: PCB footprint count matches schematic (74), 2-layer board fully routed

- **Status**: new
- **Analyzer**: pcb
- **Source**: RingLight_RingLight.kicad_pcb.json
- **Created**: 2026-03-24

### Correct
- The PCB correctly has 74 footprints matching the schematic, 398 track segments, 41 vias, 9 zones on an 80x71mm 2-layer board with complete routing.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001691: Component count correct: 81 including 25 LEDs, 25 resistors, 3 ICs; transistor_circuits=0 despite 2 uPA2753 transistor arrays present

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: RingWrite2_RingWrite2.sch.json
- **Created**: 2026-03-24

### Correct
- RingWrite2.sch has 81 components correctly parsed: resistor(25), capacitor(9), ic(3), connector(4), jumper(2), led(25), mounting_hole(2), test_point(9), transistor(2). All types are correctly identified.

### Incorrect
(none)

### Missed
- Same issue as RingLight: Q1 and Q2 are uPA2753 transistor arrays with non-standard pin names (G/D/S variants), correctly typed as 'transistor' in component_types, but the transistor_circuits detector reports 0 entries. The analyzer cannot classify this custom-library transistor's switching topology.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00001692: PCB footprint count matches schematic (81), fully routed 2-layer board

- **Status**: new
- **Analyzer**: pcb
- **Source**: RingWrite2_RingWrite2.kicad_pcb.json
- **Created**: 2026-03-24

### Correct
- The PCB correctly has 81 footprints, 358 track segments, 28 vias, 5 zones on a 57x62mm 2-layer board with complete routing.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001693: total_components=2 but schematic has 4 components (1 IC + 3 connectors with different values); SPI bus falsely detected: SCK signal is on the +3.3V power net

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: SPI9341_SPI9341_SPI9341.sch.json
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
- SPI9341.sch has 4 non-power components: LCD_ILI9341_SPI (U?), Conn_01x07 (J?), Conn_01x04 (J?), Conn_01x05 (J?). The output reports total_components=2 and the BOM only shows 2 entries (1 IC + 1 connector value), missing the Conn_01x04 and Conn_01x05 variants because all three connectors share the same ref J?. The component_types shows only connector=1 instead of 3.
  (statistics)
- The analyzer detects a half-duplex SPI bus with SCK on net '+3.3V' and MOSI on '__unnamed_14'. The ILI9341's SCK pin (pin 7) is connected directly to the +3.3V power rail in the schematic — this appears to be a design-in-progress error. The analyzer should not classify a power net as an SPI SCK signal. This is a false positive SPI detection because the SCK pin is erroneously tied to a power rail.
  (design_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001694: Empty stub PCB correctly parsed with zero footprints

- **Status**: new
- **Analyzer**: pcb
- **Source**: SPI9341_SPI9341_SPI9341.kicad_pcb.json
- **Created**: 2026-03-24

### Correct
- SPI9341.kicad_pcb is a stub file (51 bytes). The analyzer correctly reports footprint_count=0.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001695: total_components=5 but raw schematic has 16 non-power component instances; DISPLAY? (I2C_OLED SSD1306) incorrectly classified as type 'diode'; 6 I2C busses falsely detected due to unannotated dupli...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: STEPPER_STEPPER.sch.json
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
- STEPPER.sch has 16 non-power component instances: 4x U? (2x NodeMCU-32S, ULN2003, AE-DRV8835), 2x SW? (Rotary_Encoder_Switch), 6x R? (10k), 2x SM? (28BYJ-48 BiPolar, 28BYJ-48 UniPolar), 2x DISPLAY? (I2C_OLED SSD1306). The output reports total_components=5 (counting only 5 unique refs), which severely undercounts the actual component density. The BOM also shows only 5 entries with qty=1 each instead of reflecting true quantities.
  (statistics)
- The I2C_OLED(SSD1306) component is classified as type='diode' in the BOM and component_types statistics. An OLED display module is not a diode. This misclassification is due to the lib_id 'kdn_kicad:I2C_OLED(SSD1306)' not matching any of the analyzer's IC/connector/display patterns. The component_types shows diode=1 instead of ic=1 (or a display subtype).
  (statistics)
- The analyzer detects 6 I2C bus entries, with SCL/SDA signals on the +3.3V and GND power nets among others. The proliferation is caused by multiple unannotated duplicate U? instances all sharing the same reference, creating spurious net connections. Only 1 genuine I2C bus (DISPLAY? OLED on SCL/SDA) likely exists. The I2C entries on '+3.3V' and 'GND' as SCL/SDA nets are clearly erroneous.
  (design_analysis)

### Missed
(none)

### Suggestions
- Fix: DISPLAY? (I2C_OLED SSD1306) incorrectly classified as type 'diode'

---

## FND-00001696: Empty stub PCB correctly parsed with zero footprints

- **Status**: new
- **Analyzer**: pcb
- **Source**: STEPPER_STEPPER.kicad_pcb.json
- **Created**: 2026-03-24

### Correct
- STEPPER.kicad_pcb is a stub file (51 bytes). The analyzer correctly reports footprint_count=0.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001697: Component count correct: 47 components including 22 test points and 3 transistors; LDO voltage regulator correctly detected (NJU7223 5V→3.3V); BJT transistor circuits correctly detected: Q1 and Q3 ...

- **Status**: new
- **Analyzer**: schematic
- **Source**: kyocera3_kyocera3.sch.json
- **Created**: 2026-03-24

### Correct
- kyocera3.sch contains 47 components: connector(4), ic(2), capacitor(7), resistor(9), test_point(22), transistor(3). All types are correctly classified.
- The analyzer correctly identifies U1 (NJU7223) as an LDO regulator with input rail +5V and output rail +3V3.
- The analyzer correctly identifies Q1 and Q3 as BJT transistor circuits. Note Q2 (uPA2753 array) is not detected due to non-standard pin names, but Q1 and Q3 (2SC1815, TO-92) are correctly analyzed.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001698: PCB footprint count matches schematic (47), 2-layer board fully routed

- **Status**: new
- **Analyzer**: pcb
- **Source**: kyocera3_kyocera3.kicad_pcb.json
- **Created**: 2026-03-24

### Correct
- The PCB correctly has 47 footprints matching the schematic, 307 track segments, 37 vias, 7 zones on a 71x51mm 2-layer board with complete routing.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001699: Component count correct: 12 components including 2 JFET transistors; JFET transistor circuits correctly detected for Q1 and Q2 (2SK2881 N-channel JFETs); RC coupling/bias filters correctly detected...

- **Status**: new
- **Analyzer**: schematic
- **Source**: mic_amp_mic_amp_mic_amp.sch.json
- **Created**: 2026-03-24

### Correct
- mic_amp.sch has 12 components: connector(2), resistor(6), capacitor(2), transistor(2). Q1 (2SK2881) and Q2 (2Sk2881) are correctly classified as transistors and detected as JFET circuits.
- The analyzer correctly identifies both Q1 and Q2 as JFET type transistors using Device:Q_NJFET_SGD. Gate resistors are correctly attributed: Q2 gate has R6, R3, R2, R1; Q1 gate has R2. The JFET topology is correctly identified.
- The mic_amp design uses C1 (0.22uF) and C2 (2.2uF) with various resistors for input coupling and bias bypassing. The analyzer correctly identifies 4 RC filter networks with computed cutoff frequencies: 1.54 Hz (47k+2.2uF bias bypass), 0.72 Hz (1M+0.22uF input coupling), and 72.34 Hz (10k+0.22uF).

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001700: Single-layer PCB correctly identified with 12 footprints and complete routing

- **Status**: new
- **Analyzer**: pcb
- **Source**: mic_amp_mic_amp_mic_amp.kicad_pcb.json
- **Created**: 2026-03-24

### Correct
- The PCB correctly has 12 footprints matching the schematic, 1 copper layer, 39 track segments, 0 vias (expected for single-layer), and complete routing on a 52x14mm board.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001701: Component count correct: 12 components including FT2232 USB-JTAG module; UART bus correctly detected on FT2232 RxD/TxD pins

- **Status**: new
- **Analyzer**: schematic
- **Source**: minimodule_minimodule.sch.json
- **Created**: 2026-03-24

### Correct
- minimodule.sch has 12 components: ic(1 AE-FT2232), connector(4), diode(1), capacitor(2), transistor(2), resistor(2). All types correctly identified.
- The analyzer correctly detects 2 UART signals (RxD net with U1 device, and TxD net) on the FT2232 USB-to-serial/JTAG module. The UART detection is accurate for the serial interface portion of the FT2232.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001702: Empty stub PCB correctly parsed with zero footprints

- **Status**: new
- **Analyzer**: pcb
- **Source**: minimodule_minimodule.kicad_pcb.json
- **Created**: 2026-03-24

### Correct
- minimodule.kicad_pcb is a stub file (51 bytes). The analyzer correctly reports footprint_count=0.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001703: total_components=4 but schematic has 8 component instances (4 J?, 2 Q?, 2 R?); JTAG debug interface not detected despite TCK/TDI/TDO/TMS signals present

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: pio_unified_debugger_pio_unified_debugger.sch.json
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
- pio_unified_debugger.sch has 8 non-power component instances: 1x AE-FT2232 (U?), 3x connectors (J? - Conn_01x06, Conn_01x07, Conn_02x05_Odd_Even), 1x additional J? connector, 2x 2SC945 (Q?), 2x 10k resistors (R?). The output reports total_components=4 (unique refs: U?, J?, Q?, R?) and shows connector=1 in component_types when there are 4 connectors. The BOM shows J? as Conn_01x06 qty=1, missing the Conn_01x07 and Conn_02x05 variants.
  (statistics)

### Missed
- The pio_unified_debugger connects FT2232 to JTAG signals (TCK, TDI, TDO, TMS) and also has RX/TX for UART. The UART is detected (2 entries), but the JTAG/debug interface is not explicitly detected as a debug bus. The design nets 'TCK', 'TDI', 'TDO', 'TMS' are classified as 'debug' in net_classification but no dedicated debug bus detection fires. This is a missed detection opportunity for JTAG/SWD interfaces.
  (design_analysis)

### Suggestions
(none)

---
