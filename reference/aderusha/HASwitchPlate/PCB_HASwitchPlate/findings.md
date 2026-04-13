# Findings: aderusha/HASwitchPlate / PCB_HASwitchPlate

## FND-00000590: Component count (8), type breakdown, and power rail detection are accurate; Net label tracing bug: LCD_TX/LCD_RX labels not resolved to J2 connector pins in KiCad 5 legacy format; Reset pin observa...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: PCB_HASwitchPlate.sch.json
- **Created**: 2026-03-23

### Correct
- 8 components (3 ic, 3 connector, 1 transistor, 1 resistor), power rails +3.3V/+5V/GND, and all footprints correctly extracted. BOM accurately lists all 8 unique parts with correct footprints and datasheets.
- Q1 base=LCD_CTL, collector=GND, emitter=LCD_GND is an unusual but real topology (LCD backlight ground switch). The analyzer correctly identifies: type=bjt, load_type=connector (LCD connector on emitter side), base_resistors=[R1 1k]. The collector_is_power=true and emitter_is_ground=true flags are consistent with the actual net assignments.
- The schematic has no capacitors at all; the WeMos module is powered directly from the IRM-03-5 without local decoupling. The design_observations entry for U2 correctly lists both rails as rails_without_caps.

### Incorrect
- LCD_TX and LCD_RX net labels appear in the schematic connecting U2 (WeMos D1, D0) to J2 (RX, TX pins). The output shows LCD_TX and LCD_RX as single-device nets (only U2), while J2.RX and J2.TX land on anonymous nets __unnamed_9 and LCD_GND respectively. The KiCad 5 legacy parser is not correctly associating the text label coordinates with the wire endpoints at J2, causing the UART signals to appear disconnected from the display connector.
  (signal_analysis)
- The design_observations entry for U2 (WeMos mini) RST pin says 'net': '+3.3V', 'has_pullup': false. RST is wired directly to the +3.3V rail, which constitutes a pull-up connection. The analyzer should detect a named power rail connected to a reset pin as a pull-up. Reporting false is incorrect and misleading.
  (signal_analysis)

### Missed
- U1 is a MeanWell IRM-03-5, a 3W AC/DC module (5V output). U3 is a MeanWell SLC03-series isolated DC/DC converter. Neither appears in signal_analysis.power_regulators. The detector likely only recognizes regulators by lib_id keywords (LDO, VREG, etc.) and misses custom-library AC/DC and DC/DC modules. These are the primary power supply components of the design.
  (signal_analysis)

### Suggestions
(none)

---
