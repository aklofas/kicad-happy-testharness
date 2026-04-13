# Findings: greatscottgadgets/hackrf / hardware_LNA915

## FND-00002157: RF switches and CPLD falsely classified as active oscillators due to 'sg-' keyword matching 'gsg-symbols' library name; Test coverage classifies 17 RF and I2S signals as 'uart' due to overly broad ...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: schematic_hackrf_hardware_hackrf-one_hackrf-one.kicad_sch.json
- **Created**: 2026-03-24

### Correct
- The RF chain detector correctly assembles the HackRF One signal chain from the hierarchical schematic (4 sheets parsed). It identifies all SKY13453 and SKY13317 RF switches, the RFFC5072 wideband fractional-N IQ mixer, MGA-81563 LNA amplifiers, MAX2837 transceiver (from the baseband sub-sheet), DEA/LP0603 filters, and four baluns. Net connections between RF switch stages are traced correctly (e.g., !MIX_BYPASS, RX, TX_AMP/AMP_BYPASS paths). Total RF component count of 20 is accurate.
- The differential pair detector correctly identifies 10 differential pairs: USB DP/DM, RFFC5072 CPOUT+/-, and all four I/Q baseband pairs (RXBBQ+/-, RXBBI+/-, TXBBI+/-, TXBBQ+/- from MAX2837 to connectors with series termination resistors), plus IA+/-, QA+/-, ID+/-, QD+/- from the MAX5864 high-speed ADC/DAC. ESD protection is attributed to the ICs and series resistors are correctly identified per pair. This is accurate detection of a complex RF transceiver's differential signal topology.
- The USB compliance checker reports vbus_esd_protection as 'fail' for J1 (USB-MICRO-B). Investigation shows U15 is a LXES1TBCC2-004 TVS device (value='TVS') on the VBUS net. The checker correctly flags this because the ESD IC check looks for dedicated USB ESD protection ICs (type recognition), and a generic TVS diode categorized as type='ic' with value='TVS' does not trigger the USB ESD IC pass condition. This is borderline behavior — a TVS is legitimate ESD protection — but the distinction between a general TVS and a USB-specific ESD array is meaningful for compliance checking purposes.

### Incorrect
- The oscillator keyword 'sg-' (intended to match SG-series oscillators from Epson/SG Micro) accidentally matches any lib_id containing 'gsg-symbols' — the hackrf project's custom symbol library prefix. This causes 7x SKY13453 RF SPDT switches (U1, U2, U5, U6, U7, U10, U11) and the XC2C64A CPLD (U24) to appear in crystal_circuits as type='active_oscillator'. The exclude list contains 'spdt' but that string is not present in 'SKY13453' or the lib_id 'gsg-symbols:SKY13453', so the exclusion fails. These 8 false entries pollute the crystal_circuits output.
  (signal_analysis)
- The test_coverage uncovered_key_nets classifier uses patterns 'TX' and 'RX' to identify UART nets. These substrings match RF and baseband signal names: RXBBQ+/-, RXBBI+/-, TXBBI+/-, TXBBQ+/- (MAX2837 I/Q baseband differential pairs), RX_IF, TX_IF (intermediate frequency signals), RX_AMP_IN/OUT, TX_AMP_IN/OUT (RF amplifier connections), and I2S0_RX_WS, I2S0_RX_MCLK, I2S0_TX_MCLK (I2S audio signals). Only U0_TXD and U0_RXD are actual UART nets. Additionally I2S0_RX_SDA is falsely classified as 'i2c' because its name contains 'SDA'. The net_classification itself correctly labels these as 'data', 'clock', or 'analog', but test_coverage uses independent simple pattern matching.
  (test_coverage)

### Missed
- When the MCU sub-sheet (hardware_hackrf-one_mcu.kicad_sch) is analyzed independently, it reports I2C1_SDA and I2C1_SCL with has_pullup=false. In the top-level aggregated analysis (hackrf-one.kicad_sch), the same nets still report has_pullup=false. However, these are hierarchical labels that connect to a separate I2C bus serviced by R19/R20 pull-ups visible in the mcu.kicad_sch sheet. The pullups R27/R28 correctly serve the SDA/SCL nets while the I2C1_SDA/I2C1_SCL nets (routed to an external GPIO connector) legitimately may lack pull-ups — this is actually correct behavior in context, as the external host provides those pull-ups.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00002158: KiCad 5 PCBs with custom copper layer names (C1F/C4B) report front_side=0, back_side=0, copper_layers_used=0

- **Status**: promoted
- **Analyzer**: pcb
- **Source**: pcb_hackrf_hardware_marzipan_marzipan.kicad_pcb.json
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
- Three KiCad 5 legacy PCBs in the hackrf repo use non-standard copper layer names: C1F (front copper), C2, C3, C4B (back copper) instead of the standard F.Cu, In1.Cu, In2.Cu, B.Cu. The PCB analyzer only recognizes the canonical KiCad names. As a result, marzipan reports front_side=0/back_side=0 for 432 modules (all actually on C1F), neapolitan reports front_side=0/back_side=0 for 290 modules, and operacake reports front_side=0/back_side=0 for 152 modules (122 on C1F and 30 on C4B). copper_layers_used=0 and copper_layer_names=[] are also wrong for all three. operacake's 30 back-side components are completely invisible to the analyzer.
  (statistics)

### Missed
(none)

### Suggestions
(none)

---

## FND-00002159: operacake back-side component count is 0 when 30 components are actually on the back copper layer C4B

- **Status**: promoted
- **Analyzer**: pcb
- **Source**: pcb_hackrf_hardware_operacake_operacake.kicad_pcb.json
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
- The operacake.kicad_pcb defines its layers with custom names: layer 0 = C1F (front) and layer 31 = C4B (back). Analysis of the actual file confirms 122 modules on C1F and 30 modules on C4B. Because the PCB analyzer looks for the string 'B.Cu' to count back-side components, the 30 components on C4B are counted as neither front nor back, yielding footprint_count=152 but front_side=0, back_side=0. This affects DFM, assembly complexity, and placement analysis.
  (statistics)

### Missed
(none)

### Suggestions
(none)

---

## FND-00002160: RF matching networks not detected in the RF frontend despite 74 capacitors and 7 inductors forming explicit impedance matching around mixers and baluns

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: schematic_hackrf_hardware_hackrf-one_frontend.kicad_sch.json
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
(none)

### Missed
- The hackrf-one frontend sheet contains explicit RF impedance matching LC networks around the RFFC5072 mixer inputs/outputs (via T1 MIX_IN_BALUN and T2 MIX_OUT_BALUN), around the RX/TX baluns (T3 RX_BALUN, T4 TX_BALUN), and around each of the 10 RF switches. The 33pF capacitors (24 instances) are specifically chosen for 50-ohm matching at the target frequencies. rf_matching returns [] for all hackrf schematic files. The same is true for the marzipan, neapolitan, lollipop, and jawbreaker frontend sheets. The RF matching detector appears to only look for explicit antenna-to-IC single-stage pi/L/T networks, missing distributed switch-network matching topologies.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00002161: RF chain connection between LNA (U3/BGB741L7ESD) and SAW filter (U4/FAR-F5QA) not detected despite direct signal path

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: schematic_hackrf_hardware_LNA915_LNA915.sch.json
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
- The LNA915 is a 915 MHz low-noise amplifier board with a BGB741L7ESD LNA (U3) driving a FAR-F5QA SAW filter (U4). The RF chain correctly identifies both components (1 amplifier + 1 filter, total_rf_components=2) but shows connections=[] — no connection between U3 and U4 is traced. This is a KiCad 5 legacy schematic; all nets in the output have empty component lists (the net-to-component mapping is not populated for legacy format), which prevents the connection tracing algorithm from finding shared nets between the LNA output and the SAW filter input.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00002162: I2C pullup correctly reported as absent for operacake PCA9557 I2C GPIO expander since R7/R8 pullups are DNP

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: schematic_hackrf_hardware_operacake_operacake.sch.json
- **Created**: 2026-03-24

### Correct
- The operacake board has an I2C GPIO expander (U4/PCA9557) on the SCL/SDA bus. Pull-up resistors R7 and R8 (1.8k each) are present in the schematic but marked DNP (Do Not Populate) — operacake relies on the host HackRF board to supply I2C pull-ups. The analyzer correctly identifies has_pullup=false for both SCL and SDA since DNP components are excluded from analysis. The DNP count of 41 components is also correctly reported in statistics.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
