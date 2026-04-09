# Findings: biomimetics/MRIRobot_PCB / Main_PCB_V4_MRIRobot_PCB

## FND-00002537: MRI-compatible robot control PCB with dual NUCLEO-F446RE STM32 boards, CMOD A7 FPGA for high-speed encoder processing, three LSF0108 level shifters, FT231XS USB-UART bridge, dual LM22676 switching regulators (24V to 5V and 3.3V), P-channel MOSFET reverse polarity protection, 94 TVS diodes on all I/O lines, 7 motor channels, 7 encoder interfaces via RJ45, and 7 homing switches. The analyzer correctly identified power regulators, RC low-pass filters, voltage dividers, LED indicators, TVS protection, USB-C compliance, level shifters, and UART buses. Key issues include U1 NUCLEO misclassified as switching regulator, incorrect Vout estimate for U6 due to wrong Vref (0.6V vs 1.285V), Q2 reverse polarity MOSFET unrecognized, duplicate detections from multi-unit NUCLEO symbols, and missed motor driver/encoder interface pattern recognition.

- **Status**: confirmed
- **Analyzer**: schematic
- **Source**: Main_PCB_V4_MRIRobot_PCB.kicad_sch.json
- **Created**: 2026-04-09

### Correct
- U3 (LM22676MR-5) correctly identified as switching regulator with inductor L3, input 24V_5V, output +5V
- U6 (LM22676MR-ADJ) correctly identified as switching regulator with inductor L4, feedback divider R7/R5
- 21 voltage dividers for encoder signal conditioning correctly detected - all R=1k/10k pairs (ratio 0.909) feeding FPGA
- Feedback voltage divider R7=1.54k / R5=976 for U6 correctly identified with is_feedback=true, ratio 0.388
- Enable threshold divider R1=6.2k / R2=1k correctly identified, connected to U3 EN
- 7 RC low-pass filters on PWM-to-analog conversion (R=4k, C=0.01uF, fc=3.98kHz) correctly detected
- 21 RC low-pass filters on encoder lines (R=1k, C=100pF, fc=1.59MHz) correctly detected for EMI filtering
- 94 TVS diodes correctly identified as protection_devices on all signal lines
- 3 LSF0108 level shifter ICs (U10-U12) correctly identified as bidirectional translators, 3.3V to 5V
- Cross-domain signals correctly detected with level_translators assigned to U10/U11/U12
- 10 LEDs with 290 ohm series resistors correctly detected
- USB-C connector J29 correctly analyzed with CC1/CC2 5.1k pulldowns and 27 ohm DP/DM series resistors
- UART buses correctly detected: UART3 between U1 and U13 (FPGA), UART_TX/RX between U1 and U9 (FT231XS)
- Hierarchical design correctly flattened from 3 sheets
- Total component count 340 correct with proper breakdown
- Power rails correctly identified: +24V, +3.3V, +5V, GND
- Footprint filter warnings correctly flagged: resistors using capacitor footprints
- UART connectors J22/J23/J25/J26 correctly identified with TX/RX/GND nets
- Decoupling observations correct for NUCLEO, FPGA, and FT231XS
- RC filters on PS_NRST and PS_NPOR correctly detected as reset filters

### Incorrect
- U1 (NUCLEO-F446RE) incorrectly classified as power_regulator with 'switching' topology. U1 is an STM32 development board module, not a voltage regulator
  (signal_analysis.power_regulators)
- U6 (LM22676MR-ADJ) estimated_vout is 1.547V but correct value is 3.31V. Analyzer assumed Vref=0.6V but LM22676 datasheet specifies Vref=1.285V
  (signal_analysis.power_regulators)
- Inrush analysis uses wrong output voltage of 1.547V for U6, propagating the Vref error
  (inrush_analysis)
- Duplicate LED entries: D115 and D116 each appear twice due to multi-unit NUCLEO symbol
  (signal_analysis.led_audit)
- Duplicate entries in sleep_current_audit: D115/R92 and D116/R93 appear 4 times each on +3.3V rail
  (sleep_current_audit)
- USB-C connector J29 appears twice in usb_compliance.connectors due to multi-unit duplication
  (usb_compliance)
- Q2 (SUD08P06-155L P-MOSFET) pins 1 and 2 missing net assignments - only pin 3 maps to +24V. Pin-net resolution failure in sub-sheet
  (components)
- PWR_FLAG warnings may be false positives due to incomplete cross-sheet power flag resolution
  (pwr_flag_warnings)
- Protocol compliance warns UART3 needs level shifting but both U1 and U13 operate at 3.3V I/O
  (protocol_compliance)
- Level shifter side_a/side_b supply_net fields are null for all LSF0108 ICs despite having VREF_A/VREF_B pins
  (signal_analysis.level_shifters)

### Missed
- Q2 (SUD08P06-155L) P-MOSFET with D2 (Zener) and R8 (100K) reverse polarity protection on +24V input not detected
  (signal_analysis)
- Motor interface pattern (7 channels x Direction+Enable+PWM+Analog) through JST EH connectors with TVS not recognized
  (signal_analysis)
- 7 homing switch inputs (Home0-Home6) via 2-pin JST EH connectors with TVS and pull-ups not identified
  (signal_analysis)
- CMOD A7 FPGA module (U13) as high-speed encoder counter/decoder receiving 21 quadrature signals through level shifters not recognized
  (signal_analysis)
- 4 RJ45 connectors used for encoder wiring via shielded Ethernet cables not identified as deliberate EMC/MRI choice
  (signal_analysis)
- Extensive TVS protection (94 diodes) + RC filtering on all encoder inputs as deliberate MRI environment EMI hardening not synthesized
  (signal_analysis.design_observations)
- SW7 (5V Enable) and SW8 (3.3V Enable) as manual power sequencing switches not detected
  (signal_analysis.power_sequencing_validation)
- D1, D13, D14, D88 likely flyback/freewheeling diodes for motor outputs not classified
  (signal_analysis)
- R159/C86 (200k/0.1uF, fc=7.96Hz) appears to be power-on-reset/delayed enable circuit, not a signal filter
  (signal_analysis.rc_filters)
- LSF0108 level shifters may carry SPI-like signals between FPGA and NUCLEO not classified as bus
  (signal_analysis.bus_analysis)
- D114 near U9 (FT231XS) likely USB VBUS power OR-ing/protection diode not classified
  (signal_analysis)

### Suggestions
- Add LM22676 to Vref lookup with Vref=1.285V to correct 3.3V output voltage calculation
- Fix multi-unit symbol duplication: deduplicate by UUID or reference+pin in led_audit, sleep_current, usb_compliance
- Add reverse polarity protection detector for P-channel MOSFET + Zener configurations
- Add motor driver interface detector for repeated Dir+En+PWM+Analog signal groups
- Add homing/limit switch detector for pull-up + TVS + 2-pin connector patterns
- Resolve Q2 pin-net mapping failure in sub-sheet
- Improve LSF0108 analysis to resolve VREF_A/VREF_B pin connections for voltage domain identification
- Protocol compliance should check for existing level shifters before warning about domain crossing
- Consider detecting FPGA-as-encoder-counter pattern: many filtered quadrature inputs + UART output to MCU
- Detect manual enable switches as power control elements in power_sequencing

---
