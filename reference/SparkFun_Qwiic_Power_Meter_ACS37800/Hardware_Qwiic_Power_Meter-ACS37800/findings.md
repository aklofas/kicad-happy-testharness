# Findings: SparkFun_Qwiic_Power_Meter_ACS37800 / Hardware_Qwiic_Power_Meter-ACS37800

## FND-00001514: ACS37800 Hall-effect current sensor not detected in current_sense array; I2C pullups on SDA (R7=4.7k) and SCL (R8=4.7k) not detected — has_pullup reports false; Differential pair IP+/IP- correctly ...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: Qwiic_Power_Meter-ACS37800.kicad_sch
- **Created**: 2026-03-24

### Correct
- The design_analysis.differential_pairs correctly identifies IP+ and IP- as a differential pair, associates them with U1 (ACS37800), and marks has_esd: true with U1 as the ESD protection element (the ACS37800 has internal ESD protection on its current sense inputs). The 37-component count and 22 nets match the source schematic and PCB exactly.
- The decoupling_analysis correctly identifies C1 (0.1uF) as the only decoupling capacitor on the 3.3V rail, calculates total_capacitance_uF=0.1, and notes has_bulk: false and has_bypass: true. This is accurate for this design which uses only one bypass cap for the ACS37800.

### Incorrect
- R7 (4.7k) pin1 connects to the SDA net, R7 pin2 connects to JP2 pin3. R8 (4.7k) pin1 connects to the SCL net, R8 pin2 connects to JP2 pin1. JP2 is a 3-pole closed solder jumper whose center pin (pin2) connects to 3.3V. The schematic annotation states 'Cut I2C Jumper to remove pullup resistors from the I2C bus'. Despite this, the analyzer reports has_pullup: false for both SDA and SCL because the pullup path traverses an intermediate unnamed net through the solder jumper.
  (design_analysis)

### Missed
- U1 (ACS37800) is a dedicated power monitoring current sensor IC with IP+/IP- current sense inputs (pins 1-8) and VINP/VINN voltage sense inputs. The signal_analysis.current_sense array is empty despite U1 being the core current-sensing element of this design. The IP+/IP- differential pair is detected correctly in design_analysis.differential_pairs, but the IC's primary function as a current sensor is not reflected in current_sense. The ACS37800 has 'sensor IC' function classification in ic_pin_analysis but this does not propagate to the signal-level current_sense detector.
  (signal_analysis)
- The ACS37800 design uses R3 (8.2k) as a sense resistor between the high-voltage input and VINN, and R9 (1M), R11 (1M) as series input protection/divider resistors to VINP. The schematic text explicitly states 'For 60VDC maximum input, with RSENSE = 8.2kOhms, VINP - VINN will be 245mV'. These resistors form a voltage sensing/divider network on the VINP and VINN inputs. The signal_analysis.voltage_dividers array is empty, missing this voltage measurement front-end network.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00001515: Footprint, via, zone counts and board dimensions correct; High via density on IP+/IP- current-carrying zones correctly captured; Courtyard overlaps between Qwiic connectors and ACS37800 IC correctl...

- **Status**: new
- **Analyzer**: pcb
- **Source**: Qwiic_Power_Meter-ACS37800.kicad_pcb
- **Created**: 2026-03-24

### Correct
- footprint_count=62, via_count=126, track_segments=163, zone_count=5, and net_count=22 all verified against the source KiCad PCB file. Board dimensions 30.48x38.1mm match the source outline exactly. The 5 zones (IP- F.Cu, IP+ F.Cu, GND F.Cu, IP- B.Cu, IP+ B.Cu) are correctly counted.
- The thermal_analysis correctly identifies IP- and IP+ zones spanning both B.Cu and F.Cu with 39 stitching vias each (total 78 zone vias) and high via density (~7.7/cm2). This reflects the deliberate design choice to maximize current-carrying capacity on the ACS37800 current sense bus bars. The GND zone has 35 vias correctly captured. Total zone vias (113) plus signal routing vias (13) equals the 126 via_count.
- The placement_analysis correctly identifies 10 courtyard overlaps including J7/J3/J11/J10 overlapping with U1 (ACS37800) and R3. These reflect the SparkFun design practice of placing Qwiic connectors close to the main IC on this compact board. The overlap detection is accurate.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
