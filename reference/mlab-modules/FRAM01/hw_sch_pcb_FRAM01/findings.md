# Findings: mlab-modules/FRAM01 / hw_sch_pcb_FRAM01

## FND-00000550: Component inventory and BOM extraction accurate; SPI bus detected correctly; Decoupling capacitors correctly identified on +3.3V rail; PWR_FLAG warnings are false positives — schematic has explicit...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: hw_sch_pcb_FRAM01.kicad_sch.json
- **Created**: 2026-03-23

### Correct
- All 12 components parsed correctly (IC1, D1, J1, J2, C1, C2, M1-M4, FID1-FID2). BOM types, values, footprints, and MPN for IC1 are all correct.
- bus_analysis.spi contains one bus with MISO, MOSI, SCK signals and 1 chip-select, full_duplex mode. IC1 (CY15B108QN-40SXI FRAM) correctly identified as the SPI device.
- C1 (10uF) and C2 (100nF) both associated with IC1's VDD pin; decoupling_analysis total_capacitance_uF=10.1 is correct.

### Incorrect
- pwr_flag_warnings fires for both +3.3V and GND, but the schematic explicitly places two PWR_FLAG symbols (#FLG01 at 252.73,24.13 and #FLG02 at 252.73,36.83) on those nets. The analyzer failed to count the PWR_FLAG power_out pin as satisfying the requirement.
  (signal_analysis)
- ~{CS}, ~{WP}, MOSI, SCK all flagged as 'no output driver' but these are driven externally through J2 (the SPI header connector). This is expected for a peripheral breakout module where the host MCU is not on this schematic. The warnings pollute ERC output without actionable signal.
  (signal_analysis)
- D1 value is 'BZT52H-C3V6,115' which is the Nexperia part number. The analyzer reports D1 in missing_mpn because there is no Manufacturer_Part_Number property, but the value itself is unambiguously the MPN. The analyzer could extract the MPN from the value field for diodes using the part number pattern.
  (signal_analysis)

### Missed
- D1 (BZT52H-C3V6,115) is a 3.6V Zener diode connected between +3.3V and GND — a classic overvoltage clamp for a 1.8–3.6V supply rail. signal_analysis.protection_devices is empty; this should appear as a TVS/Zener protection finding.
  (signal_analysis)
- IC1 is a CY15B108QN-40SXI SPI FRAM (8Mbit non-volatile memory). signal_analysis.memory_interfaces is empty. The analyzer detected SPI bus but did not classify this as a memory interface.
  (signal_analysis)

### Suggestions
(none)

---
