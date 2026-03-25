# Findings: CyberKeeb2040 / PCB_MainBoard_MainBoard

## FND-00000445: Component counts are correct across both sheets: 166 total, 84 diodes, 69 switches, 5 resistors, 2 capacitors, 5 connectors, 1 IC; U1 correctly identified as Raspberry Pi Pico (MCU_RaspberryPi_and_...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: PCB_MainBoard_MainBoard.kicad_sch.json
- **Created**: 2026-03-23

### Correct
- The analyzer correctly includes components from the hierarchical sub-sheet (switch_matrix.kicad_sch) loaded via the (sheet ...) instance. Sheet 0 (MainBoard) contributes 16 components: U1 (Pico), SW1 (SW_SPDT), SW2 (SW_DIP_x04), SW3 (RotaryEncoder_Switch), R1-R5, C1-C2, J1-J5. Sheet 1 (switch_matrix) contributes 150 components: 66 SW_SPST key switches and 84 series diodes. Total 166 matches the source. The 69-switch count correctly includes SW1+SW2+SW3+66 SPST keys.
- U1 lib_id is 'MCU_RaspberryPi_and_Boards:Pico', value 'Pico', classified as 'ic'. Pin 36 (3V3) connects to +3.3V, pins 39 (VSYS) and 40 (VBUS) connect to +5V. The power domain correctly reports U1 on both +3.3V and +5V rails. The footprint is correctly read as 'MCU_RaspberryPi_and_Boards:RPi_Pico_SMD_TH' (slightly differs from source 'RPi_Pico:RPi_Pico_SMD_TH' — this is a footprint library name discrepancy between what the source declares and what the bom shows, but not an analyzer error since the lib_id portion is correct).
- SW1 uses lib_id 'Switch:SW_SPDT' (value 'PiPowerSwitch'), correctly classified as 'switch'. SW2 uses lib_id 'Switch:SW_DIP_x04' (value 'SPI_SW'), correctly classified as 'switch'. SW3 uses lib_id 'Device:RotaryEncoder_Switch' (value 'RotaryEncoder_Switch'), correctly classified as 'switch' with pins A, B, C, S1, S2.
- The bus_analysis correctly identifies a full-duplex SPI bus. SPI_MOSI, SPI_MISO, SPI_SCK are global labels that connect through the Pi Zero connector (J1) interface signals and the Pico (U1). chip_select_count is 2, corresponding to SPI_CS and PI_SPI_CS global labels seen in the schematic. The devices list shows only U1, which is correct for what the main board sheet directly connects.
- The bus_analysis correctly identifies two I2C nets (I2C0_SDA, I2C0_SCL) via global labels. It correctly reports has_pull_up: false and pull_ups: [] for both lines. This is a real design observation: the schematic routes I2C to J5 (JoyStick_Or_I2C1) and J2 (JMD0.96C OLED display) without explicit pull-up resistors in this schematic — the pullups may be on connected modules. The design_observations section correctly calls this out.
- The sleep_current_audit correctly identifies R3 and R4 as pull-up resistors on the +3V3 rail. Net tracing confirms: +3V3 → R3 pin2 → net __unnamed_2 (connecting SW3 pin A and R2 pin2); +3V3 → R4 pin1 → net __unnamed_0 (connecting SW3 pin B and R5 pin1). R3 and R4 are the actual pull-up resistors to the encoder quadrature signals. R2 and R5 are series resistors between the junction and the Enc1/Enc2 signals at U1 GPIO16/GPIO17. The pull-up current of 660 uA (2 × 330 uA at 10k on 3.3V) is numerically correct.
- Checking a sample of key pins: GPIO0 (pin 1) → net 'C6' (keyboard column); GPIO1 (pin 2) → 'C5'; GPIO2 (pin 4) → 'C4'; GPIO16 (pin 21) → 'Enc1'; GPIO17 (pin 22) → 'Enc2'; GPIO26_ADC0 (pin 31) → 'ANG2'; GPIO28_ADC2 (pin 34) → connects to LED net. The keyboard column nets C0..C6 are correctly mapped to U1 GPIO0..GPIO6 (pins 1,2,4,5,6,7,9). The named row-select nets R0..R4 correctly appear on U1 GPIO7..GPIO15 (pins 10-20). Pin 36 (3V3) → '+3.3V', pins 39/40 (VSYS/VBUS) → '+5V'. All verified pin counts and net assignments match the source schematic.
- The hierarchical_labels section reports global_label_count: 73. The labels list includes the correct global labels: SPI_SCK, SPI_MOSI, SPI_MISO, SPI_CS, PI_SPI_SCK, PI_SPI_MOSI, PI_SPI_MISO, PI_SPI_CS, I2C0_SDA, I2C0_SCL, ANG1, ANG2, LED, C0..C6, R0..R4, Enc1, Enc2, Encoder_SW_1, Encoder_SW_2, Extra1..Extra3, ExtraSource — all matching labels in the source schematic. The bus_topology correctly identifies bus-like signal groups: C (7 signals), R (5 signals), Enc (2 signals), Encoder_SW_ (2 signals), Extra (3 signals), ANG (2 signals).

### Incorrect
- The key_matrices detector reports 12 rows, 80 columns, estimated_keys: 132, switches_on_matrix: 132, diodes_on_matrix: 132. The actual design has 66 MX key switches (SW4..SW69) and 84 series diodes (D1..D84) in the switch matrix, giving 5 rows (R0..R4) × some columns + 7 column lines (C0..C6) plus extras. The reported 132 switches_on_matrix is double the actual 66 SPST key switches, and 132 diodes_on_matrix is incorrectly higher than the actual 84 diodes. The columns count (80) is grossly over-stated — the switch_matrix has ~66 unique switch-diode pairs connected to R0..R4 (rows) and C0..C6 + a few extras (columns). The row_nets correctly show C0..C6 and R0..R4 (12 nets) but the column count (80) reflects all unnamed single-switch nets rather than actual column buses. The estimated_keys value of 132 appears to arise from counting both unnamed switch-side nets and named row/column nets, effectively double-counting.
  (signal_analysis)
- The Pico's VSYS (pin 39) and VBUS (pin 40) are both connected to the '+5V' power net in this schematic, and the power_domains groups them both as '+5V'. In Pico architecture, VSYS is the main power input (can be 1.8–5.5V) and VBUS is USB 5V. However the schematic connects both to the '+5V' rail label, so this mapping reflects the schematic accurately. The ic_power_rails reports ['+3.3V', '+5V'] for U1 — the Pico's internal 3.3V regulator output (pin 36/3V3) is labeled '+3.3V' in this schematic (not '+3V3'), which is correct per the schematic's power symbol usage. The missing rail '+3V3' (separate KiCad power symbol used by R3/R4) is not included in U1's power rails, which is correct since U1 pin 36 connects to '+3.3V' (different symbol name). No error here, but the distinction between the '+3.3V' (Pico output) and '+3V3' (encoder pull-up supply) rails being treated as separate domains is correct.
  (signal_analysis)

### Missed
- J3 is a 3-pin header (Connector:Conn_01x03_Female, value 'WS2812') with a 330Ω series resistor R1 connecting the LED data line. The global label 'LED' connects to the Pico (U1 GPIO28_ADC2 via 'LED' global label). The signal_analysis.addressable_led_chains section returns an empty list []. The design uses J3 as an external connector for WS2812 LED strips — a standard WS2812 signal path with a series resistor (R1=330Ω) on the data line. The analyzer should detect the J3 WS2812 connector + R1 series resistor pattern as an LED chain interface.
  (signal_analysis)
- J1 uses footprint 'PiZero:Raspberry_Pi_Zero_Socketed_THT_MountingHoles_Castellated' and value 'Pi_Zero'. It is a 40-pin (2×20) connector providing the Pi Zero GPIO interface carrying the SPI bus (PI_SPI_MOSI, PI_SPI_MISO, PI_SPI_SCK, PI_SPI_CS), I2C (I2C0_SDA, I2C0_SCL), and power (Pi_VCC local net). The analyzer classifies J1 only as a generic 'connector' type. No design_observation or special annotation identifies it as a Raspberry Pi Zero expansion header, even though the footprint name and value strongly indicate it. This is not a critical miss but represents a missed annotation opportunity.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00000446: switch_matrix.kicad_sch correctly parsed as standalone sheet: 150 components (84 diodes, 66 switches), no power rails; switch_matrix net topology correctly resolves row nets (R0..R4), column nets (...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: PCB_MainBoard_switch_matrix.kicad_sch.json
- **Created**: 2026-03-23

### Correct
- The switch_matrix schematic is a sub-sheet with only Device:D diodes and Switch:SW_SPST switches. The analyzer correctly reports total_components: 150, diode: 84, switch: 66, and power_rails: [] (no power symbols in this sheet). All 66 SPST switches (SW4..SW69) and all 84 diodes (D1..D84) are correctly enumerated. No ICs, capacitors, or connectors are present, which matches the source.
- The net R1 in switch_matrix correctly connects D35 (K), D42 (A), D37 (A), D39 (A), D40 (A), D36 (A), D34 (K), D32 (K), D31 (K), D41 (A), D30 (K), D29 (K), D38 (A) — these are the diodes whose anodes or cathodes share the row bus R1. The column-side nets (Encoder_SW_2, Encoder_SW_1) correctly connect SW31 pin 2 (B) and SW30 pin 2 (B) respectively through the diodes to those column buses. The Extra1/Extra2/Extra3 single-pin nets correctly have only one diode-anode pin each (D47 pin A, D62 pin A, D75 pin A), indicating extra keys with no direct column return wire in this sheet.
- The bus_topology.detected_bus_signals correctly identifies: C prefix (width 14, range C0..C6 — note the width reflects both occurrences across both sheets but the prefix detection is correct), Extra prefix (width 3, range Extra1..Extra3), R prefix (width 5, range R0..R4). These match the global labels used in the switch_matrix to implement the keyboard column (C0..C6) and row (R0..R4) matrix lines.
- Switch values match their keycap labels: SW17='SW_esc', SW18='SW_tab' (1.50u footprint), SW30='SW_back' (2.00u), SW32='SW_caps' (1.75u), SW63='SW_space' (6.25u), SW58='SW_ctrl' (1.25u), SW60='SW_alt' (1.25u), SW59='SW_super' (1.25u). All footprint sizes (1.00u standard, 1.25u for modifier keys, 1.50u for tab, 1.75u for caps, 2.00u for backspace, 6.25u for spacebar) are correctly recorded in the BOM. This correctly represents a standard TKL-style keyboard layout.

### Incorrect
- The standalone switch_matrix.kicad_sch analysis also reports switches_on_matrix: 132 and diodes_on_matrix: 132, with 80 column nets. The actual content is 66 switches and 84 diodes. The same root cause applies: the detector counts both sides of switch-diode pairs as contributing to the column count — each switch has an unnamed net on its switch-side pin (66 nets) plus the named column return nets (R0..R4, C0..C6, Extra1..Extra3, etc.), inflating the column count to 80. The switch count of 132 is approximately 2×66, suggesting each switch is being counted twice. The diode count of 132 is also inflated vs the actual 84.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---
