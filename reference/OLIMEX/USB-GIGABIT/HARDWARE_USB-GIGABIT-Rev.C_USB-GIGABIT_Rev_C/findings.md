# Findings: OLIMEX/USB-GIGABIT / HARDWARE_USB-GIGABIT-Rev.C_USB-GIGABIT_Rev_C

## FND-00001566: kicad_version reported as 'unknown' for file_version 20230121 (KiCad 7); RTL8153 SPI EEPROM interface (Microwire) to 93LC46 misclassified as I2C bus; USB 3.0 SuperSpeed differential pairs classifie...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: HARDWARE_USB-GIGABIT-Rev.E_USB-GIGABIT_Rev_E.kicad_sch
- **Created**: 2026-03-24

### Correct
- The ethernet_interfaces detector correctly identifies U3 (RTL8153VC-CG) as the Ethernet PHY and LAN1 (TM211Q01FM22/LPJG16402AQNL) as the connector. The magnetics list is empty, which is accurate since the TM211Q01FM22 is a magjack with integrated magnetics — there is no separate magnetic transformer component in the schematic.
- The power_regulators detector correctly identifies U4 (SY8089AAAC) as a switching buck converter with inductor L1, output rail V12, and feedback via R15/R12 (both 1.1K). The estimated Vout=1.2V using Vref=0.6V and ratio=0.5 is arithmetically correct for SY8089AAAC. The output rail V12 connects to the RTL8153 VDD10 pins (core voltage). The topology and inductor identification are accurate.
- The crystal_circuits detector correctly identifies X1 (25MHz, 20pF rated) with load capacitors C7 and C8 (39pF each), computing an effective load capacitance of 22.5pF (series combination + stray). The 25MHz crystal is the clock source for the RTL8153. Both load caps are on the correct CKXTAL1/CKXTAL2 nets.
- The signal_analysis detects differential pairs M0_P/M0_N, M1_P/M1_N, M2_P/M2_N, M3_P/M3_N (Gigabit Ethernet MDI pairs between RTL8153 and LAN1 magjack), and USB SS pairs U3SRX_P/N, U3TX_P/N, U3STX_P/N, U3D_P/N (USB 3.0 signals to connector). The Gigabit Ethernet topology with 4 differential pairs is correctly identified.

### Incorrect
- Both Rev.D (file_version 20221018) and Rev.E (file_version 20230121) kicad_sch files report kicad_version='unknown'. These version tokens correspond to KiCad 7.0.x. The analyzer lacks version mapping for these tokens. The PCB output for Rev.E (file_version 20221018) also reports 'unknown'. This affects both schematic and PCB outputs across Rev.D and Rev.E.
  (kicad_version)
- The bus_analysis.i2c section reports two nets (__unnamed_5 = SPISDI/SDA/EEDI and __unnamed_7 = EECS/SCL) as I2C SDA and SCL lines connecting U3 (RTL8153) and U2 (93LC46). In reality, the RTL8153 uses a 3-wire Microwire/SPI interface to the 93LC46 EEPROM. The pin names on the RTL8153 symbol include alternate function labels 'SDA' and 'SCL' for the I2C mode (unused here), which the analyzer incorrectly matches as I2C. The 93LC46 is a Microwire EEPROM, not an I2C device. No I2C pull-up resistors are present, which the analyzer correctly notes (has_pull_up=false).
  (design_analysis)
- The bus_analysis.uart section reports six nets (U3SRX_P, U3SRX_N, U3TX_P, U3TX_N, U3STX_P, U3STX_N) as UART. These are USB 3.0 SuperSpeed (SS) differential pairs between the RTL8153 (U3) and the USB connector (USB1). The net names contain 'TX' and 'RX' substrings which the UART detector matches on, but these are SuperSpeed USB differential pairs carrying USB 3.0 protocol, not UART signals. None of these signals connect to a UART-capable device.
  (design_analysis)
- The USB compliance check reports vbus_decoupling='fail' for USB1. However, C5 (100nF/50V/Y5V/0805) is connected to USB1 pin 0 (shield/power pin) which is on the same net as R4 and the USB housing, not the VBUS pin 1. The VBUS pin 1 connects to FB1 (ferrite bead). The architecture is a USB device (powered from USB host), where VBUS goes through the ferrite bead to power the internal rails. A cap on the connector housing side (C5) is a typical EMI filter, not missing decoupling. The decoupling for the post-ferrite 5V rail (VDD5) is C12 and others.
  (usb_compliance)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001567: total_nets over-counted (93 reported vs ~47 actual) in KiCad 5 legacy schematic; U1 (USB Type-A male connector, USBA30MALE) misclassified as type 'ic'

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: USB-GIGABIT_Rev_C.sch
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
- The Rev.C KiCad 5 legacy schematic reports total_nets=93, but the corresponding PCB has net_count=47, and the equivalent Rev.D/E KiCad 6+ schematics report 51 nets for the same design. The KiCad 5 legacy parser counts wire segments as individual nets rather than tracing electrically connected nodes, inflating the net count by approximately 2x. The Rev.E schematic (KiCad 6+ format) correctly reports 51 nets matching the PCB.
  (statistics)
- In Rev.C, U1 has value 'USBA30MALE' and lib_id 'USB-GIGABIT_Rev_C:USBA30MALE', clearly a USB Type-A male connector. The analyzer classifies it as type='ic' instead of 'connector'. This causes the connector count to be 1 (only LAN1) while it should be 2, and the ic count to be 4 instead of 3. The component type classification relies on lib_id/value heuristics and fails here because the symbol comes from a local library without a recognizable connector prefix.
  (statistics)

### Missed
(none)

### Suggestions
- Fix: U1 (USB Type-A male connector, USBA30MALE) misclassified as type 'ic'

---

## FND-00001568: 4-layer board correctly identified with 59 footprints, 75 vias, 51 nets, fully routed; DFM flags 0.127mm (5mil) track spacing as requiring 'advanced' process when it is within standard capabilities

- **Status**: promoted
- **Analyzer**: pcb
- **Source**: HARDWARE_USB-GIGABIT-Rev.E_USB-GIGABIT_Rev_E.kicad_pcb
- **Created**: 2026-03-24

### Correct
- The PCB analyzer correctly identifies the 4-layer stackup (F.Cu, In1.Cu/GND, In2.Cu, B.Cu), 59 footprints (52 schematic components + 4 logos/signs + 3 blank-reference logo footprints), 75 vias, 680 track segments, and confirms complete routing with 0 unrouted nets. Board dimensions 51.5x19.0mm match the gerber Edge.Cuts. Net count 51 matches the schematic.

### Incorrect
- The DFM checker reports tier_required='advanced' for 0.127mm minimum track spacing, with standard_limit_mm also set to 0.127mm (actual == standard_limit). The message 'requires advanced process (standard: 0.127mm)' is contradictory: if the actual value equals the standard limit, it should pass as standard. Furthermore, 0.127mm (5mil) is well within the capability of standard PCB processes (most standard fabricators handle 6/6 or 5/5 mil). The threshold logic appears to trigger 'advanced' when actual >= standard_limit rather than when actual < standard_limit.
  (dfm)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001569: Rev.C gerber alignment warning is legitimate — In2.Cu is 4.1mm narrower than Edge.Cuts

- **Status**: new
- **Analyzer**: gerber
- **Source**: gerbers
- **Created**: 2026-03-24

### Correct
- The alignment check flags Rev.C gerbers as misaligned with 'Width varies by 4.1mm across copper/edge layers'. The In2.Cu layer is 47.431mm wide while Edge.Cuts is 51.5mm — a 4.069mm difference — indicating that routing on the second inner copper layer does not extend to the board edges. This is a real observation about the routing distribution in the older Rev.C layout, generated by KiCad 5.99.0-dev. Rev.D and Rev.E inner copper layers are properly sized (~53.7mm and ~50.7mm respectively vs their edge cuts).

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001570: Rev.E 4-layer gerber set is complete and aligned, with correct via and hole classification

- **Status**: new
- **Analyzer**: gerber
- **Source**: HARDWARE_USB-GIGABIT-Rev.E_gerbers
- **Created**: 2026-03-24

### Correct
- The gerber analyzer correctly identifies all 11 gerber layers plus 2 drill files (PTH and NPTH), confirms completeness with no missing required or recommended layers, and validates alignment across copper layers. Via classification correctly identifies two via sizes (0.4mm and 0.6mm diameter, totaling 75 vias matching PCB analysis). Component hole classification identifies 1.1mm holes (14 count) for through-hole pads and 3.3mm NPTH for mounting holes. Board dimensions 51.5x19.0mm match PCB output.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001899: Crystal circuit X1 correctly identified with load capacitors and effective load calculation; Switching regulator U4 (SY8089AAAC) correctly identified with feedback divider and estimated output volt...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: repos_USB-GIGABIT_HARDWARE_USB-GIGABIT-Rev.E_USB-GIGABIT_Rev_E.kicad_sch
- **Created**: 2026-03-24

### Correct
- X1 (25MHz, 20pF spec) detected with C7 and C8 (39pF each) as load capacitors. Effective load calculated as 22.5pF (39/2 + ~3pF stray), which is close to but slightly over the 20pF spec — a reasonable observation. Crystal circuit section is correctly populated.
- U4 detected as a switching regulator with inductor L1, feedback resistors R15/R12 (1.1k/1.1k ratio 0.5), output rail V12, estimated Vout=1.2V (Vref=0.6V assumed). This matches the RTL8153 core voltage domain requirement. Input rail recorded as '__unnamed_0' (the VBUS net after ferrite bead FB1).
- All 4 Ethernet MDI pairs (M0–M3) and 3 USB pairs (U3SRX, U3TX, U2/U2D) identified. U2D_P/N has series resistors R2/R3 noted. All pairs routed to correct ICs (RTL8153 and/or TM211Q01FM22 magnetics connector).
- Power sequencing analysis correctly shows U4 (SY8089AAAC) enable pin is driven from a net controlled by U3, FB1, and C12, indicating the 1.2V core rail is soft-start controlled from the USB-to-GbE bridge.
- usb_compliance shows 2 failures: no VBUS ESD TVS and no VBUS decoupling capacitor on USB1 (USB1065 Type-A connector). The design relies on the host for VBUS protection; the dongle does not add its own. These are real gaps even if acceptable by design intent.
- sourcing_audit shows 0/48 MPN coverage. The design uses Olimex-internal value-only component designations (e.g. '100nF/10V/X5R /20%/0402') without DigiKey/Mouser/LCSC part numbers populated in schematic properties. This is accurate.
- connectivity_issues shows empty unconnected_pins, single_pin_nets, and multi_driver_nets lists. Routing is complete with all pins connected as expected for this production design.

### Incorrect
- ic_pin_analysis assigns U3 function='Ethernet PHY'. The RTL8153VC-CG is a USB 3.0 to Gigabit Ethernet bridge/controller IC that integrates both the USB 3.0 device interface and the Ethernet MAC+PHY. Classifying it as merely 'Ethernet PHY' misses the USB side. A more accurate label would be 'USB-to-Gigabit Ethernet bridge' or 'USB-Ethernet controller'. This also flows into ethernet_interfaces where the magnetics list is empty — the analyzer looks for a discrete magnetics IC rather than recognizing that the TM211Q01FM22 MagJack connector has integrated magnetics.
  (ic_pin_analysis)
- bus_analysis.i2c reports two nets as I2C: __unnamed_5 (U3 pin SPISDI/SDA/EEDI to U2 DI) and __unnamed_7 (U3 pin EECS/SCL to U2 CS). The RTL8153VC-CG uses a proprietary serial EEPROM interface (not standard I2C) to read configuration from 93LC46 (U2, a Microwire/SPI EEPROM). Pin 40 is 'EECS' (EEPROM Chip Select), not SCL. No I2C pull-up resistors are present, and the I2C 'no pull-up' warning is technically a consequence of this misclassification. The analyzer infers I2C from SDA/SCL substrings in multi-mode pin names.
  (design_analysis)
- test_coverage.debug_connectors lists USB1 (USB1065, USB Type-A male plug) with interface='uart'. USB1 is the main functional USB 3.0 connector connecting the dongle to the host PC. Nets U3SRX_P/N and U3STX_P/N are USB 3.0 SuperSpeed differential pairs (RX and TX). The 'UART' classification arises from pattern-matching 'RX'/'TX' substrings in net names. This misidentification misleads: there is no debug UART on this board.
  (test_coverage)
- The schematic header contains '(version 20230121) (generator eeschema)' which corresponds to KiCad 7. The analyzer extracts file_version correctly but leaves kicad_version as 'unknown'. The same issue occurs for the PCB (file_version 20221018, KiCad 6). The version mapping integer→product is not implemented.
  (kicad_version)
- The schematic uses the power net symbol '+3.3V' (statistics.power_rails and decoupling_analysis.rail), while the PCB netlist names the same rail '+3V3'. These are two different strings for the same net. The analyzer reports each file independently without flagging this naming inconsistency across the schematic/PCB pair. This is a genuine design inconsistency in the source files that ideally would be surfaced.
  (statistics)

### Missed
- ethernet_interfaces[0].magnetics is empty []. The TM211Q01FM22 (also known as LPJG16402AQNL) is a RJ-45 jack with integrated Bob Smith termination and magnetics. The analyzer looks for a separate discrete magnetics transformer component rather than recognizing that this connector has built-in magnetics. A complete analysis would note that the design does not require a separate transformer because LAN1 provides integrated magnetics.
  (signal_analysis)
- ic_pin_analysis shows U2 value='NA(93LC46)' with function='' and category left as 'ic'. The 93LC46 is a well-known Microwire/SPI serial EEPROM (Microchip). The component description field is empty in the schematic properties, so the analyzer has no description text to categorize it. However, the part number '93LC46' is present in the value field and could be matched to a known EEPROM pattern.
  (ic_pin_analysis)
- test_coverage.test_point_count=0 and test_points=[]. This is accurate: the design has no dedicated TP* test point footprints. This is worth flagging as a design observation (small form-factor dongle without testability features) but the analyzer does not surface it as a notable absence in the design observations section.
  (test_coverage)

### Suggestions
(none)

---

## FND-00001900: 4-layer stackup correctly identified: F.Cu (signal), In1.Cu (GND, aliased In1_GND.Cu), In2.Cu (power), B.Cu (signal); Board dimensions correct: 51.5mm × 19.0mm matches Edge.Cuts in source; Routing ...

- **Status**: promoted
- **Analyzer**: pcb
- **Source**: repos_USB-GIGABIT_HARDWARE_USB-GIGABIT-Rev.E_USB-GIGABIT_Rev_E.kicad_pcb
- **Created**: 2026-03-24

### Correct
- layers array shows 4 copper layers with correct names and types. In1.Cu has alias 'In1_GND.Cu' matching the KiCad layer alias in the source file. The layer type assignments (mixed for signal layers, power for inner planes) are accurate.
- statistics shows board_width_mm=51.5, board_height_mm=19.0. This matches the compact USB dongle form factor targeting a standard PCB footprint.
- connectivity shows routing_complete=true, unrouted_count=0, total_nets_with_pads=51. The production design is fully routed, which is verified correctly.
- dfm shows dfm_tier='advanced', min_track_width_mm=0.127, approx_min_spacing_mm=0.127. The tight pitch of the RTL8153 QFN-56 and the signal routing requires advanced fab capabilities. One DFM violation noted for track spacing at the advanced threshold.
- placement_analysis.edge_clearance_warnings shows USB1 on B.Cu with edge_clearance_mm=-0.35. This is expected and intentional: the USB Type-A plug extends beyond the PCB edge by design so it can plug into a host port. The detection is accurate.
- tombstoning_risk lists multiple 0402 capacitors (C10, C11, etc.) as medium risk where one pad connects to a GND pour and the other to a signal net. This is a standard SMT assembly concern for small-body passives adjacent to ground pours.
- statistics.zone_count=150. The KiCad 7 source file contains $teardrop$ pad/via zones with priority 30000+ for every pad and via transition, which inflate the zone count significantly. The analyzer counts these correctly; they represent teardrops on all 75 vias and many component pads.

### Incorrect
- PCB header contains '(version 20221018) (generator pcbnew)' which is KiCad 6. The analyzer extracts file_version=20221018 correctly but kicad_version='unknown'. Notably the schematic (version 20230121, KiCad 7) and PCB (version 20221018, KiCad 6) are different KiCad versions — the project was migrated partially. Neither is identified by product version.
  (kicad_version)

### Missed
- net_lengths shows the USB 3.0 SuperSpeed RX pair: U3SRX_P=33.455mm, U3SRX_N=33.516mm (delta=0.061mm). USB TX pair: U3TX_P=30.042mm, U3TX_N=28.885mm (delta=1.157mm). The U3TX skew of 1.157mm is above typical 0.1mm USB 3.0 SS guideline. Ethernet MDI pairs show sub-0.1mm skew (e.g. M3_P=11.705, M3_N=11.731, delta=0.026mm). The analyzer reports per-net lengths but does not compute intra-pair skew or flag USB TX imbalance.
  (net_lengths)
- The board has 680 track segments and 75 vias across a 4-layer stackup. High-speed signals (USB SS, Gigabit Ethernet) traverse layers via vias, potentially crossing plane boundaries. The analyzer does not check whether high-speed signal vias have adjacent return-path vias or whether layer transitions cross a GND-to-power boundary (which would create a return path discontinuity). This is important for a design operating at USB 3.0 (5 Gbps) and Gigabit Ethernet frequencies.
  (layer_transitions)

### Suggestions
(none)

---

## FND-00001901: 11-file Gerber set correctly identified as complete 4-layer stackup; PTH drill count (94 holes) and NPTH count (4 holes) correctly reported; Layer alignment check passes — all copper and mask layer...

- **Status**: promoted
- **Analyzer**: gerber
- **Source**: repos_USB-GIGABIT_HARDWARE_USB-GIGABIT-Rev.E_gerbers_USB-GIGABIT_Rev_E.zip
- **Created**: 2026-03-24

### Correct
- Gerber analysis identifies 11 gerber files covering F.Cu, In1.Cu (GND), In2.Cu (power), B.Cu, F.SilkS, B.SilkS, F.Mask, B.Mask, F.Paste, Edge.Cuts, and User.Comments. Plus 2 Excellon drill files (PTH and NPTH). All mandatory layers present for a standard 4-layer board.
- The drill analysis reports 94 PTH holes and 4 NPTH holes for a total of 98. The 4 NPTH holes are likely the USB connector's mechanical retention pins. This matches the board's low via count (75 vias in PCB analysis) plus component through-holes.
- alignment_check shows all layers properly aligned. Gerber extents for copper layers are within the 51.5mm × 19mm board outline, consistent with PCB analysis. The alignment verification is correctly executed.
- B.SilkS layer has x_max=56.38mm while Edge.Cuts x_max=51.5mm — a 4.88mm overshoot on the right side. This is likely caused by the USB Type-A connector body silkscreen outline extending past the board edge (by design, as the connector protrudes). The gerber analyzer correctly identifies this as a silk overflow vs the board outline.
- The PTH Excellon file defines tool T4 with 1.0mm diameter but uses it for 0 holes. The gerber analyzer reports this accurately. This is a minor DFM note — drill file contains a defined but unused tool, which is harmless but indicates leftover tooling from a prior revision.

### Incorrect
(none)

### Missed
- The B.SilkS extension beyond Edge.Cuts is intentional (the USB-A connector body extends past the PCB). The gerber analyzer flags it as an anomaly but does not distinguish between intentional connector-body silkscreen overhang (benign) and accidental text/logo outside the board boundary (a fabrication concern). Without context from the PCB component placement, the analyzer cannot make this distinction, but the output would benefit from noting that connectors or mechanical features often justify such overhangs.
  (layer_extents)

### Suggestions
(none)

---
