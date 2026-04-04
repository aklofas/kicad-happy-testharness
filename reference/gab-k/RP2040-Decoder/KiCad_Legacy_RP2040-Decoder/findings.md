# Findings: RP2040-Decoder / KiCad_Legacy_RP2040-Decoder

## FND-00001156: Core component extraction correct: 57 components, 4 ICs, 5 MOSFETs, crystal load caps, LDO regulator detected; SPI bus not detected despite W25Q64 flash with CLK/DI/DO/CS nets connected to RP2040; ...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: RP2040-Decoder.kicad_sch
- **Created**: 2026-03-23

### Correct
- Statistics (57 components, 59 nets, 17 caps, 5 transistors, 1 crystal, 1 diode) are accurate. LDO (HT7533S, +V→+3V3), W25Q64 SPI flash with RP2040 memory interface, crystal load cap calculation (8pF effective), decoupling coverage all correctly identified.

### Incorrect
- bus_analysis.spi is empty. The W25Q64 (U3) is connected to RP2040 (U4) via named SPI-role pins (CLK, DI(IO0), DO(IO1), ~CS). The memory_interfaces detector did pick up the pairing (6 shared signal nets), but the dedicated SPI bus detector missed it. Same miss in the USB variant.
  (signal_analysis)
- R5 (6k8) + R7 (1k) form a voltage divider on ADC_EMF_A (GPIO28/ADC2), symmetric to R6/R8 on ADC_EMF_B which was detected. The ADC_EMF_A divider has identical topology and values but was not included in voltage_dividers output. Same miss in the USB variant.
  (signal_analysis)
- The file is KiCad 7 format (version string 20230121 is post-KiCad 6.0). The analyzer correctly reads file_version but fails to infer the KiCad major version, leaving kicad_version as 'unknown'. The USB variant (file_version 20231120) correctly reports '8.0'.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001157: USB-C compliance checker correctly identifies CC pull-downs (5k1), D+/D- series resistors, and two failing checks (VBUS decoupling, VBUS ESD); multi_driver_nets false positive on VBUS: USB-C connec...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: KiCad_USB_RP2040-Decoder.kicad_sch
- **Created**: 2026-03-23

### Correct
- J3 USB_C_Receptacle_USB2.0_16P: cc1_pulldown_5k1 and cc2_pulldown_5k1 pass (R2/R3 = 5k1), dm/dp series resistors pass (R6/R7 = 27Ω). VBUS decoupling fail and VBUS ESD fail are accurate — no decoupling cap on VBUS rail and no TVS present. usb_esd_ic info (optional) is appropriate.
- protection_devices correctly shows D1 as reverse_polarity type, protected_net=VDC, clamp_net=VBUS. D2 (KMB24F flyback/TVS) is in the diode BOM but not flagged as protection — acceptable since KMB24F is a TVS/flyback for the motor driver output and classification as protection would also be reasonable.

### Incorrect
- VBUS is reported as having 4 power_out drivers from J3. This is expected for a USB Type-C 16-pin connector where all VBUS pins are tied together — not a real multi-driver conflict. The analyzer should recognize USB-C connector pin groups as a single source.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001158: U2 thermal pad reported twice with different areas (5.51mm² and 7.95mm²) — duplicate thermal pad detection; Routing completeness correctly reported: 2-layer 25x20mm board, fully routed (0 unrouted)...

- **Status**: promoted
- **Analyzer**: pcb
- **Source**: RP2040-Decoder.kicad_pcb
- **Created**: 2026-03-23

### Correct
- routing_complete=true, unrouted_count=0 consistent with net count. Board dimensions 25x20mm are accurate. DFM tier 'standard' with no violations is plausible for 0.127mm min track and 0.3mm min drill.

### Incorrect
- thermal_analysis.thermal_pads contains two entries for U2 pad '9', one with 5.51mm² and one with 7.95mm². The SOIC-8 BDR6133 custom footprint SOIC-8-1EP has a single exposed pad; the analyzer appears to be detecting both the footprint's internal via-pad polygon and the outer pad boundary as separate thermal pads. Same duplication occurs in the USB PCB for U4.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001159: 4-layer board correctly identified with In1.Cu (power) and In2.Cu (power) inner planes, unrouted net correctly flagged; Tombstoning risk flagged for 0402 bypass capacitors with GND-pour asymmetry —...

- **Status**: new
- **Analyzer**: pcb
- **Source**: KiCad_USB_RP2040-Decoder.kicad_pcb
- **Created**: 2026-03-23

### Correct
- copper_layers_used=4, inner layers typed as 'power' matches the stackup. The one unrouted net (Net-(J2-Pin_1), connecting J2.1 to D2.2) is correctly reported. DFM 'challenging' tier due to 0.05mm annular ring below 0.1mm advanced limit is a real and correct violation.
- Multiple 0402 caps (C10, C11, C12, etc.) flagged at 'medium' risk for thermal asymmetry due to one pad on GND pour. This is a valid DFM concern for 0402 passives in reflow soldering. C1 (crystal load cap) also correctly identified with track width asymmetry (0.127mm vs 0.498mm, ratio 3.9x).

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
