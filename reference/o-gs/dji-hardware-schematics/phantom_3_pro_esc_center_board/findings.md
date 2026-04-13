# Findings: o-gs/dji-hardware-schematics / phantom_3_pro_esc_center_board

## FND-00002613: DJI Phantom 3 Pro ESC center board with 4x DRV8301 3-phase motor drivers, 4x TMS320F28027F DSPs, LM25116 + 2x TPS54531 switching regulators, and 2x LED driver channels; major misclassifications of DRV8301 as diode and TMS320F28027F as transformer, missed current sensing and feedback networks

- **Status**: new
- **Analyzer**: schematic
- **Source**: phantom_3_pro_esc_center_board_phantom_3_pro_esc_center_board.sch.json
- **Created**: 2026-03-23

### Correct
- 3 switching power regulators correctly identified: LM25116 and 2x TPS54531
- 6 AON6504 MOSFETs correctly identified as motor-driving transistor circuits in the 3-phase bridge
- Q25/Q26 correctly identified as NMOS driven by LM25116 gate driver IC in the buck converter
- MOTOR_A/B/C drain net labels on high-side FETs correctly identified as motor load type
- Voltage divider R134 (102k) / R133 (21k) from +BATT correctly detected with 17% ratio for LM25116 enable
- 2 crystal circuits detected for TMS320F28027F DSP with 36pF load caps
- 2 LC filters correctly identified: L14/C172 (159kHz) and L15/C183 (65kHz) for switching regulators
- USB data lines (DP/DM) detected with ESD protection observation
- 4 power rails correctly identified: +3.3V, +BATT, GND, VCC
- +BATT decoupling analysis correct with 7 caps totaling 442uF including bulk electrolytics
- 80 resistors correctly counted in statistics
- 76 capacitors correctly counted in statistics
- 10 connectors correctly identified (BAT, GPS, GIMBAL, USB, OFDM, CMPAS, API, MC_FRONT, MC_BACK, BAT_PWR)

### Incorrect
- T1 (TMS320F28027F) classified as 'transformer' - it is a TI C2000 series 32-bit DSP/microcontroller (48-pin TSSOP). Misclassified because the library uses 'T' as the default reference prefix in DEF line. Should be type 'ic' and counted as such.
  (components[ref=T1].type)
- D5 (DRV8301_DCA_56) classified as 'diode' - it is a TI DRV8301 3-phase brushless motor pre-driver IC (56-pin) with integrated buck regulator, charge pump, SPI interface, and current shunt amplifiers. Misclassified because reference starts with 'D'. Should be type 'ic'.
  (components[ref=D5].type)
- statistics.ic count is 3 but should be 5 (U1, U2, U3 plus T1/TMS320F28027F and D5/DRV8301)
  (statistics.component_types.ic)
- RF matching false positive: C36 (2.2uF) and C33 (2.2uF) identified as antennas with matching networks (L3, L2), but these are MCU power supply decoupling capacitors on the +3.3V rail near the TMS320F28027F, not RF components
  (signal_analysis.rf_matching)
- Crystal Y1 and Y2 share the same load caps (C37/C38) in the output, but they are two separate crystals each with their own load cap pair. The analyzer appears to have assigned the same caps to both crystals.
  (signal_analysis.crystal_circuits)

### Missed
- 3-phase H-bridge motor drive topology not identified: Q1/Q2 (phase A), Q3/Q4 (phase B), Q5/Q6 (phase C) with DRV8301 gate driver, 10mOhm sense resistors, and bootstrap capacitors. This is the core ESC function.
  (signal_analysis.bridge_circuits)
- Current sensing not detected: R21 (10mOhm) and R25 (10mOhm) are low-side current sense resistors for motor phases A and B (connected to DRV8301 SP1/SN1 and SP2/SN2 shunt amplifier inputs). R155 (0.01 Ohm) is the LM25116 current sense resistor.
  (signal_analysis.current_sense)
- SPI bus not detected: SPISIMOA, SPISOMIA, SPICLKA, SPISTEA# nets connect TMS320F28027F to DRV8301 for motor driver configuration and status readback
  (signal_analysis)
- Feedback network for LM25116 not detected: R134 (102k)/R133 (21k) voltage divider feeds back to U3 pin 11 (DEMB) for output voltage regulation. The voltage divider is detected but not linked as a feedback network.
  (signal_analysis.feedback_networks)
- Multiple UART interfaces not detected: ESC_TX/ESC_RX, U3_TX/U3_RX, U4_TX/U4_RX, U7_TX/U7_RX, U8_TX/U8_RX are serial communication buses between the ESC MCUs and the flight controller
  (signal_analysis)
- Brushless motor symbol (M1, Brushless_Motor_3phase) classified as 'other' - could be specifically recognized as a motor/actuator
  (components[ref=M1].type)
- DRV8301 internal buck regulator topology not detected: the DRV8301 has pins for an internal buck converter (PH, BSTBK, PVDD2, ENBUCK, SSTR) that generates VCC rail, with external L1 (22uH), D6 (Schottky), and C15 (47uF)
  (signal_analysis.power_regulators)
- LED driver circuits not identified: 2 instances of phantom_3_pro_led_drv.sch with Q29/Q30 (PMST3904 BJTs) driving LEDs through R186-R191 current limiting resistors for red/green motor position indicators
  (signal_analysis)

### Suggestions
- Component classification should look at lib_id and pin count, not just reference prefix - a 56-pin 'D' prefix part or 48-pin 'T' prefix part cannot be a simple diode or transformer
- Detect 3-phase bridge topologies when 6 MOSFETs are found in high/low-side pairs with motor labels
- Recognize low-value resistors (< 100mOhm) connected between MOSFET source and ground as current sense resistors
- Detect SPI bus when nets with SPI-related names (MOSI/MISO/SCK/CS or SPISIMO/SPISOMI/SPICLK/SPISTE) connect two ICs
- Link voltage dividers to feedback_networks when mid-point connects to a regulator FB pin
- RF matching detection should require RF-frequency components or antenna symbols, not just L+C near a power pin

---
