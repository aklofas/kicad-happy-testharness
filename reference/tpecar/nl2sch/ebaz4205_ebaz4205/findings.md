# Findings: tpecar/nl2sch / ebaz4205_ebaz4205

## ?: EBAZ4205 Zynq XC7Z010 Bitcoin miner board with DDR3, NAND flash, Ethernet PHY, 4x switching regulators; power regulators and isolation well-detected but DDR3 memory interface missed entirely and several component type misclassifications

- **Status**: new
- **Analyzer**: schematic
- **Source**: ebaz4205_ebaz4205.kicad_sch.json
- **Created**: 2026-03-23

### Correct
- 565 unique component references correctly counted across resistors(288), capacitors(212), inductors(11), ferrite beads(4), ICs(20), connectors(10), etc.
- 4x J37I switching regulators (U22, U26, U27, U28) correctly identified with topology=switching, inductors, and feedback dividers computing accurate output voltages (3.3V, 1.0V, 1.5V, 1.8V)
- TPS51200AQDRCRQ1 (U72) correctly identified as LDO DDR termination regulator with VCC input and VCC1 output
- 4 feedback networks correctly identified on J37I regulators connecting FB pins to voltage dividers
- Isolation barrier detected with 4 ground domains (GND, GND3, GNDA, GNDADC_0) and 4 optocouplers (U67, U68 EL817; U69, U70 PC817)
- Ethernet PHY IP101GA (U24) correctly detected in ethernet_interfaces
- 9 voltage dividers detected including DDR VREF (R2458/R2459 = 0.5 ratio into PS_DDR_VREF0), MIO VREF (R2432/R2433 = 0.5 into PS_MIO_VREF_501), and 4 regulator feedback dividers
- Power sequencing correctly identifies 5 regulators with controlled enable pins and U72 PGOOD signal
- U31 Zynq XC7Z010 correctly handled as 9-unit multi-unit symbol with 400 total pins across all units
- NAND flash U12 W29N01HVSINA correctly mapped with 48 pins, data/control signals connected to Zynq PS_MIO pins
- Y3 25MHz crystal correctly detected in crystal_circuits

### Incorrect
- U20 and U21 (MMBT3904/1AM NPN transistors, lib_id Device:Q_NPN_BEC) classified as type=ic instead of type=transistor; they are discrete BJTs used in power control circuits
  (statistics.component_types)
- EC2, EC5, EC6 (Device:CP electrolytic capacitors with values 470UF/16V and 100UF/16V) classified as type=other instead of type=capacitor
  (statistics.component_types)
- X3 (DS1307Z+ RTC IC with 8 pins, I2C interface) misclassified as type=connector instead of type=ic; the DS1307Z+ is a real-time clock chip
  (components)
- X5 (TXC-EBAZ oscillator module) classified as type=connector; likely an oscillator or crystal module based on its lib_id pattern and placement near clock circuitry
  (components)
- Ethernet interface missing magnetics: T6 (BT16B03 Ethernet transformer) connects between PHY U24 and RJ45 U25 but is not listed in ethernet_interfaces magnetics array
  (signal_analysis.ethernet_interfaces)
- Power rails list incomplete: stats shows only [GND, GNDA, VCC, VCCA] but design has additional major rails: VCC-DDR, VCCP, VCC1, IN, VCCE, VCCO, VCCB, VCC6, VCC8, GND3, GNDADC_0
  (statistics.power_rails)
- Cross-domain signals over-flagging: DDR signals between U31 and U66 flagged as needing level shifters, but the Zynq VCCO_DDR_502 bank runs at VCC-DDR (1.5V) matching the DDR3 voltage domain -- no level shifter needed
  (design_analysis.cross_domain_signals)

### Missed
- DDR3 memory interface not detected: U66 (EM6GD16EWKG-12H DDR3L SDRAM) connects to U31 Zynq via 76+ DDR signals (address, data, control, DQS) but memory_interfaces is empty
  (signal_analysis.memory_interfaces)
- Transistor circuits not detected: U20 and U21 (MMBT3904 NPN BJTs) have surrounding passive components (capacitors, resistors) in power switching roles but transistor_circuits is empty
  (signal_analysis.transistor_circuits)
- X8 (33.333MHz crystal, lib_id ebaz4205:TXC-7C) not detected in crystal_circuits despite being typed as crystal; only Y3 and Y2 appear in the list
  (signal_analysis.crystal_circuits)
- U65 SGM706-SYS8 voltage supervisor/watchdog not detected as a protection device; it monitors supply voltage and provides system reset functionality
  (signal_analysis.protection_devices)
- RJ45 connector U25 (8P8C_LED) not linked in ethernet_interfaces connectors array despite being in the same subcircuit as PHY U24 and magnetics T6
  (signal_analysis.ethernet_interfaces)
- RC/LC filters on power rails not detected despite numerous inductor+capacitor combinations on VCC, VCCP, VCCA, VCC-DDR rails used for power filtering/decoupling
  (signal_analysis.lc_filters)

### Suggestions
- Device:Q_NPN_BEC, Device:Q_PNP_BEC, and similar lib_ids should be classified as type=transistor, not type=ic
- Device:CP and Device:CP_Small should be classified as type=capacitor (electrolytic/polarized)
- Crystal circuit detection should match components by type=crystal regardless of reference prefix (X vs Y)
- Memory interface detection should look for DDR3/DDR4 SDRAM ICs and their address/data bus connections to SoC/FPGA
- Ethernet interface detection should trace the signal path from PHY through magnetics transformer to RJ45 connector
- Voltage supervisors (SGM706, TPS382x, etc.) should be detected as protection devices
- Power rail detection should include all nets with VCC/GND prefixes or those connected to regulator outputs, not just explicitly named power symbols

---

## FND-00002528: EBAZ4205 is a Zynq 7010-based board (originally Bitcoin miner controller) with DDR3 SDRAM, NAND flash, IP101GA Ethernet PHY, four J37I switching regulators, and optocoupler isolation. Analyzer performs well on power regulation and Zynq handling, but misses DDR3 and NAND flash memory interfaces, misclassifies several component types, and falsely detects RMII Ethernet signals as UART.

- **Status**: confirmed
- **Analyzer**: schematic
- **Source**: ebaz4205_ebaz4205.kicad_sch.json
- **Created**: 2026-03-30

### Correct
- Four J37I switching regulators (U22/U26/U27/U28) correctly identified with accurate voltages: VCC=3.3V, VCCP=1.0V, VCCA=1.8V, VCC-DDR=1.5V
- XC7Z010-1CLG400I (U31) correctly identified as FPGA with all 9 units parsed (400 pins)
- IP101GA Ethernet PHY (U24) correctly identified with RMII pins and 25MHz crystal Y3
- Four optocouplers (U67/U68 EL817, U69/U70 PC817) correctly detected in isolation_barriers with separate ground domains
- Zynq JTAG debug nets correctly classified
- DDR VREF divider R2432/R2433 (100K/100K) correctly identified at 1.65V
- TPS51200AQDRCRQ1 (U72) DDR termination regulator correctly identified
- 74 DDR-related nets correctly parsed in nets dictionary

### Incorrect
- U20/U21 (MMBT3904 NPN transistors, Device:Q_NPN_BEC) classified as 'ic' instead of 'transistor'.
  (statistics.component_types)
- U25 (RJ45 connector, 8P8C_LED) classified as 'ic' instead of 'connector'.
  (statistics.component_types)
- X3 (DS1307Z+ RTC IC) classified as 'connector' instead of 'ic' due to X-prefix fallback.
  (statistics.component_types)
- EC2/EC5/EC6 (Device:CP polarized capacitors) classified as 'other' instead of 'capacitor'.
  (statistics.component_types)
- RMII signals TXD0-3, RXD0-3 between U24 (PHY) and U31 (Zynq) falsely detected as UART. These are Ethernet data signals.
  (design_analysis.bus_analysis.uart)
- False decoupling warnings for ICs on VCC rail which has 26 decoupling capacitors.
  (signal_analysis.design_observations)
- power_budget for VCC-DDR shows ic_count=0 despite U66 DDR3 being on that rail.
  (power_budget)

### Missed
- DDR3 SDRAM interface not detected: U66 (EM6GD16EWKG-12H) with 16 DQ, differential DQS, 14 address, CK/CKE/CS/ODT/WE/CAS/RAS to Zynq. memory_interfaces is empty.
  (signal_analysis.memory_interfaces)
- NAND flash interface not detected: U12 (W29N01HVSINA 1Gbit) with 8 I/O, ALE, CLE, #CE, #RE, #WE to Zynq PS_MIO.
  (signal_analysis.memory_interfaces)
- Ethernet transformer T6 (BT16B03) not linked to ethernet_interfaces. U25 (RJ45) also not linked.
  (signal_analysis.ethernet_interfaces)
- X3 (DS1307Z+ RTC) not detected as I2C device. bus_analysis.i2c is empty.
  (design_analysis.bus_analysis.i2c)

### Suggestions
- Add Device:Q_NPN_* and Device:Q_PNP_* lib_id recognition for transistor classification.
- Add 8P8C/RJ45 lib_id recognition for connector classification.
- Add Device:CP lib_id recognition for capacitor classification.
- Improve memory_interfaces to detect DDR (DQ/DQS/CK net names) and NAND (ALE/CLE/#CE signals).
- Exclude RMII signals from UART detection when Ethernet PHY present on same nets.
- Improve X-prefix classification: check lib_id before defaulting to connector.

---
