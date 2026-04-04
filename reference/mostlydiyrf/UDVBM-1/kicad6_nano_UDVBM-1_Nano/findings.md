# Findings: UDVBM-1 / kicad6_nano_UDVBM-1_Nano

## FND-00001609: kicad_version reported as 'unknown' instead of '6' for all three schematics; Capacitor value '0.10' parsed as 0.1 Farads (100 MF) instead of 100 nF (0.1 uF); LM7805 classified as topology='LDO' but...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: kicad6_pro-mini_UDVBM-1.kicad_sch
- **Created**: 2026-03-24

### Correct
- pro-mini: 37 total components (3 IC, 13 connector, 14 cap, 1 diode, 1 resistor, 1 inductor, 4 mounting holes), 35 nets, 3 no-connects — all confirmed correct from source. Nano: 39 total components (3 IC, 14 connector, 15 cap, 1 diode, 1 resistor, 1 inductor, 4 mounting holes), 37 nets — correct. Xiao: 29 total components (4 IC, 8 connector, 10 cap, 1 diode, 1 resistor, 1 inductor, 4 mounting holes), 26 nets, 4 no-connects — correct. BOM excludes mounting holes in all three: 33, 35, and 25 BOM entries respectively.
- All three designs have I2C (SDA/SCL) without pull-up resistors — only R1=10 ohm exists in each design and it is used as a power filter resistor, not an I2C pull-up. The bus_analysis correctly reports has_pull_up=false and pull_ups=[] for both SDA and SCL in all three designs. Pro-mini: U1+U2 on I2C. Nano: U1+U2 on I2C. Xiao: U1+U3+U4 on I2C (correctly including M24C08 EEPROM).
- All three designs are missing PWR_FLAG symbols on GND (and additionally +3.3V, +5V for xiao). The pwr_flag_warnings correctly identifies these missing flags. Pro-mini and nano report GND only. Xiao reports +3.3V, +5V, and GND — all correct since no PWR_FLAG symbols are placed in any of the designs. These will cause KiCad ERC errors.

### Incorrect
- All three schematic files contain '(kicad_sch (version 20211123) (generator eeschema)'. The file_version field correctly captures '20211123', but kicad_version is set to 'unknown' instead of deriving '6' from the generator/version combination. This applies to pro-mini, nano, and xiao variants.
  (kicad_version)
- C1, C3, C4, C6-C10, C12-C14 all have value='0.10' with footprint Capacitor_THT:C_Disc_D5.0mm_W2.5mm_P2.50mm — a disc ceramic/film capacitor. The analyzer parses '0.10' as 0.1 Farads, yielding parsed_value=0.1, farads=0.1 in decoupling_analysis and pdn_impedance. The correct interpretation is 100 nF (0.1 uF = 1e-7 F). This causes downstream errors: total_capacitance_uF=1100000 (should be ~1.1 uF for 11 caps), self_resonant_hz=15915 Hz (should be ~15.9 MHz for ceramic), and caps are classified as 'electrolytic/tantalum' in PDN analysis instead of 'ceramic'. The same error affects nano (12 caps, total_capacitance_uF=1200000) and xiao (7 caps, total_capacitance_uF=600000).
  (signal_analysis)
- U3 (LM7805) in pro-mini and nano designs is reported as power_regulators[].topology='LDO'. The LM7805 is a 78xx-series fixed positive voltage regulator with ~2V minimum input-output differential — it is explicitly NOT an LDO (Low Dropout Regulator, which requires <1V dropout). The correct topology label should be 'linear' or 'fixed_linear'. This also propagates to the power_budget regulator entry. The AZ1117-3.3 in xiao is correctly identified as 'LDO'.
  (signal_analysis)

### Missed
- All three designs include a '1wire' net and connectors labeled 'One-Wire Port 1' and 'One-Wire Port 2' (pro-mini: J5, J13; nano: J5, J13; xiao: '1wire' net). The bus_analysis section contains i2c, spi, uart, and can keys but has no one_wire entry. The net_classification maps '1wire' to 'signal' rather than recognizing it as a 1-Wire bus signal. This is a missed detection across all three schematic variants.
  (design_analysis)

### Suggestions
- Fix: LM7805 classified as topology='LDO' but it is a standard 78xx linear regulator

---

## FND-00001610: Cross-domain signals SCL/SDA incorrectly flagged as crossing +3.3V and +5V power domains

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: UDVBM-1_Nano.kicad_sch
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
- design_analysis.cross_domain_signals reports SCL and SDA as crossing +3.3V and +5V domains between U1 (Si5351A) and U2 (Arduino_Nano). However, U1's VCC is on +5V (confirmed via ic_pin_analysis: pin 6 Vin connects to +5V net), and U2 operates its I2C at 5V. The +3.3V appears in U2's power_rails because the Arduino Nano has a 3.3V power_out pin (pin '3.3V', type=power_out) — it generates +3.3V as an output, not as its I/O supply. The analyzer includes power_out pins when building IC domain membership, causing the false cross-domain detection. The connectivity_issues correctly reports +3.3V as a single_pin_net connected only to U2's output pin.
  (design_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001611: Xiao design correctly identifies 4 ICs including AZ1117-3.3 LDO, M24C08 EEPROM, Si5351A clock gen, and Seeed XIAO module; LC power supply filter correctly detected at 339 Hz resonance for 1mH + 220...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: kicad6_xiao_UDVBM-1_Xiao.kicad_sch
- **Created**: 2026-03-24

### Correct
- U1=Si5351A_Adafruit (7-pin clock generator), U2=AZ1117-3.3 (3.3V LDO, correctly detected with estimated_vout=3.3, input_rail and output_rail=+3.3V), U3=M24C08-RMN (EEPROM, function='EEPROM', correctly placed on I2C bus with SDA/SCL), U4=Seeed_XIAO (MCU module). Power domain correctly shows all on +3.3V. AZ1117 LDO topology correctly identified. M24C08 EEPROM function detection is correct.
- The power supply CLC filter consisting of L1=1.0mH and C5/C11=220uF each is correctly analyzed. Resonant frequency f = 1/(2π√(LC)) = 1/(2π√(0.001×0.000220)) = 339.32 Hz is mathematically correct. Impedance at resonance = √(L/C) = √(0.001/0.000220) = 2.13 ohms is also correct. Two LC filter instances are reported (L1+C11 and L1+C5) sharing the inductor, which correctly models the pi-filter topology.

### Incorrect
- In pdn_impedance.rails.+3.3V (and +5V), capacitors C1, C2, C6, C7, C9, C10, C11 with value='0.10' and footprint Capacitor_THT:C_Disc_D5.0mm_W2.5mm_P2.50mm are assigned type='electrolytic/tantalum' with esr_ohm=0.1, esl_nH=7.5, and srf_hz=5812 Hz. Disc capacitors are ceramic or film, not electrolytic/tantalum. The misclassification appears to stem from the same root cause as finding #2: the parser treats '0.10' as 0.1 Farads (a value more consistent with electrolytic caps), triggering the wrong cap-type heuristic. A true 100nF ceramic disc cap would have esr<0.1 ohm, esl~1nH, and SRF~15 MHz.
  (pdn_impedance)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001612: Xiao PCB statistics are accurate: 35 footprints (3 SMD, 25 THT), 2-layer board, fully routed; Xiao PCB has C8 but the xiao schematic has C9 — schematic-PCB net list is out of sync

- **Status**: promoted
- **Analyzer**: pcb
- **Source**: kicad6_xiao_UDVBM-1_Xiao.kicad_pcb
- **Created**: 2026-03-24

### Correct
- PCB source confirms 35 footprints: U2 (TO-252-2 SMD), U3 (SO-8 SMD), U4 (Seeed_XIAO, attr=smd) = 3 SMD; U1 (Si5351A, attr=through_hole), all THT passives and connectors = 25 THT; 6 graphics logos (G*** refs) and 1 footprint unaccounted. Board dimensions 86.944x39.751mm, fully routed (0 unrouted), GND pour on both layers with thermal vias for U2 correctly detected.

### Incorrect
- The xiao schematic lists capacitors C1, C2, C3, C4, C5, C6, C7, C9, C10, C11 (no C8). The xiao PCB has C1, C2, C3, C4, C5, C6, C7, C8, C10, C11 (no C9). This is a genuine schematic-PCB mismatch — a capacitor was renumbered in one file but not the other. The analyzer does not flag this cross-file discrepancy. This is a design documentation issue, not an analyzer parsing error, but worth noting as an observation about the design state.
  (statistics)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001613: Pro-mini PCB correctly analyzed as a multi-instance panel board with 266 footprints and 3 unrouted nets

- **Status**: new
- **Analyzer**: pcb
- **Source**: kicad6_pro-mini_UDVBM-1.kicad_pcb
- **Created**: 2026-03-24

### Correct
- The pro-mini PCB is a template/panel board with multiple copies of circuit blocks: 42 capacitors (C1-C42), 9 U-refs, 12 H-refs, 18 G*** graphics. The 266-footprint count correctly reflects the actual PCB file (confirmed: 266 footprint instances in source). The 3 unrouted nets (Net-(U1-Pad0/1/2) corresponding to Si5351A clock outputs with 3 instances each: U1/U4/U7) are correctly identified.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001614: Nano PCB DFM correctly flags board size exceeding 100x100mm JLCPCB threshold

- **Status**: new
- **Analyzer**: pcb
- **Source**: UDVBM-1_Nano.kicad_pcb
- **Created**: 2026-03-24

### Correct
- Nano PCB is 126.9x51.2mm, which correctly triggers a DFM violation: 'Board size 126.9x51.2mm exceeds 100x100mm — higher fabrication pricing tier at JLCPCB'. The dfm_tier='standard' and violation_count=1 are correct. The xiao board (86.944x39.751mm) has no DFM violations, which is also correct.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001929: Component count, bus detection (I2C, SPI), and power regulator detection all correct; LM7805 incorrectly classified as topology='LDO'; should be 'linear' (standard fixed regulator); Capacitor value...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: repos_UDVBM-1_kicad6_pro-mini_UDVBM-1.kicad_sch
- **Created**: 2026-03-24

### Correct
- 37 components correctly parsed. LM7805 (U3) correctly identified as power regulator. I2C bus on SDA/SCL with devices U2 (ArduinoPro_Mini) and U1 (Si5351A) correctly detected. SPI bus with MOSI/MISO/SCK detected on U2. Missing I2C pull-up resistors correctly flagged (no pull-up R on SDA/SCL in this schematic — the design relies on module-level pull-ups). Reset pin observation for U2.RST is substantively correct.

### Incorrect
- U3 (value='LM7805', lib_id='UDVBM-1-rescue:LM7905_TO220-Regulator_Linear') is classified as topology='LDO'. The LM7805 is a classic 3-terminal fixed positive voltage regulator with a minimum dropout of ~2V — it is definitively NOT a low-dropout regulator. LDO refers to regulators with dropout <1V (e.g., LM1117, AZ1117, MCP1700). The correct topology for LM7805 is 'linear'. Note also the lib_id references 'LM7905' (negative voltage version) while the value is 'LM7805' — this discrepancy in the source is not flagged.
  (signal_analysis)
- The schematic uses '0.10' as the value string for disc ceramic capacitors (C1, C3, C4, C6–C10, C12–C14), meaning 0.10 µF = 100 nF. The value parser interprets '0.10' as a bare decimal = 0.1 F (farads), then converts to 1.0×10⁵ µF per cap. With 11 such caps on +5V, total_capacitance_uF = 1,100,000 µF (≈1.1 F). The self_resonant_hz of 15,915 Hz (instead of ~15.9 MHz for 100 nF) confirms the wrong unit interpretation. The correct total should be ~1.1 µF. Same bug affects nano (1,200,000 µF for 12 caps) and xiao variants.
  (signal_analysis)
- design_observations includes {category: 'regulator_caps', component: 'U3', missing_caps: {input: '__unnamed_0'}}. However, C2 (10 µF electrolytic) appears in the nets dict for '__unnamed_0' alongside U3 and R1. The false positive occurs because U3 and C2 have pins=None in the parsed output (net membership is known but pin-level connections are not), so the cap-checking logic cannot confirm that C2 is a bypass cap for U3. Same false positive appears in nano variant for U3, and xiao for U2 (AZ1117-3.3).
  (signal_analysis)
- signal_analysis.design_observations contains two identical entries for {category: 'reset_pin', component: 'U2', value: 'ArduinoPro_Mini', pin: 'RST', net: 'RST', has_pullup: False, has_filter_cap: False, connected_components: [{ref: 'J3'}, {ref: 'J2'}]}. The same duplication occurs in the nano variant. The substance of the observation (no pull-up, no filter cap, reset connected to breakout headers) is correct, but it should appear only once.
  (signal_analysis)
- All .kicad_sch (file_version 20211123 = KiCad 6.0) and .kicad_pcb (file_version 20211014 = KiCad 6.0) files report kicad_version='unknown'. The file version numbers are sufficient to determine the KiCad generation: 20211123 and 20211014 correspond to KiCad 6.0 release. Also affects .kicad_pcb files from KiCad 5 (file_version 20171130) — those also report 'unknown'. Only legacy .sch files get correct version detection ('5 (legacy)'). The PCB analyzer should map known file_version ranges to KiCad major versions (e.g., 20171130=KiCad5, 20211014=KiCad6).
  (kicad_version)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001930: Routing incompleteness correctly detected; 3 unrouted nets identified with pad-level detail; PCB footprint count (266) reflects panelized multi-module design

- **Status**: new
- **Analyzer**: pcb
- **Source**: repos_UDVBM-1_kicad6_pro-mini_UDVBM-1.kicad_pcb
- **Created**: 2026-03-24

### Correct
- routing_complete=false with unrouted_net_count=3 correctly identified. Unrouted nets are Net-(U1-Pad0), Net-(U1-Pad1), Net-(U1-Pad2), each connecting 3 pads across U1/U4/U7. This is correct — the pro-mini design is a panelized board with multiple module placeholders and the design was never fully routed. Board dimensions 135.6×180.3mm correctly reported; DFM correctly flags the board as exceeding 100×100mm pricing threshold.
- The pro-mini PCB contains 266 footprints vs 37 in the schematic. This is a multi-module panel: 9 U references (U1–U9), multiple REF markers (96), graphic elements. The PCB is a combination of the main board with repeated module areas. The analyzer correctly processes the file without error.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001931: Nano PCB fully routed, correct dimensions and layer usage

- **Status**: new
- **Analyzer**: pcb
- **Source**: repos_UDVBM-1_kicad6_nano_UDVBM-1_Nano.kicad_pcb
- **Created**: 2026-03-24

### Correct
- 74 footprints, 2-layer board, routing_complete=true, 0 unrouted nets. Board 126.9×51.2mm. 252 track segments, 167 vias, 3 zones. Mix of 32 SMD + 39 THT footprints (consistent with THT capacitors and connectors visible in schematic). The nano variant is a compact single-row form factor.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001932: Xiao variant correctly identifies AZ1117-3.3 LDO with estimated output voltage

- **Status**: new
- **Analyzer**: schematic
- **Source**: repos_UDVBM-1_kicad6_xiao_UDVBM-1_Xiao.kicad_sch
- **Created**: 2026-03-24

### Correct
- U2 (AZ1117-3.3) correctly identified: topology='LDO', output_rail='+3.3V', estimated_vout=3.3, vref_source='fixed_suffix'. The Xiao uses both +5V and +3.3V rails. 4 ICs detected: Si5351A (clock gen), AZ1117-3.3 (LDO), Seeed_XIAO (MCU module), M24C08-RMN (EEPROM). I2C bus on SDA/SCL with 3 devices (U1/U4/U3) correctly found.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001933: Xiao PCB: compact fully-routed 2-layer board with correct stats

- **Status**: new
- **Analyzer**: pcb
- **Source**: repos_UDVBM-1_kicad6_xiao_UDVBM-1_Xiao.kicad_pcb
- **Created**: 2026-03-24

### Correct
- 35 footprints, 2-layer board, routing_complete=true. Board 86.9×39.8mm. 198 tracks, 117 vias, 5 zones. 3 SMD + 25 THT footprints (Seeed_XIAO is SMD module, rest THT). Net count 23 consistent with Xiao schematic 26 nets (small differences due to PCB-only power nets).

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001934: Analyzer correctly processes UDVBM-1_Nano.kicad_pcb copy stored in xiao/ directory

- **Status**: new
- **Analyzer**: pcb
- **Source**: repos_UDVBM-1_kicad6_xiao_UDVBM-1_Nano.kicad_pcb
- **Created**: 2026-03-24

### Correct
- The xiao subdirectory contains a copy of UDVBM-1_Nano.kicad_pcb (identical content to nano/UDVBM-1_Nano.kicad_pcb, 74 footprints, 126.9×51.2mm). The analyzer processes the file at its actual path without error. This is a design repo artifact, not an analyzer issue.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
