# Findings: tjhorner/bizcard / pcb_bizcard

## FND-00001993: RP2040 PCB business card: all major circuits correctly detected — LDO, crystal, WS2812B chain, W25Q128 flash, buzzer, decoupling; WS2812B addressable LED chain correctly detected: chain_length=4, d...

- **Status**: new
- **Analyzer**: schematic
- **Source**: bizcard.kicad_sch
- **Created**: 2026-03-24

### Correct
- The analyzer correctly identifies: AMS1117-3.3 LDO (VBUS→+3V3), 12MHz crystal with 30pF load caps (effective load 18pF), 4-LED WS2812B addressable chain on GPIO24, W25Q128JVS flash connected to RP2040 via QSPI (6 shared nets, memory_interfaces entry), CUI CPT-9019S buzzer on GPIO3, and comprehensive decoupling on +1V1 (1.2µF), +3V3 (11.8µF), and VBUS (10.4µF) rails.
- The 4-LED WS2812B chain (D1–D4) is correctly identified with chain_length=4, first_led=D1, last_led=D4, data_in_net=GPIO24, protocol='single-wire (WS2812)', led_type=WS2812B, and estimated_current_mA=240mA. The fifth LED (D5) is a plain LED status indicator correctly classified separately.
- The memory_interfaces section correctly identifies W25Q128JVS (U2) connected to RP2040 (U3) with 6 shared signal nets (QSPI_SCLK, QSPI_SS, QSPI_SD0–SD3). This is properly captured even though the QSPI bus does not appear as a standard SPI bus in bus_analysis, which is appropriate since QSPI uses a dedicated naming scheme.
- The design_observations correctly identify USB_D+ and USB_D- nets with R4 and R5 (27 ohm series resistors, standard for RP2040 USB) and correctly notes has_esd_protection=false. The RP2040 has internal USB transceivers so this is expected for this design.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001994: Bizcard PCB correctly reports 49 footprints, RP2040 (70 pads), 88.9mm x 50.8mm credit-card form factor, routing complete; Courtyard overlaps between J2 (USB-C) and R6/R7 (CC resistors) correctly de...

- **Status**: new
- **Analyzer**: pcb
- **Source**: bizcard.kicad_pcb
- **Created**: 2026-03-24

### Correct
- The 49 footprint count (45 schematic components + 4 board-only items) is plausible. The RP2040 QFN-56 is correctly identified with 70 pads (56 signal + thermal/EP). Board dimensions 88.9mm x 50.8mm (standard credit card) are correct. Routing is complete with 31 vias and 362 track segments.
- The placement_analysis correctly identifies two courtyard overlaps: J2 vs R6 (0.522mm²) and J2 vs R7 (0.522mm²). R6 and R7 are the 5.1k CC pull-down resistors placed close to the USB-C receptacle, which commonly results in courtyard violations in tight designs. The edge clearance warning for J2 (0.86mm) is also appropriate.
- 22 tombstoning risk entries are reported for 0402 capacitors where one pad connects to GND (ground zone) and the other to a signal/power net. This is a genuine thermal asymmetry risk for 0402 reflow assembly when a GND pour is present on only one pad. All flags are medium risk which is appropriate for standard manufacturing.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
