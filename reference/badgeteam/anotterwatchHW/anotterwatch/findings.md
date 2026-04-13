# Findings: badgeteam/anotterwatchHW / anotterwatch

## FND-00001838: Total component count 133 correctly aggregated across all 3 hierarchical sheets; 4 addressable SK6812MINI LEDs (D1-D4) correctly detected in a single-wire chain; I2C bus correctly detected with 3 d...

- **Status**: new
- **Analyzer**: schematic
- **Source**: anotterwatch.sch.json.json
- **Created**: 2026-03-24

### Correct
- The multi-sheet hierarchy (anotterwatch.sch + afe.sch + power.sch) contains exactly 133 unique component references with no overlap between sheets. The analyzer correctly parses all three sheets and reports statistics.total_components=133.
- signal_analysis.addressable_led_chains reports chain_length=4, protocol='single-wire (WS2812)', led_type='SK6812MINI', data_in_net='IO0'. All four LEDs D1-D4 are confirmed in afe.sch as SK6812MINI with the correct footprint.
- design_analysis.bus_analysis.i2c reports I2C_SCL and I2C_SDA each with devices=[U3, U4, U6] and 5.1k ohm pull-ups (R21, R20) to +3.3V. This matches the ESP32, BMI270, and TCA9535 devices connected on the AFE sheet.
- signal_analysis.protection_devices reports U9 as type='esd_ic' protecting PROBE1/PROBE2. The schematic (afe.sch) confirms USBLC6-4SC6 is connected to PROBE1 and PROBE2 (analog measurement probe lines), not USB_DP/USB_DN. The USB data lines have no ESD protection, which is a real design gap.
- statistics.power_rails lists all five supply domains present in the design. GNDA is the analog ground used in the AFE sheet for the precision measurement circuitry, correctly separated from digital GND.

### Incorrect
- signal_analysis.power_regulators reports U14 with topology='LDO'. The TPS63001 is a TI synchronous buck-boost converter (supports both step-up and step-down). It has two inductor pins (L1, L2), a separate PGND, and a VIN range of 1.8–5.5V with VOUT up to 5V, which is inconsistent with LDO operation. The pin-to-net mapping shows L1 and L2 switch pins present, confirming it is a switching converter.
  (signal_analysis)
- signal_analysis.rf_matching contains two entries: one with antenna='C6' (4p7 cap) and one with antenna='C7' (3p9 cap). The actual antenna is AE1 (Texas SWRA117D 2.4GHz footprint). C6 and C7 are shunt capacitors to GND in the ESP32 RF matching network, with L1 as the series inductor between them and AE1. The detector inverted the topology and double-counted the same pi-network.
  (signal_analysis)
- design_analysis.bus_analysis.spi contains a bus 'IPS' with MOSI=IPS_MOSI (U3.GPIO2) and SCK=IPS_SCK. However, IPS_SCK is connected to R13 and U12 pin 8 (AIN1 — an analog input of the ADS7946 ADC), not a clock pin. The actual display SPI clock goes from the ESP32 to unnamed nets connected to U1 (ST7789V display). This is a spurious SPI bus constructed from an accidental net name prefix match.
  (design_analysis)
- design_analysis.bus_analysis.spi contains bus 'pin_U1' with MOSI=IPS_RST. IPS_RST is the reset line for the ST7789V display (U1), connected to a pull-up resistor and filter cap. It is a control/reset signal, not SPI data. The actual SPI MOSI for U1 goes through IPS_MOSI. The ERC also flags IPS_RST as a no-driver net, confirming it is not a data output.
  (design_analysis)

### Missed
- signal_analysis.buzzer_speaker_circuits reports has_transistor_driver=false and direct_gpio_drive=true for LS1. However, net tracing shows LS1 pin 2 connects to net __unnamed_108 which also connects to Q6 source (AO3400 NMOS). Q6 gate is driven by BUF_ENABLE from U6 (TCA9535 GPIO expander). The speaker is driven through Q6, making has_transistor_driver=false incorrect.
  (signal_analysis)
- signal_analysis.opamp_circuits is empty despite U7 (TLV9062S, dual op-amp) and U8 (OPA2322S, dual op-amp) being present in the AFE sheet as multi-unit amplifier instances. Both use the schematic symbol 'Amplifier_Operational:LTC6081xDD' with type='ic'. The detector likely fails to recognize these components as op-amps due to the library symbol name not matching expected op-amp identifiers. The AFE sheet has a precision analog front-end with multiple op-amp gain stages and buffers.
  (signal_analysis)

### Suggestions
- Fix: TPS63001DRCR (U14) topology reported as 'LDO' but it is a buck-boost converter

---

## FND-00001839: 4-layer stackup correctly identified (F.Cu, In1.Cu, In2.Cu, B.Cu); Single unrouted net CHRG correctly identified between U3 and U13; Thermal pads correctly identified for U3 (ESP32), U14 (TPS63001)...

- **Status**: new
- **Analyzer**: pcb
- **Source**: anotterwatch.kicad_pcb.json.json
- **Created**: 2026-03-24

### Correct
- statistics.copper_layers_used=4 and copper_layer_names=['B.Cu', 'F.Cu', 'In1.Cu', 'In2.Cu']. The gerber files confirm all four inner and outer copper layers are present.
- connectivity.unrouted_count=1 and the unrouted net is 'CHRG' between U3.6 (ESP32 GPIO) and U13.7 (TP4056 charge status). This matches the schematic where the CHRG status signal from the charger IC is intended to connect to the ESP32 but has no route in the PCB.
- thermal_analysis.thermal_pads lists all four exposed-pad QFN/SON packages with nearby via counts: U3 (ESP32 5.3x5.3mm pad, 41 thermal vias), U14 (TPS63001 PVSON, 7 vias), U12 (ADS7946 QFN, 5 vias), U6 (TCA9535 QFN, 5 vias). All are on B.Cu consistent with the back-side dominant placement.
- statistics.front_side=5 and back_side=128, smd_count=127, tht_count=1. This is consistent with a wearable watch design where the display and other front-facing elements are minimal and most electronics are on the back. The density metrics (front 0.2/cm2, back 6.1/cm2) reflect this correctly.

### Incorrect
- The PCB file header reads '(kicad_pcb (version 20171130) (host pcbnew 5.0.2-bee76a0~70~ubuntu18.04.1)'. The analyzer reports kicad_version='unknown' instead of extracting the version from the 'host' field (5.0.2) or mapping file_version 20171130 to KiCad 5. The file_version=20171130 is correctly captured, but the human-readable kicad_version should be 'KiCad 5' or '5.0.2'.
  (kicad_version)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001840: V1.0 gerber set is complete with all 4 copper layers and drill files present; Board dimensions consistent between V1.0 gerbers and PCB file (48.5 x 43.0mm)

- **Status**: new
- **Analyzer**: gerber
- **Source**: gerber_V1.0.json.json
- **Created**: 2026-03-24

### Correct
- completeness.complete=true, completeness.found_layers includes all four copper layers (F.Cu, In1.Cu, In2.Cu, B.Cu) plus F/B Mask, Paste, SilkS, Edge.Cuts. PTH and NPTH drill files are both present. layer_count=4.
- board_dimensions reports width_mm=48.5 and height_mm=43.0, matching the PCB file statistics exactly (board_width_mm=48.5, board_height_mm=43.0). The edge cuts draw count is 21, matching the PCB board_outline.edge_count=21.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001841: V1.1 gerber set complete with 4 copper layers; slightly more vias than V1.0 (296 vs 288); Gerber alignment reported as failed due to F.SilkS width of 89.276mm, which is out-of-board silkscreen

- **Status**: new
- **Analyzer**: gerber
- **Source**: gerber_V1.1.json.json
- **Created**: 2026-03-24

### Correct
- completeness.complete=true. drill_classification.vias.count=296 vs 288 in V1.0, reflecting the incremental routing improvements in revision 1.1 of the gerbers. The PTH drill file confirms 296 via holes at 0.2997mm. All required layers are present.

### Incorrect
- alignment.aligned=false with issue 'Height varies by 2.4mm across copper/edge layers'. The underlying cause is F.SilkS width=89.276mm vs Edge.Cuts width=48.5mm — nearly double the board width. This indicates silkscreen text or graphics extend ~40mm beyond the board edge, which is a real design artifact (likely text placed outside the board during layout). The alignment flag is technically correct but the 2.4mm height variation is separately caused by normal mask/paste shrinkage, not a true misalignment.
  (alignment)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001842: AFE sheet correctly identifies 63 components across 3 power rails (+3.3V, GND, GNDA)

- **Status**: new
- **Analyzer**: schematic
- **Source**: afe.sch.json.json
- **Created**: 2026-03-24

### Correct
- statistics.total_components=63 with power_rails=['+3.3V', 'GND', 'GNDA']. The GNDA rail is used for the precision analog circuitry (REF2915 voltage reference U5, ADS7946 ADC U12, op-amp stages). The component breakdown (8 ICs, 26 resistors, 18 capacitors, 4 transistors, 1 speaker, 1 ferrite bead) matches the source afe.sch content.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
