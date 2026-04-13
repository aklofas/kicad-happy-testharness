# Findings: Ikarthikmb/Circuit-Designs / 1_Breadboard_power_supply_bread power supply schematic

## FND-00000428: Bridge rectifier formed by D1/D2/D3/D4 not detected; design_observations incorrectly reports Vin and Vout1 have no decoupling capacitors; Net 'V-' (negative power rail / GND return) classified as '...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: 1_Breadboard_power_supply_bread power supply schematic.sch.json
- **Created**: 2026-03-23

### Correct
(none)

### Incorrect
- The nets JSON shows C1 pin 2 is on Vin (C1 is a polarized cap, pin 2 is the positive terminal) and C2 pin 2 is on Vout1. Both U1's input and output rails therefore have filter capacitors. Two design_observations fire incorrectly: one 'decoupling' observation listing Vin in rails_without_caps and one 'regulator_caps' observation claiming both input and output capacitors are missing for U1/LM7805.
  (signal_analysis)
- The net named 'V-' carries the bridge rectifier's negative output: it connects D2 cathode, D4 cathode, C1 negative, C2 negative, LED anodes, and all output connector ground pins. This is structurally the ground/return rail of the PSU. It is classified as 'signal' in design_analysis.net_classification. It should be classified as 'ground' or 'power_internal'. Similarly, Vout1 and Vout2 are regulated/switched power outputs but are classified as 'signal'.
  (design_analysis)

### Missed
- D1, D2, D3, D4 (all 1N4007) form a full-wave bridge rectifier: D1A/D3A join at Vin (positive DC rail), D2K/D4K join at V- (negative rail), D1K/D2A and D3K/D4A join the AC input terminals. The signal_analysis.bridge_circuits array is empty. This is a clear bridge rectifier topology that the analyzer should detect.
  (signal_analysis)

### Suggestions
- Fix: Net 'V-' (negative power rail / GND return) classified as 'signal' instead of 'ground'

---

## FND-00000429: Power net '3V3' (distributed via labels) classified as 'signal' instead of a power class

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: 2_Raspberrypi_fs_hat_v01_2-Raspberry Pi FS Hat v01.sch.json
- **Created**: 2026-03-23

### Correct
(none)

### Incorrect
- The label '3V3' is used throughout the schematic as the 3.3 V supply rail — it powers the DHT22 sensor (U1 pin 4 labeled GND connects here, and U1 pin 1 is VCC on 3V3), both LED indicator resistors, the switch pull-up, and is marked with PWR_FLAG. It is classified as 'signal' in design_analysis.net_classification. Since it is flagged by a PWR_FLAG symbol and drives IC power pins, it should be classified as 'power'. Additionally, '3V3' does not appear in statistics.power_rails even though it is the only supply rail other than GND.
  (design_analysis)

### Missed
(none)

### Suggestions
- Fix: Power net '3V3' (distributed via labels) classified as 'signal' instead of a power class

---

## FND-00000430: statistics.total_components reports 7 but the schematic contains 25 component instances; Only 1 of 6 BD249 BJT transistor circuits is reported in transistor_circuits

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: 7_dctodc_dctodc.sch.json
- **Created**: 2026-03-23

### Correct
(none)

### Incorrect
- All components in this schematic are unannotated (Q?, C?, D?, R?, etc.). The analyzer deduplicates by reference string, counting only 7 unique ref designators (one each for Q?, C?, D?, R?, T?, BT?, F?) instead of the 25 actual placed instances: 6x BD249 BJTs, 4x pspice:CAP capacitors, 5x Device:D diodes, 7x Device:R resistors, plus T?, BT?, F? (1 each). The components array correctly contains all 25 entries, but statistics.total_components and statistics.component_types reflect the deduplicated counts, making them severely inaccurate for unannotated schematics.
  (statistics)

### Missed
- The schematic has 6 BD249 NPN BJT instances (all sharing reference 'Q?' due to lack of annotation). The signal_analysis.transistor_circuits array contains only a single entry for 'Q?'. The other five BJT instances are ignored, and their connectivity (base_net, collector_net, emitter_net) is not analyzed. A correct analysis should either report all six instances or make clear that deduplication is occurring.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00000431: pspice:VSOURCE components V1 and V2 misclassified as 'varistor' type; Clapp/Colpitts oscillator topology not detected; reported only as disconnected LC filter pairs

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: Gouriet_clapp_capacitive_oscillator_Gouriet_clapp_capacitive_three_point_oscillator_Gouriet_clapp_capacitive_three_point_oscillator.sch.json
- **Created**: 2026-03-23

### Correct
(none)

### Incorrect
- V1 (5.5 V gate bias) and V2 (30 V drain supply) are pspice:VSOURCE ideal voltage sources used for SPICE simulation — not varistors (voltage-dependent resistors). The analyzer classifies both as type 'varistor' because the lib_id starts with 'pspice:V'. They then erroneously appear in signal_analysis.protection_devices as varistors clamping nets to GND, which is functionally incorrect. They should be classified as 'voltage_source' or 'power_supply' and not appear in protection_devices.
  (signal_analysis)

### Missed
- The circuit is a Gouriet-Clapp capacitive three-point (Colpitts-family) oscillator: IRF740 MOSFET Q1 with tank circuit formed by L1 (200 nH gate-source), L2 (2 µH drain-source), C1 (22 pF), C2 (1 µF), and C3 (100 µF bypass). The analyzer finds three independent LC filter pairs with resonant frequencies but misses the feedback loop connecting drain to gate through the LC network. The oscillator topology is not surfaced in any signal_analysis section.
  (signal_analysis)

### Suggestions
- Fix: pspice:VSOURCE components V1 and V2 misclassified as 'varistor' type

---
