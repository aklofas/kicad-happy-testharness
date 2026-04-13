# Findings: OLIMEX/RP2040pc / HARDWARE_RP2040pc-REV.B_RP2040pc_Rev_B

## FND-00000135: RP2040 SBC with DVI, USB, battery management - good power regulation analysis with 3 regulators detected and 7 voltage dividers; audio PWM filters and protection diodes correctly found; crystal circuit undetected; DVI interface not analyzed

- **Status**: confirmed
- **Analyzer**: schematic
- **Source**: repos/RP2040pc/HARDWARE/RP2040pc-REV.B/RP2040pc_Rev_B.kicad_sch
- **Created**: 2026-03-14

### Correct
- TPS62A02 switching regulator correctly identified with feedback divider R36/R37 (220k/49.9k), ratio 0.185, estimated Vout 3.25V
- MT3608 boost converter correctly identified with feedback divider R34/R35 (8.25k/1.05k), ratio 0.113, estimated Vout 5.31V
- CH217K USB power switch correctly identified for +5V_USB_HOST
- PWM audio voltage dividers R14/R12 (270R/150R) and R15/R13 (270R/150R) for stereo audio correctly detected with 0.357 ratio
- Battery sensing divider R41/R42 (470k/470k) with 0.5 ratio on GPIO29/BAT_SENS correctly identified
- Power sensing divider R39/R40 (220k/470k) with 0.681 ratio on GPIO28/PWR_SENS correctly found
- VBUSM sensing divider R50/R51 (47k/100k) for USB hub at 0.680 ratio correctly detected
- 5 protection diodes correctly classified: D1/D5/D7 (1N5822 reverse polarity), D9 (battery reverse polarity), D4 (optional power OR-ing)
- Crystal load cap filter R6 100R / C15 18pF at 88.4MHz correctly found (though this is crystal circuit, not RC filter)
- HUB_RST# RC delay (R45 10k / 10.1uF parallel caps at 1.58Hz) correctly detected for USB hub reset timing
- LC filter (L1 2.2uH / 44uF at DCDC_VIN, 16.18kHz resonance) correctly identified
- Decoupling analysis shows +3.3V at 25.1uF across 11 caps, +1V1 at 2.4uF across 3 caps, +5V at 79.1uF across 4 caps
- MOSFET BSS138 level shifter (FET1) identified as transistor circuit
- 12 power rails correctly enumerated including VBUS_PGM, VBUS_PWR, PWR_SW for power path management

### Incorrect
- Crystal circuit components (R6 100R series with C15/C16 18pF load caps) classified as RC filter at 88.4MHz - this is the RP2040 12MHz crystal oscillator circuit
  (signal_analysis.rc_filters)
- Buttons (BOOT1 with T1102D footprint) classified as type other instead of switch
  (statistics.component_types)
- Some items classified as other (4 total) likely include buttons and connectors that should have proper types
  (statistics.component_types)

### Missed
- No crystal circuit detected for RP2040 12MHz crystal with 18pF load caps (C15/C16) and 100R series resistor (R6)
  (signal_analysis.crystal_circuits)
- DVI connector (DVI1) with 8 series resistors (R24-R31) for TMDS differential pairs not detected as display interface
  (design_analysis.differential_pairs)
- Audio output circuit (SPK_L1, SPK_R1 speaker connectors with AUDIO1 headphone jack) not linked into audio signal chain
  (signal_analysis.buzzer_speaker_circuits)
- USB hub IC not detected as subcircuit (U4 with VBUSM pin suggests FE1.1s or similar)
  (subcircuits)
- Battery charger circuit not identified despite CHARGING1 LED and battery management components present
  (subcircuits)
- Power path management (D1/D5/D7/D9 Schottky diode OR-ing between USB/battery/external power) not analyzed as power path topology
  (signal_analysis.protection_devices)
- PGM/RUN1 connector for RP2040 programming/debug not detected
  (subcircuits)

### Suggestions
- Crystal circuit detection: RP2040 pattern uses 100R series resistor + 18pF load caps (different from ESP32 pattern of 10M feedback + 22pF caps). Detector needs to handle both topologies.
- DVI/HDMI TMDS detection: look for 8 matched series resistors (typically in 4 pairs) connecting MCU GPIO to DVI/HDMI connector - common in RP2040 PIO-based DVI designs
- Power path topology analysis: when multiple Schottky diodes create OR-ing between power sources (USB, battery, external), this should be identified as a power path management circuit
- Battery charger detection: look for charging LED + charge controller IC + battery connector pattern

---
