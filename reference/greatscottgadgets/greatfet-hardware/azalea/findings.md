# Findings: greatfet-hardware / azalea_azalea

## FND-00002149: MC4558CPT dual op-amp falsely classified as active_oscillator in crystal_circuits

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: schematic_greatfet-hardware_foxglove_power_supplies.sch.json
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
- The MC4558CPT is a dual bipolar op-amp (STMicroelectronics). It appears in signal_analysis.crystal_circuits with type='active_oscillator'. Op-amps are not oscillators by nature, and this schematic uses the MC4558CPT as a signal buffer/driver, not as an oscillator. The same false positive also appears in foxglove_foxglove.sch.json for the same IC. The crystal_circuits detector is incorrectly triggering on general-purpose op-amp library symbols.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00002150: MCP73831T LiPo charger and PCA9674 I2C expander classified as active_oscillators

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: schematic_greatfet-hardware_jasmine_jasmine.sch.json
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
- jasmine_jasmine.sch.json lists two false positives in crystal_circuits: U1 (MCP73831T, a single-cell LiPo battery charger controller) and U4 (PCA9674, an 8-bit I2C I/O expander). Neither IC has any oscillator functionality. The crystal_circuits detector appears to match on any IC that has an output pin connected to certain net patterns, regardless of whether it is actually an oscillator. These are clear misclassifications.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00002151: TXEN/RXEN GPIO pins of ADF7242 802.15.4 radio falsely detected as UART bus; SPI bus of four ADF7242 802.15.4 radio ICs not detected; ADF7242 802.15.4 radio ICs and SKY13322 RF switch not identified...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: schematic_greatfet-hardware_luckybamboo_luckybamboo.sch.json
- **Created**: 2026-03-24

### Correct
- luckybamboo has four XTAL4PIN crystal references (X1-X4), each with two 18pF load capacitors. All four are correctly detected in crystal_circuits with their two load cap pairs, and the effective load capacitance is computed correctly as 12pF (9pF series + 3pF stray). This demonstrates correct multi-crystal handling for a board with symmetric repeated circuit blocks.

### Incorrect
- The luckybamboo board has four ADF7242 802.15.4 radio transceivers (U1-U4). Each has TXEN_GP5 and RXEN_GP6 pins which are configurable GPIO/RF-enable signals, not UART TX/RX lines. The analyzer detects nets TXEN1-4 and RXEN1-4 as UART buses, producing 8 false UART entries (one TXEN and one RXEN per radio). The devices list is the correct ADF7242 reference but the classification as UART is wrong. These are RF transmit/receive enable control lines.
  (design_analysis)

### Missed
- Each ADF7242 has a 4-wire SPI interface with pins named SO (MISO), SI (MOSI), SCLK (clock), and ~CS~ (chip select). These pins are present in the component data and their types are correctly parsed (bidirectional/input). However, the SPI bus detector produces an empty list. The root cause is that the KiCad 5 legacy parser does not populate the 'net' field on individual component pins — the pin objects have position coordinates but no net assignment, so the bus detector cannot find which net each SPI pin connects to and fails to assemble a bus entry.
  (design_analysis)
- luckybamboo contains four ADF7242 IEEE 802.15.4 2.4 GHz radio transceivers with external XTAL oscillators (X1-X4), HHM2293A1 bandpass filters, BGA7H1H6 RF amplifiers, and a SKY13322 SP3T RF switch. Despite this board being a dense RF subsystem, signal_analysis.rf_chains is empty. The analyzer does classify HHM2293A1/BGA7H1N6/ADF7242 as active_oscillator false positives in crystal_circuits, but produces no rf_chain detection. The board clearly warrants at least one rf_chain entry grouping the transceiver, filter, amplifier, and switch per channel.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00002152: GND and VCC power nets falsely reported as I2C SCL/SDA bus lines

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: schematic_greatfet-hardware_narcissus_narcissus.sch.json
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
- The narcissus I2C bus analysis contains four entries. Two are correct (I2C0_SCL and I2C0_SDA with PCA9698 devices). Two are false positives: GND is reported as an I2C SCL line with 15 connected devices, and VCC is reported as an I2C SDA line with 9 devices. Investigation shows that U1 and U2 (PCA9698 40-bit I2C expanders) have address/reset pins named SCL and SDA in the library symbol that happen to connect to GND and VCC. The I2C detector picks up these pin names regardless of whether the net is a power rail, creating nonsensical entries.
  (design_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00002153: USB differential net USB1_D+ falsely classified as I2C SCL line

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: schematic_greatfet-hardware_azalea_azalea.sch.json
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
- azalea_azalea.sch.json reports four I2C bus entries. Two are legitimate (I2C0_SDA and I2C0_SCL on the LPC4330 MCU). The other two are false positives: the net 'USB1_D+' is reported as SCL for U1 (LPC4330FBD144), and 'P2_4' is reported as SDA. USB1_D+ is a USB full-speed/high-speed differential signal and has nothing to do with I2C. This false positive likely occurs because the LPC4330 has multiplexed pins where the USB D+ pin's KiCad symbol pin name contains 'SCL' as an alternate function label.
  (design_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00002154: nRF24L01+ chip-select (CSN) and enable (CE) pins falsely detected as both I2C bus and duplicate SPI bus

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: schematic_greatfet-hardware_crocus_crocus.sch.json
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
- The crocus board uses a nRF24L01+ SPI 2.4 GHz radio (U1) and a PCA9674 I2C expander (U2). The correct SPI bus (bus_id=0) is detected with MOSI/MISO/SCK. However a spurious second SPI bus (bus_id='pin_U1') is also emitted where MOSI=CSN (the nRF chip select) and MISO=CE (the chip enable), which are not data lines. Separately, the I2C detector produces two false entries: CSN reported as SCL for both U1 and U2, and IRQ reported as SDA for both. These pin names (CSN, IRQ, CE) do not indicate I2C functionality.
  (design_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00002155: Analog signal net 'RXIN' (RF receive input) falsely detected as UART receiver net; RF matching network detector misidentifies all signal-chain filter inductors as antenna matching networks

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: schematic_greatfet-hardware_gladiolus_gladiolus.sch.json
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
- gladiolus is a software-defined radio (SDR) front-end board with an AD9283 8-bit 50MSPS ADC, AD9704 8-bit 175MSPS DAC, and analog signal conditioning (AD8330 VGA, THS4520 differential opamp). The net named 'RXIN' is the RF/analog receive input signal, connected to diodes, resistors, and a capacitor for ESD/filtering. Its net_classification is 'data'. However, the UART detector flags it as a UART RX line with 6 pin connections. This is a pattern-matching false positive on the substring 'RX' in the net name.
  (design_analysis)
- gladiolus has 10 inductors (L1-L10) forming anti-aliasing and reconstruction filters for the ADC/DAC signal paths, along with 3 capacitors (C9, C10, C14-C16). The rf_matching detector produces 6 separate matching network entries, treating each inductor as an 'antenna' component with all adjacent L/C components as its matching network. These are not antenna matching networks — they are multi-section LC bandpass/lowpass filters for the 50MSPS ADC input and 175MSPS DAC output. The inductor values (1-2.2uH) and resonant frequencies (9-33 MHz) are consistent with signal filtering, not antenna matching.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00002156: Graceful handling of an empty/stub KiCad 5 schematic with only a header line

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: schematic_greatfet-hardware_wiggler_wiggler.sch.json
- **Created**: 2026-03-24

### Correct
- wiggler.sch contains only a single line ('EESchema Schematic File Version 2') with no components, nets, or wires. The analyzer returns a valid JSON structure with all counts at zero and empty arrays for all analysis sections, with no crash or error. This confirms correct edge-case handling of effectively empty legacy schematics.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
