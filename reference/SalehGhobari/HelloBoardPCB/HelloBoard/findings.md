# Findings: SalehGhobari/HelloBoardPCB / HelloBoard

## FND-00000601: Component counts, BOM, and power rail extraction are accurate; TMP235A2DCKR (temperature sensor) falsely classified as LDO regulator; I2C bus with pullups correctly detected; crystal circuit (16 MH...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: HelloBoard.kicad_sch.json
- **Created**: 2026-03-23

### Correct
- All 36 components correctly identified across 8 categories (6 IC, 6 R, 14 C, 4 connectors, 2 LED, 2 switch, 1 crystal, 1 ferrite). Power rails +3.3V, +3.3VA, VBUS, GND all detected. AMS1117-3.3 LDO correctly identified with VBUS input and +3.3V output.
- I2C_SCL and I2C_SDA nets show U1 (STM32) and U4 (ADXL343) as participants with R2 and R4 (2K2) pullups to +3.3V. Crystal Y1 at 16 MHz with C10/C11 10 pF load caps detected, effective load 8 pF calculated correctly. ERC warnings for NRST and BOOT0 (no active driver, driven only by passive components) are valid.
- RV1 (Bourns 3214W, 10k) is stored in the 'resistor' type bucket. The description field correctly reads 'Potentiometer', so there is no information loss. The BOM correctly separates it from fixed resistors because its footprint differs.

### Incorrect
- U3 (TMP235A2DCKR) is a linear analog temperature sensor with a voltage output proportional to temperature. It has a power supply pin and an analog output (Temp_OUT), which the analyzer pattern-matched as an LDO. This causes a secondary false positive: a 'regulator_caps' design observation warning about missing output capacitors on the Temp_OUT rail, which is not a power rail at all.
  (signal_analysis)
- LCD_E, LCD_RS, LCD_D4–D7 are flagged needs_level_shifter=True because DS2 (WC1602A LCD, VDD=VBUS=5V) shares nets with U1 (STM32, VDD=3.3V). However, the STM32F103's GPIO outputs are 5V-tolerant and the WC1602A datasheet specifies the 5V LCD accepts 3.3V-level inputs without a level shifter. The cross-domain detection is valid structurally, but the level-shifter recommendation is an overreach for 5V-tolerant GPIO scenarios.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00000602: Component extraction, subcircuits, crystal circuit with load caps all correct; Crystal Y1 frequency not extracted from MPN (ABS06-32.768KHz-1-T); ESD protection on USB D+/D- falsely credited to U1 ...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: _home_aklofas_Projects_kicad-happy-testharness_repos_Hostess_FeatherWing_hardware_Hostess Feather.sch.json
- **Created**: 2026-03-23

### Correct
- All 28 components across 7 types correctly parsed from legacy KiCad 5 .sch. Crystal Y1 load cap analysis (C5/C6 22 pF, effective 14 pF) is correct. Differential pair D+/D- detection correct. VBUS_FILTERED decoupling (100 uF + 100 nF) correctly identified.
- The XOUT global label at schematic Y=3150 mils (80.01 mm) connects to U1 pin 40 (~RESET, input type) and Y1 pin 2 + C6 (passive). The coordinate match is exact. Since no bidirectional or output pin drives this net, the no_driver ERC warning is structurally correct. The naming ('XOUT' for the RESET net) appears to be a schematic design issue in the source.

### Incorrect
- The differential_pairs entry reports has_esd=True with esd_protection=['U1']. U1 is the MCU itself, not a dedicated ESD protection device. The design_observations also correctly flags has_esd_protection=False for the D+ net. These two outputs contradict each other. The correct answer is: no dedicated ESD device is present; the MCU's internal clamps do not qualify.
  (signal_analysis)
- The analyzer flags needs_level_shifter=True for FAULT and VBUSEN because U1 (ATSAMD21, +3V3) and U2 (TPS2051, VBUS_FILTERED ~5V) share these nets with different power domains. However, the TPS2051's FAULT pin is open-drain and its EN pin accepts 3.3V logic at 5V VBUS operation; no level shifter is needed. The cross-domain detection is architecturally correct but the level-shifter flag is wrong for this device class.
  (signal_analysis)

### Missed
- Y1 has value 'Crystal' (generic) and MPN 'ABS06-32.768KHz-1-T', which encodes the 32.768 kHz frequency. The analyzer sets frequency=null because it only parses the value field for numeric frequency. The MPN field contains the frequency unambiguously. The load caps (22 pF) are correct for a 32.768 kHz watch crystal.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00000603: Component count, connector types, and BOM accurate for a connector-heavy Nucleo shield; Decoupling analysis empty — C1–C8 on 3.3V rail not detected because 3.3V uses global labels, not power symbol...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: _home_aklofas_Projects_kicad-happy-testharness_repos_HuskyA100_Nucleo_Shield_HuskyA100_Nucleo_Shield.sch.json
- **Created**: 2026-03-23

### Correct
- All 18 components correctly identified: 8 connectors (CN7–CN10, J1–J4), 8 capacitors (C1–C8), 1 LED, 1 resistor. The 106 nets are plausible given the four large Nucleo headers (CN7–CN10 total 100 pins). No false positives in component classification.

### Incorrect
(none)

### Missed
- The 3.3V net (from global_label text) has C1–C8 capacitors (4× 10 nF + 4× 100 nF) connected between it and GND, but decoupling_analysis returns []. The analyzer only identifies power rails from KiCad power symbols (PWR_FLAG, +3V3 etc.), not from global labels named '3.3V' or '5V'. Similarly, power_rails only lists 'GND' (from a power symbol), not '3.3V' or '5V'. This is a systematic gap for label-based power distribution (common in KiCad 5 legacy designs).
  (signal_analysis)
- D1 (LED, 5V-powered via global label) has R1 (66.5 Ω) as a series current-limiting resistor to GND. This is a textbook LED circuit that should appear in design_observations. Instead, subcircuits is empty and design_observations is empty. The absence of power_symbols (no PWR_FLAG, no power ICs) prevents the analysis engine from anchoring the topology.
  (signal_analysis)

### Suggestions
(none)

---
