# Findings: ESP32-P4-PC / HARDWARE_ESP32-P4-PC-Rev.B_ESP32-P4-PC_Rev_B

## FND-00000112: Complex SBC with HDMI, USB hub, Ethernet, audio codec well-analyzed for power regulation but missing HDMI bridge, USB hub, and audio codec subcircuit classification; crystal circuits undetected

- **Status**: confirmed
- **Analyzer**: schematic
- **Source**: repos/ESP32-P4-PC/HARDWARE/ESP32-P4-PC-Rev.B/ESP32-P4-PC_Rev_B.kicad_sch
- **Created**: 2026-03-14

### Correct
- Five power regulators correctly identified: TPS62A02 (3.3V, switching), TPS2116 (power mux, x2), MT3608 (5V boost), CH217K (USB host LDO)
- Feedback divider for TPS62A02 (R44/R45 = 30.1k/6.49k) correctly computed with ratio 0.177 giving estimated Vout 3.38V
- Feedback divider for MT3608 (R95/R98 = 8.25k/1.05k) correctly computed with ratio 0.113 giving estimated Vout 5.31V
- Battery sensing voltage divider R90/R96 (470k/470k) with 0.5 ratio correctly identified
- Power sensing voltage divider R36/R94 (220k/470k) correctly detected
- VBUSM sensing divider R69/R70 (4.7k/10k) for USB hub FE1.1s correctly found
- LDO voltage reference divider for VR1 (R52/R50 = 240R/110R) correctly identified for VCC_1.8V generation
- Ethernet PHY IP101GRR correctly detected in ethernet_interfaces
- RC filter on ESP_EN pin (R41 10k / C40 100nF, fc=159Hz) correctly found as reset delay circuit
- USB data line RC filters (R25/R26 22R with 150pF, fc=48MHz) correctly detected for USB signal conditioning
- Audio ADCVREF RC filter (R79 200R / C104 1uF, fc=796Hz) correctly identified
- Multiple audio RC filters for mic inputs (MICP/MICN) correctly detected with parallel cap computation
- 16 power rails correctly enumerated including separate analog domains (+3.3VA, GNDA, VCC_1.8V)

### Incorrect
- TPS2116 (U13) classified as LDO but it is actually a power multiplexer/switch (selects between two input supplies), not a voltage regulator
  (signal_analysis.power_regulators)
- TPS62A02 (U5) detected as switching regulator but missing estimated_vout - the feedback network for FB_DCDC was not linked to the regulator
  (signal_analysis.power_regulators)
- Crystal oscillator RC filters (R87 1M with C113/C114 27pF, fc=5.9kHz) misidentified as generic low-pass filters - these are actually crystal load capacitor bias resistors for the 40MHz crystal
  (signal_analysis.rc_filters)
- RC filter R13 10M with C1/C2 22pF classified as 723Hz low-pass but this is the crystal feedback resistor for the main oscillator
  (signal_analysis.rc_filters)

### Missed
- LT8912B HDMI bridge (U12) not identified as display interface subcircuit - this is a MIPI-DSI to HDMI converter, a significant design block
  (subcircuits)
- FE1.1s USB hub (U7) not identified as USB hub subcircuit despite being a 4-port USB 2.0 hub IC
  (subcircuits)
- ES8311 audio codec (U8) not classified as audio codec subcircuit with I2S/I2C interfaces
  (subcircuits)
- W25Q128 SPI flash (U3, 16MB) not identified as memory interface
  (signal_analysis.memory_interfaces)
- No crystal circuits detected despite ESP32-P4 having external crystal oscillator with 22pF load caps (C1/C2) and 10M feedback resistor (R13)
  (signal_analysis.crystal_circuits)
- MIPI-DSI differential pairs (to LT8912B) not detected
  (design_analysis.differential_pairs)
- MIPI-CSI camera interface not detected
  (design_analysis.differential_pairs)
- HDMI differential pairs from LT8912B to HDMI connector not detected
  (design_analysis.differential_pairs)
- RCLAMP0524P ESD protection arrays (U9, U10, U11) not linked to the USB ports they protect
  (signal_analysis.protection_devices)
- TP4054 battery charger (U15) not identified as charger subcircuit
  (subcircuits)

### Suggestions
- Detect common HDMI bridge/converter ICs (LT8912, IT6613, ADV7533) as display interface subcircuits
- Detect USB hub ICs (FE1.1s, USB2514, USB2517) and map upstream/downstream ports
- Detect audio codec ICs (ES8311, WM8960, MAX98357) and classify I2S/I2C connections
- Crystal circuit detection should look for high-value feedback resistors (1M-10M) between XTAL pins with matched load caps
- Detect SPI flash memory ICs (W25Qxxx, MX25Lxxx) as memory interfaces
- Power multiplexer ICs (TPS2116, TPS2121) should not be classified as LDO

---
