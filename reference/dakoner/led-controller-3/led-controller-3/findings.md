# Findings: led-controller-3 / led-controller-3

## FND-00002376: SPICE DC voltage sources V1/V2 misclassified as varistors; SPI bus false positive on ESP32 internal flash pins; Missed detection that this is an early-stage/incomplete design with minimal connections

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: schematic_led-controller-3_led-controller-3.kicad_sch.json.json
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
- V1 and V2 are 'Simulation_SPICE:VDC' symbols (DC voltage sources for SPICE simulation, values '5' and '24'). The analyzer classified them as type 'varistor' based on the 'V' reference prefix. They appear in statistics.component_types.varistor (count 2), in signal_analysis.protection_devices as varistors clamping VDD/VCAM rails, and in missing_footprint (correctly noted they have no footprint). These are simulation-only components, not real protection devices.
  (statistics)
- The analyzer detected an SPI bus (bus_id 'pin_U1') on the ESP32's SDO/SDI/CLK pins. These are the ESP32's internal SPI flash interface pins (CMD, SD2, SD3, CLK, SDO, SDI), all of which are placed as no-connects in the schematic (30 total no_connects). There is no external SPI device connected. The SPI detection triggers only because the pin names match SPI signal patterns, not because a real external SPI bus is present.
  (design_analysis)

### Missed
- The ESP32 (U1) has 38 pins but only 4 meaningful nets: VDD (5V), GND, and two GPIO pins (GPIO13, GPIO25) going to a 2-pin connector (J2). GPIO32 and GPIO33 go nowhere (single-pin nets not on connector). 30 of 38 pins are no-connects. The analyzer does not flag this as an incomplete design or raise any design_observation about the extremely high no-connect ratio (~79%). The connectivity_issues.single_pin_nets list is empty despite GPIO32/GPIO33 apparently being single-pin nets in the schematic.
  (signal_analysis)

### Suggestions
(none)

---
