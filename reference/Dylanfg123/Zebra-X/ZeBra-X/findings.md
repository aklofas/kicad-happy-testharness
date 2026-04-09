# Findings: Dylanfg123/Zebra-X / ZeBra-X

## FND-00002539: Xilinx Zynq-7010 FPGA/SoC demo board with 1 GB DDR3L (2x MT41K256M16TW), Gigabit Ethernet (RTL8211F RGMII), USB 2.0 HS (USB3320C ULPI PHY), FTDI JTAG/UART debug (FT2232HL), QSPI boot flash (W25Q128), eMMC, and mezzanine expansion. The analyzer correctly identifies 424 components, 4 SY8003ADFC switching regulators, feedback networks, JTAG debug, SDIO bus, DDR differential pairs, USB pairs, LEDs, and decoupling. However, it misses the RTL8211F Ethernet PHY RGMII interface (39 ETH nets), the DDR3L memory interface (84 DDR nets), clock distribution (4 oscillators), QSPI flash bus, and ULPI bus. 3 of 4 oscillators are misclassified as connectors, TPS2051C is classified as LDO instead of load switch, power tree shows all regulators at sequence_order=0 despite actual PG cascade, and Zynq power_domains lists only +3V3 instead of 7 rails.

- **Status**: confirmed
- **Analyzer**: schematic
- **Source**: ZeBra-X.kicad_sch.json
- **Created**: 2026-04-09

### Correct
- All 4 SY8003ADFC switching regulators (U101-U104) correctly identified with correct input (+5V) and output rails (+1V0, +1V8, +1V35, +3V3)
- Feedback networks correctly identified for all 4 switchers with accurate Vref=0.6V (lookup), resistor values, and computed output voltages
- JTAG debug interface at J300 correctly detected with all 4 signals and status=pass
- Voltage divider R400/R401 (12K/12K) generating MIO_VREF_0V9 correctly detected
- RC filter R903/C905 (12K/4u7) correctly detected as 2.82 Hz low-pass on USB_HS_VBUS_FILT
- SDIO bus correctly identified connecting U200 and U403 (eMMC) with pullup detection
- DDR differential pairs correctly detected for CK, DQS0-DQS3
- USB differential pairs correctly identified for both FTDI and USB HS with ESD noted
- All 6 LEDs correctly audited with 510 ohm series resistors
- 4 NMOS transistor circuits correctly identified as LED drivers with gate resistors
- D100 (PMEG1030EJ) correctly identified as reverse polarity protection
- LS1205EVD33 (U100) correctly identified as LDO from VCC to +5V
- Decoupling analysis correctly covers all 16 power rails
- Bus topology correctly identifies DDR bus widths and USB data signals
- Power sequencing dependencies correctly show EN/PG net connections
- FT2232HL (U300) correctly identified as producing +1V8_FTDI from internal LDO
- RGMII MDI differential pairs correctly detected between J800 and U800
- Isolation barrier correctly identifies separate GNDPWR domain and +5V_USB_B
- RC filters on PS_NRST and PS_NPOR correctly detected as reset filters
- Cross-domain signal analysis correctly flags USB data lines between voltage domains

### Incorrect
- TPS2051CDBV (U901) classified as LDO but is a USB power distribution switch with overcurrent protection, no voltage regulation
  (signal_analysis.power_regulators)
- X400 (33.333 MHz), X800 (25 MHz), X900 (13 MHz) misclassified as type=connector instead of oscillator. Only X300 (12 MHz) correct
  (statistics.component_types)
- Power tree shows all regulators at sequence_order=0 with enable_type=always_on despite actual PG cascade chain: +5V->U101(+1V0)->PG->U102(+1V8)->PG->U103(+1V35)->PG->U104(+3V3)
  (signal_analysis.power_sequencing_validation.power_tree)
- Zynq U200 power_domains only lists +3V3 but connects to 7 rails: +1V0, +1V35, +1V8, +1V8_PLL, +3V3, +0V675_REF, GND
  (design_analysis.power_domains)
- Regulator input/output capacitor lists over-attribute caps from shared power bus to specific regulators
  (signal_analysis.power_regulators)
- ESD coverage audit lists oscillators X400/X800/X900 as connectors needing ESD protection -- they are internal components
  (signal_analysis.esd_coverage_audit)
- Cross-domain signals flags PG_3V3 as needs_level_shifter but it's already an open-drain output with pullup to correct domain
  (design_analysis.cross_domain_signals)
- R127/C125 detected as RC filter but is actually the output filter of BD3539FVM DDR VTT termination regulator
  (signal_analysis.rc_filters)

### Missed
- RTL8211F-CG Gigabit Ethernet PHY: 39 ETH nets, RGMII data lines with series resistors, MDC/MDIO management bus, dedicated power domains
  (signal_analysis.ethernet_interfaces)
- DDR3L memory interface: 2x MT41K256M16TW, 32-bit data bus, 15-bit address, 3-bit bank, 4 DQS pairs, differential clock, all command signals
  (signal_analysis.memory_interfaces)
- BD3539FVM (U105) DDR VTT termination regulator generating +0V675 from +1V35 not detected
  (signal_analysis.power_regulators)
- 3 of 4 oscillators missed: X400 (33.333 MHz Zynq PS_CLK), X800 (25 MHz Ethernet), X900 (13 MHz USB)
  (signal_analysis.crystal_circuits)
- Clock distribution not detected: 4 distinct clock domains (PS_CLK, ETH_CLK, USB_CLK, FTDI_CLK)
  (signal_analysis.clock_distribution)
- QSPI flash bus not detected: W25Q128 connected via QSPI_CLK/NCS/DQ0-DQ3 with series resistors, doubles as boot mode pins
  (design_analysis.bus_analysis.spi)
- USB ULPI bus not detected: USB3320C with 8-bit ULPI data bus, CLK, DIR, NXT, STP
  (design_analysis.bus_analysis)
- Zynq boot mode configuration circuit with resistor dividers on QSPI lines and DIP switch override not detected
  (signal_analysis)
- 93LC65B EEPROM for FT2232HL configuration not detected as SPI bus
  (design_analysis.bus_analysis.spi)
- 74LVC1G07 open-drain buffers for level translation/reset distribution not detected
  (signal_analysis.level_shifters)
- RGMII series termination resistors on all data/control lines not characterized for signal integrity
  (signal_analysis)

### Suggestions
- Check description field for oscillator keywords ('oscillator', 'XTAL OSC XO') to fix type classification
- Classify TPS2051/TPS2052/TPS2065 as power_switch/load_switch, not LDO
- Resolve power_tree EN chains: when EN connects via resistor to PG of another regulator, set sequence_order accordingly
- Aggregate power pins across all multi-unit symbol units for power_domains
- Add ethernet_interfaces detector for RTL8211F and similar PHYs with RGMII/RMII patterns
- Add memory_interfaces detector for DDR3/DDR3L/DDR4 with address/data/control bus patterns
- Detect QSPI flash with DQ0-DQ3 as Quad SPI bus
- Fix oscillator misclassification cascade into false esd_coverage_audit entries

---
