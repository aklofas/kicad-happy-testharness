# Findings: aswinvenu/beaglev-kicad / BeagleV_BeagleV

## FND-00002593: BeagleV v0.7 RISC-V SBC (VIC-V10 SoC, LPDDR4, USB3 hub, Ethernet, HDMI, WiFi/BT) - 19-sheet hierarchical design with 643 components; good signal detection for crystals, RC filters, I2C, and one voltage divider; missed LPDDR4 memory interfaces, misidentified HDMI connector and TPS65086100 feedback, LMR62014 Vref wrong

- **Status**: new
- **Analyzer**: schematic
- **Source**: BeagleV_BeagleV.kicad_sch.json
- **Created**: 2026-03-23

### Correct
- Correctly identified 5 crystal circuits (X1, X3, X4, X6, X?) with load capacitors and effective load pF calculations
- Correctly detected 8 RC filter networks in the audio DAC output section (R265-R272 with C309-C314)
- Correctly identified R261/R264 voltage divider (49.9K/13.3K) as feedback for U13 LMR62014 boost converter
- Correctly detected 4 I2C buses (I2C0 SCL/SDA, I2C2 SCL/SDA) with pull-up resistors and connected devices
- Correctly detected Ethernet PHY U5 (KSZ9031RNXCA) in ethernet_interfaces
- Correctly identified 2 power regulators: U13 (LMR62014 switching) and U14 (TPS65086100 PMIC)
- Correctly identified J13 as USB Type-C connector with passing CC1/CC2 5.1K pulldown checks
- Correctly detected RF matching network for ANT1 antenna (RFECA3216060A1T) with L3 10nH and C213 1pF
- Correctly identified 6 protection devices including TVS diodes (D1, D2, D4, D5), Schottky (D52 SMBJ5.0CA), and fuse F2
- Correctly detected 4 MOSFET transistor circuits: Q1/Q3 (CJ1012 LED drivers), Q8 (IRLML6401 P-ch power switch), Q2 (USB power control)
- Total component count of 643 is consistent with 640 unique non-power references across 19 hierarchical sheets
- Correctly identified 19 hierarchical sheets in this complex SBC design
- Decoupling analysis correctly identified 5 power rails with capacitor coverage details

### Incorrect
- LMR62014 (U13) has both input_rail and output_rail set to +5V, which is impossible for a boost converter; the input should be a lower voltage rail (CTL5 or similar) and output should be VSYS_5V8/+5V
  (signal_analysis.power_regulators)
- TPS65086100 (U14) feedback_divider incorrectly identifies R100=100K and R167=4.7K as its feedback network; these are actually gate resistors for Q3 (CJ1012 LED driver MOSFET), not feedback for the PMIC which uses internally-set voltages
  (signal_analysis.power_regulators)
- LMR62014 estimated_vout of 2.851V uses assumed Vref=0.6V, but the LMR62014 datasheet specifies Vref=1.233V; correct Vout would be ~5.86V (matching VSYS_5V8 rail)
  (signal_analysis.power_regulators)
- HDMI interface detection found P? (HDMI_1V8 power symbol) as the HDMI connector instead of J11 (ST-HD-010 actual HDMI connector) and missed U11 (TDA19988 HDMI transmitter IC) as the encoder
  (signal_analysis.hdmi_dvi_interfaces)
- Ethernet interface found U5 (KSZ9031RNXCA) but shows empty magnetics and connectors arrays; J6 (LPJG0801HBNL RJ45 with integrated magnetics) should be detected as the connector
  (signal_analysis.ethernet_interfaces)
- IC pin analysis reports 0 connected pins for all 96 IC entries despite signal detectors successfully resolving net connectivity - systematic failure in pin connectivity counting
  (ic_pin_analysis)
- OSC1 (32.768kHz-clock oscillator module) classified as type=other; should be classified as oscillator or crystal
  (statistics.component_types)

### Missed
- LPDDR4 memory interfaces not detected: U7 and U8 (32Gbit_RAM) are LPDDR4 chips with full address/data bus connections to U9 (VIC-V10 SoC)
  (signal_analysis.memory_interfaces)
- USB 3.0 hub (U1 GL3520-OS322) not identified as a bus hub/repeater in any signal analysis section; it connects upstream USB from VIC SoC to two downstream USB 3.0 Type-A ports
  (signal_analysis.design_observations)
- PCMF2USB3S USB3 ESD protection ICs (D27-D32, 6 devices) not detected in protection_devices despite being dedicated USB ESD suppressors on the Type-A port data lines
  (signal_analysis.protection_devices)
- WiFi/BT combo module U12 (AP6236) not specifically identified in any signal analysis section; has dedicated 26MHz crystal (X4), antenna matching network, and SDIO/UART interfaces
  (signal_analysis.design_observations)
- Q6 and Q7 (CSD87381P NexFET power MOSFETs) used as external power stages for TPS65086100 PMIC not detected in transistor_circuits
  (signal_analysis.transistor_circuits)
- Q9 (BCM857BS-7F-F dual PNP transistor) used in USB VBUS/OTG detection circuit not detected in transistor_circuits
  (signal_analysis.transistor_circuits)
- Multiple custom power domains from P? power flag symbols (VSYS_5V8, VCC_0V9, LDO_3V3, 3V3_WIFI, AVDD09_PLL, VETH1_DVDDH/AVDDH) not captured in power_rails
  (statistics.power_rails)
- D65 (PMEG3010CEJ) is a Schottky catch diode for LMR62014 boost converter but not linked to the regulator circuit or identified in protection_devices
  (signal_analysis.protection_devices)

### Suggestions
- Improve HDMI detection to associate TDA19988 (HDMI encoder IC) with the actual HDMI connector J11 instead of power flag symbols
- Add LPDDR4 memory interface detection: identify RAM ICs by part name pattern (xxGbit_RAM, DDR, LPDDR) and their address/data buses
- Detect integrated magnetics RJ45 connectors like LPJG0801HBNL to populate ethernet_interfaces.connectors
- For PMICs like TPS65086100, do not assign external feedback dividers when the device uses internally-set output voltages
- Recognize PCMF2USB3S and similar multi-channel USB ESD protection ICs in protection_devices
- Improve Vref heuristics for boost converters: LMR62014 uses 1.233V reference, not 0.6V; consider using a lookup table for common regulator ICs
- Detect NexFET/power MOSFET pairs (CSD87381P) associated with PMIC ICs as part of the regulator subcircuit
- Recognize custom power domain symbols (P? with values like VCC_0V9, 3V3_WIFI) as additional power rails

---
