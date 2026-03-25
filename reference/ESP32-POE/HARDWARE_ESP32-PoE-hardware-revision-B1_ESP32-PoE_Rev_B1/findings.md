# Findings: ESP32-POE / HARDWARE_ESP32-PoE-hardware-revision-B1_ESP32-PoE_Rev_B1

## FND-00000513: kicad_version reported as 'unknown' for file_version 20230121 (KiCad 7); ESD protection for ethernet and USB differential pairs attributed to wrong components; Power regulator detection for U7 (TPS...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: HARDWARE_ESP32-PoE-hardware-revision-M1_ESP32-PoE_Rev_M1.kicad_sch.json
- **Created**: 2026-03-23

### Correct
- M1.kicad_sch correctly identifies U7 as a switching regulator with topology='switching', inductor='L2', output_rail='+3.3V', input_rail='__unnamed_1', estimated_vout=3.245V (using 0.6V Vref heuristic and R29/R30 ratio 0.185), feedback_divider={'r_top':'R29','r_bottom':'R30'}. U5 (TX4138 PoE boost converter) is also detected with feedback divider R38/R34, estimated_vout=4.053V. The inrush analysis, feedback_networks, and is_feedback flag on voltage dividers are all correctly populated. The regulator subcircuit neighborhood (C36 output cap, D3 diode, FET2 gate driver) is captured in subcircuits.
- M1.kicad_sch correctly detects I2C SCL on GPIO16\I2C-SCL with pull-up R31 (2.2k/R0402 to +3.3V) and SDA on GPIO13\I2C-SDA with pull-up R35 (2.2k/R0402 to +3.3V), both driven by U6 (ESP32). L1.sch also correctly detects this (legacy parser does resolve these nets). M1.sch fails to detect I2C due to its net connectivity bug.
- All three schematics correctly identify the ethernet interface: phy_reference='U4', phy_value='LAN8710A-EZC(QFN32)', connector LAN_CON1 (RJP-003TC1). RMII signals (GPIO17-GPIO27 group) are present in net_classification. The +3.3V/+3.3VLAN domain split for the PHY is detected in M1.kicad_sch with 10 cross-domain signals identified for the EMAC lines. The LAN magnetics are listed as empty (magnetics=[]) which is correct — this design uses an integrated magnetics RJ45 connector.
- M1.kicad_sch correctly identifies 7 components present in M1 but absent from L1: U9 (TPS2378DDAR PoE Class 4 interface controller), R52 (24.9k), R53 (1.27k), R54 (NA/66.5R), R55 (4.7k), Class4_EN1 (Closed jumper), and C36 (NA/120pF DNP). U2 (TPS2375D PoE controller from L1) is absent in M1.kicad_sch, replaced by U9 (TPS2378DDAR). The dnp_parts count of 1 correctly captures C36 as the only DNP component. These differences correctly reflect the PoE controller upgrade from TPS2375D to TPS2378DDAR between L1 and M1.

### Incorrect
- The analyzer reports kicad_version='unknown' for file_version 20230121. KiCad 7 uses format dates in the 2022-2023 range (e.g., 20221018, 20230121). The version should be identified as '7' or '7.x'. The L1.sch (KiCad 5 legacy) and M1.sch (KiCad 5 legacy) correctly identify as '5 (legacy)', so the regression is specific to KiCad 6/7/8 format date-based version mapping.
  (signal_analysis)
- For RD+/RD- and TD+/TD- ethernet pairs, esd_protection=['U4'] — but U4 is the LAN8710A ethernet PHY, not an ESD device. The actual ESD protection is provided by TVS1 (ESDS314DBVR, explicitly listed in protection_devices), TVS2, and TVS3 (GG0402052R542P), which are all passive/diode-type components on those nets. U4 appears in shared_ics because it is a legitimate functional device on those nets, not because it provides ESD protection. For the USB D+/D- pair, esd_protection=['U1'] — but U1 is the CH340X USB-to-UART IC. There is no separate ESD protection component on D+/D-, so has_esd should be false and esd_protection should be empty. The analyzer appears to pick the largest or first matching IC on a net as the ESD protector rather than filtering for dedicated TVS/ESD components.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00000514: Legacy parser fails to resolve 19 named net pin connections, causing cascading analysis failures; T1 transistor circuit missed; I2C bus not detected; ERC warnings absent due to broken net connectiv...

- **Status**: new
- **Analyzer**: schematic
- **Source**: HARDWARE_ESP32-PoE-hardware-revision-M1_ESP32-PoE_Rev_M1.sch.json
- **Created**: 2026-03-23

### Correct
(none)

### Incorrect
- M1.sch (KiCad 5 legacy) shows 19 named nets with point_count > 0 but 0 pins, including GPIO4\U1TXD (9 points), TD+ (12 points), GPIO3\U0RXD (13 points), GPIO16\I2C-SCL (14 points), GPI39 (11 points), and many EMAC signal nets. These nets have wires and labels present (point_count > 0) but the legacy net tracer fails to associate component pins with them. The same schematic in M1.kicad_sch correctly resolves all of these — e.g. GPIO3\U0RXD has 5 pins in the .kicad_sch output but 0 in the .sch output. Total nets: 110 in M1.sch vs 120 in M1.kicad_sch (same schematic content). This is a net-grouping/pin-connection bug in the KiCad 5 legacy parser.
  (signal_analysis)
- Due to the zero-pin net bug in M1.sch legacy parsing: (1) T1 (LMUN2211LT1G) transistor circuit is not detected — M1.kicad_sch correctly detects Q2, Q3, and T1 while M1.sch only finds Q2 and Q3. (2) I2C bus is empty ([] for i2c in bus_analysis) because the SCL and SDA nets (GPIO16\I2C-SCL with 0 pins, GPIO13\I2C-SDA with 1 pin) cannot be linked to U6 pull-up resistors R31 and R35 — M1.kicad_sch correctly detects both. (3) ERC warnings count is 0 for M1.sch vs 5 for M1.kicad_sch because nets with no pins produce no driver/load violations. These are all downstream consequences of the net-pin resolution failure.
  (signal_analysis)
- M1.sch reports 0 cross-domain signals. M1.kicad_sch correctly identifies 10 cross-domain signals, including GPIO26\EMAC_RXD1(RMII), GPIO25\EMAC_RXD0(RMII), GPIO27\EMAC_RX_CRS_DV crossing the +3.3V / +3.3VLAN power domain boundary (U6 ESP32 vs U4 LAN8710A). This is a direct consequence of the net-pin resolution failure: without pin associations on those nets, the analyzer cannot determine which ICs share the net and therefore cannot detect domain crossings.
  (signal_analysis)
- M1.sch reports differential pair TD+/TD- with series_resistors=['R15'] only. R15 is an ethernet termination/bias resistor, not a series resistor for TD. The correct series resistors for TD+/TD- are R12 and R13 as identified in both L1.sch and M1.kicad_sch. Similarly RD+/RD- shows ['R10', 'R15'] but R15 should not be there. These mis-attributions result from broken net connectivity causing the analyzer to pick up wrong resistors.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00000515: Voltage divider R29/R30 midpoint erroneously placed on U7 LX (switching node) instead of FB pin; U7 (SY8089AAAC buck converter) not detected as a power regulator; Ethernet differential pairs show h...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: HARDWARE_ESP32-PoE-hardware-revision-L1_ESP32-PoE_Rev_L1.sch.json
- **Created**: 2026-03-23

### Correct
- L1.sch correctly identifies Q1 as a 12 MHz crystal with load caps C4 and C5 (27pF each), computed effective load capacitance 16.5 pF (series combination + ~3 pF stray). This component was removed in the M1 revision (not present in M1.kicad_sch), which is consistent with the ESP32-WROOM module revision using an internal crystal. M1.sch (legacy snapshot of M1) still shows Q1, confirming the .sch file predates the removal.

### Incorrect
- In L1.sch, the voltage divider R29 (220k) / R30 (49.9k) is reported with mid_net=__unnamed_1, which connects to U7 pin 3 (LX, the switching node of SY8089AAAC). However, U7 pin 5 (FB, the feedback input) is on __unnamed_2, which connects to L2 inductor pin 1. In M1.kicad_sch, the same R29/R30 divider's midpoint (__unnamed_2) correctly connects to U7 FB pin. The legacy parser merges what should be two separate nets — the inductor output and the feedback resistor junction — causing the feedback network to appear as if it monitors the LX switching node. The voltage divider mid_point_connections therefore incorrectly shows U7/LX as the monitored point instead of U7/FB, preventing the power_regulators list from being populated for L1.sch.
  (signal_analysis)
- L1.sch reports both RD+/RD- and TD+/TD- differential pairs with has_esd=false. However, TVS1 (ESDS314DBVR, a 4-channel ESD IC) is in the protection_devices list with protected_nets=['RD+','RD-','TD+','TD-']. The ESD IC is directly on those nets yet the differential pair analysis fails to cross-reference protection_devices. M1.kicad_sch correctly shows has_esd=true for both ethernet pairs. Note: M1.kicad_sch's esd_protection=['U4'] attribution is itself wrong (see next finding), but the has_esd boolean is correct.
  (signal_analysis)

### Missed
- L1.sch signal_analysis.power_regulators is empty []. U7 is a SY8089AAAC synchronous buck converter with L2, R29/R30 feedback divider, C6 output cap, and D3 bootstrap diode — a classic switching regulator subcircuit. M1.kicad_sch correctly detects U7 (TPS62A02ADRLR, the M1 revision equivalent) with topology='switching', inductor='L2', output_rail='+3.3V', and estimated_vout=3.245V. The detection failure in L1.sch is caused by the net connectivity error described above: the FB pin is not linked to the feedback divider midpoint, so the regulator topology cannot be inferred.
  (signal_analysis)

### Suggestions
(none)

---
