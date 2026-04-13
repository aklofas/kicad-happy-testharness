# Findings: Jana-Marie/EF-S-Adapter / hardware_v1.1_lensmount-v1.1

## FND-00000488: All 39 component references and 41 nets correctly extracted; U1 STM32F042F6Px USB pin assignments are correct; Q1/Q2/Q3 2N7002 N-channel level shifters correctly identified; U2 XC6206PxxxMR LDO reg...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: hardware_v1.1_lensmount-v1.1.kicad_sch.json
- **Created**: 2026-03-23

### Correct
- All component references (J1–J10, U1–U3, Q1–Q5, R1–R13, C1–C7, P1) are correctly parsed with accurate values, lib_ids, footprints, and Mouser part numbers. All 41 nets are correctly constructed from wires and global labels. Net membership is accurate for all named nets including +3V3, VBUS, +BATT, GND, D+, D-, NRST, SWDIO, SWCLK, DCLK_3V3, DOUT_3V3, DIN_3V3, and the 5V-side SPI-equivalent signals.
- D- is correctly assigned to U1 pin 17 (PA9/PA11) and D+ to U1 pin 18 (PA10/PA12). SWDIO maps to pin 19 (PA13), SWCLK to pin 20 (PA14). The level-shifted SPI signals are correct: DCLK_3V3 on pin 11 (PA5), DOUT_3V3 on pin 12 (PA6), DIN_3V3 on pin 13 (PA7). EN_VBAT on pin 2 (PF0), EN_VBUS on pin 3 (PF1).
- All three 2N7002 FETs are correctly classified as level_shifter topology. Q1: gate=+3V3, drain=DIN_5V, source=DIN_3V3. Q2: gate=+3V3, drain=DOUT_5V, source=DOUT_3V3. Q3: gate=+3V3, drain=DCLK_5V, source=DCLK_3V3. Gate resistors R3/R4/R5 (5k1) correctly associated.
- U2 is correctly classified as topology=LDO with input_rail=VBUS and output_rail=+3V3. Input decoupling C3 (1u) and output decoupling C4 (1u) are both present on their correct rails.
- USB compliance reports cc1_pulldown_5k1=pass and cc2_pulldown_5k1=pass. R1 (5k1) is on the J9.A5 (CC1) net and R2 (5k1) on the J9.B5 (CC2) net. This correctly identifies the board as a USB device (not host), conforming to USB-C 2.0 Rd pulldown requirements.

### Incorrect
- Q4 (AO3401A at position (214.63, 43.18), rotation 270°, mirror_x) and Q5 (AO3401A at (226.06, 58.42), rotation 270°, mirror_x) have gate_net=__unnamed_13/17, drain_net=__unnamed_15/19, source_net=__unnamed_14/18 in the output. The actual connectivity from the schematic wires is: Q4 source connects to VBUS/+BATT area (R9+VBUS path), Q4 gate is driven by a divider of R10 (100k, +BATT pullup) and R11 (5k1) to EN_VBAT (U1 PF0). Q5 source connects to VBUS, Q5 gate is driven by R12 (100k, VBUS pullup) and R13 (5k1) to EN_VBUS (U1 PF1). The Q4/Q5 topology is software-controlled power switching (P-channel high-side switches) for the VBAT and VDD output rails. The failure is that after 270° rotation with mirror_x, the analyzer cannot resolve which schematic wire endpoints correspond to which MOSFET pins.
  (signal_analysis)
- The protection_devices output correctly identifies U3 (USBLC6-4) as protecting both D+ and D- (protected_nets includes both). However, the design_observations entry for net D- has has_esd_protection=False, while the entry for D+ has has_esd_protection=True. Both D- (via U3 pin 1, IO1) and D+ (via U3 pin 3, IO2) are protected by U3. The per-net ESD check appears to only match U3 as protecting whichever net is listed as protected_net (the first one, D+) rather than checking all entries in protected_nets.
  (signal_analysis)
- For transistor_circuits entries Q1, Q2, and Q3, gate_driver_ics includes ['U1', 'U1', 'U2']. U2 (XC6206PxxxMR LDO) is not a gate driver — it is the power regulator whose output (+3V3) forms the gate bias rail. It appears because its VO pin is on the +3V3 net. The gate driver should be U1 (STM32F042F6Px), which controls the GPIO signals. Additionally, U1 appears twice because it has two supply pins (VDD pin 16 and VDDA pin 5) on +3V3, causing it to be counted once per pin in the gate driver search.
  (signal_analysis)
- J10 has value='Picoblade DNP' in both v1 and v1.1 schematics and has no formal KiCad DNP attribute. The analyzer reports dnp=False for J10 and the statistics show dnp_parts=0 in v1.1. In contrast, D1 in v1 has value='DNP' (exact match) and is correctly reported as dnp=True. The DNP detection only triggers on exact value match 'DNP', not substring match. J10 is a DNP connector (Do Not Populate) per the design intent indicated by the value string.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00000489: U1 STM32F042F6Px signal pin numbers systematically wrong in legacy KiCad5 parser; U3 (lensmount-v1-rescue:USBLC6-4-otter) pin numbers wrong in legacy parser — D- net has U3.2 (GND pin) instead of U...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: hardware_v1_lensmount-v1.sch.json
- **Created**: 2026-03-23

### Correct
- All 34 component references are correctly identified. D1 (value='DNP', Device:D_Small) is correctly flagged as dnp=True and correctly placed on the VBUS (K/cathode) and +BATT (A/anode) nets, representing an optional reverse-current blocking diode. J10 is correctly identified as Conn_01x05_MountingPin (a 5-pin connector with mounting pin, vs the 4-pin J10 in v1.1). The LDO U2 (VBUS→+3V3) and level-shifter topology for Q1/Q2/Q3 are also correctly detected.

### Incorrect
- The legacy KiCad5 parser assigns incorrect pin numbers for U1 STM32F042F6Px right-side signal pins. The analyzer assigns: D- to U1.8 (PA2), D+ to U1.7 (PA1), SWDIO to U1.6 (PA0), and omits SWCLK from U1 entirely. The correct assignments based on schematic wire coordinates are: D- on U1.17 (PA9/PA11), D+ on U1.18 (PA10/PA12), SWDIO on U1.19 (PA13), SWCLK on U1.20 (PA14). The pin numbering error is caused by incorrect geometric mapping of KiCad5 component position + orientation to pin endpoint coordinates — pins 17–20 are instead placed on unnamed nets (__unnamed_5 through __unnamed_9), while the D+/D-/SWDIO labels connect to the wrong low-numbered pins (6–8) which correspond to PA0–PA2.
  (signal_analysis)
- In the D- net, the analyzer places U3.2 (pin name 'GND') rather than U3.1 (pin name 'IO1'). From the schematic source, the wire connecting to D- at y=1850 reaches U3 pin 1 (IO1 at the left side of the SOT-23-6 package). The GND pin (pin 2) is unconnected on the D- net. This is another instance of the legacy KiCad5 pin-numbering error where pin endpoint coordinates are resolved to wrong pin numbers for components in the lensmount-v1-rescue library.
  (signal_analysis)
- In v1 (KiCad5 legacy format), every capacitor has pin1 on GND and pin2 on the power rail. Per the Device:C_Small symbol definition, pin1 is the top connection point (power rail side) and pin2 is the bottom (GND side). The v1.1 output (KiCad6 parser) correctly assigns: C7 pin1=VBUS, pin2=GND; C6 pin1=+BATT, pin2=GND; etc. The v1 output reverses these for all capacitors (C1–C7): e.g., C7 pin2=VBUS (wrong), pin1=GND (wrong). This is a systemic bug in the legacy KiCad5 pin-number resolution for capacitors oriented vertically, where the parser appears to number pins from the coordinate ordering rather than from the symbol definition.
  (signal_analysis)
- In v1, J2 (AGND, at position 9650/1800) and J3 (AGND, at 9650/2000) have no wire connections in the schematic — they are truly unconnected pins. The GND symbol #PWR0114 is placed nearby at (9450, 1800) but there is no wire bridging it to J2. The analyzer incorrectly places J2.1 and J3.1 on the +BATT net, likely due to proximity-based net assignment rather than strict wire-connected tracing. The connectivity_issues output reports no unconnected pins, which is also wrong — J2/J3 should appear as single-pin nets or unconnected.
  (signal_analysis)

### Missed
- The usb_compliance field in the v1 output is an empty object {}, whereas the v1.1 output produces a full USB compliance report (CC pulldown checks, ESD checks, decoupling checks). The v1 design has the same USB circuit as v1.1 (J9 USB-C, R1/R2 5k1 CC pulldowns, U3 USBLC6-4). The absence of USB compliance analysis is likely caused by downstream effects of the pin numbering errors: since D+/D- are assigned to wrong U1 pins (PA1/PA2 instead of PA9-PA12), the USB topology detector may fail to recognize the USB circuit.
  (signal_analysis)

### Suggestions
(none)

---
