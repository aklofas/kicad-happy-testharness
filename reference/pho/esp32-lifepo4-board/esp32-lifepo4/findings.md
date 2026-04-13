# Findings: pho/esp32-lifepo4-board / esp32-lifepo4

## FND-00002047: TPS709 LDO regulator (U3) not detected in power_regulators; Seven false-positive no_driver ERC warnings for ESP32 I/O nets; CN3058E LiFePO4 charger correctly identified in power_regulators with top...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: schematic_esp32-lifepo4-board_esp32-lifepo4.sch.json.json
- **Created**: 2026-03-24

### Correct
- U2 (CN3058E) is a LiFePO4 battery charger IC. The analyzer found it in power_regulators with topology='unknown', which is appropriate since it does not follow a standard linear or switching regulator pin topology. The associated FB and ISET nets were also correctly captured.

### Incorrect
- U3 is a TPS709 LDO with a power_out pin (VOUT) and is clearly a power regulator, but it does not appear in signal_analysis.power_regulators. Only U2 (CN3058E battery charger) was detected. The TPS709 has a non-standard lib_id ('tps709:TPS709') and pin names VI/VO/GND rather than standard IN/OUT names, which likely caused the regulator detector to miss it. The 3V3 output rail is also misclassified as 'signal' rather than 'power' because there is no power symbol for it in this KiCad 5 schematic.
  (signal_analysis)
- The design_analysis.erc_warnings section reports 7 'no_driver' warnings for nets named IO26, IO25, IO33, IO32, IO35, IO34, and BAT+. In this KiCad 5 schematic the ESP32-WROOM-32 module is used, and the net names reflect the external header (J1/J2) pin numbering. Nets named IO26/IO25 actually carry U1 pins 3V3 and EN respectively — they are mislabeled because KiCad 5 nets are named from labels on the wire, not pin names. The 'no_driver' firing here is a side effect of the net-naming artifact, not actual missing drivers. BAT+ has pin type power_out on U2 (CN3058E) which should satisfy the driver check.
  (design_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00002048: PCB stats correctly reported: 14 footprints, 2 copper layers, fully routed

- **Status**: promoted
- **Analyzer**: pcb
- **Source**: pcb_esp32-lifepo4-board_esp32-lifepo4.kicad_pcb.json.json
- **Created**: 2026-03-24

### Correct
- The PCB analyzer accurately reports 14 footprints (13 real components + 1 REF*** marker matching the schematic), 2-layer design (F.Cu/B.Cu), 68 vias, 495 track segments, and routing_complete=true with 0 unrouted nets. Board dimensions match the gerbers (22.86 x 50.8 mm).

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
