# Findings: designer2k2/2d-xmas-tree / pcb-kicad_2D_xmas_tree01

## FND-00000314: I2C bus falsely detected on ATtiny25 ISP RESET and charlieplexing GPIO lines; Decoupling observation correct but misleading: C1 exists between VCC and GND but has no specified value; Charlieplexing...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: pcb-kicad_2D_xmas_tree01.sch.json
- **Created**: 2026-03-23

### Correct
- The design_observations entry reports U1 (ATTINY25-20SU) has rails_without_caps=['VCC'] and rails_with_caps=[]. C1 (Device:C) IS physically connected between the VCC net (pin 2) and GND net (pin 1), so a decoupling capacitor is present. However, C1's value field is just 'C' with no numeric capacitance specified, so ctx.parsed_values returns None for C1 and the detect_decoupling function skips it. The observation is technically accurate given the unspecified value, but the design does have a decoupling cap in place — it simply lacks a value annotation. This is a limitation of the value-based detection approach rather than an error.

### Incorrect
- The bus_analysis reports an I2C bus with RESET net as SDA and __unnamed_1 as SCL. The ATtiny25 PB0 pin name string includes 'SDA' as an alternate function ('PB0(MOSI/DI/SDA/AIN0/...)') and PB2 includes 'SCL' ('PB2(SCK/USCK/SCL/T0/...)'), triggering the I2C detector. However, neither is used for I2C: RESET is the ISP programming reset line (net label explicitly named RESET, connected to J1 ISP pin 1 and R6 pull-up), and __unnamed_1 is one of the five ATtiny25 GPIO charlieplexing drive lines (connected to R4 75-ohm current limiter). R6 (10k to VCC) is a standard RESET pull-up resistor, not an I2C SDA pull-up. The I2C detection is wholly a false positive caused by the ATtiny25 multi-function pin name strings.
  (design_analysis)

### Missed
- This design is a 20-LED charlieplexed Christmas tree driven by an ATtiny25. Five GPIO pins (PB0-PB4 via R1-R5 75-ohm current limiters) drive 20 LEDs (D1-D20) in a classic charlieplexing matrix topology (each resistor line connects to pairs of anti-parallel LEDs sharing a bus). This is the entire circuit's main function, yet no signal_analysis detector recognizes charlieplexing. The LEDs appear as 7 unnamed signal nets with multiple anti-parallel LED pairs, but no structured charlieplex pattern is reported. No existing detector category covers this topology.
  (signal_analysis)

### Suggestions
(none)

---
