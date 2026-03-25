# Findings: Basic_STM32_Bluepill / project_Basic_STM32_Bluepill

## FND-00000387: USB FS pull-up resistor R5 not identified as usb_pullup; USART1 remapped pins not flagged — net name vs actual pin mismatch; BOOT0 switch circuit not detected as boot mode selector; Ferrite bead LC...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: project_Basic_STM32_Bluepill.kicad_sch.json
- **Created**: 2026-03-23

### Correct
(none)

### Incorrect
(none)

### Missed
- R5 (1.5kΩ) connects +3.3V to USB_D+. This is the USB full-speed device mode pull-up resistor per STM32 AN4875 (referenced in a schematic text note). The usb_data design observation for USB_D+ correctly lists R5 in the devices array, but never identifies R5 as a pull-up — the has_esd_protection flag is the only characterization. There is no 'has_pullup' or 'pullup_resistor' field for USB lines the way there is for I2C lines. A 1.5kΩ resistor from a power rail to USB_D+ is a well-known USB FS device pull-up pattern and should be flagged similarly to how I2C pull-ups are annotated.
  (signal_analysis)
- The net USART1_TX connects to U2 pin 42 (PB6) and net USART1_RX connects to U2 pin 43 (PB7). On the STM32F103, the default USART1 pins are PA9 (TX) and PA10 (RX); PB6/PB7 are the AFIO-remapped alternate pins. The analyzer reports this net-to-pin mapping correctly in the nets section, but does not flag in design_observations that the USART1 peripheral is using remapped (alternate function) pins rather than the default mapping. This is a missed observation that could be useful for board validation.
  (signal_analysis)
- SW1 (SW_SPDT) selects between GND (pin A) and +3.3V (pin C) and routes through SW_BOOT0 → R4 (10kΩ) → BOOT0 pin on U2. This is a standard STM32 boot mode selection circuit. The analyzer correctly resolves the net connectivity and exposes the BOOT0 net with R4 as pull-down, but does not produce a design_observation identifying this as a boot mode selector circuit. The schematic even includes a text note 'HIGH - Bootloader Mode / LOW - Run Prog Mode'. This pattern (SPDT switch selecting a logic level for a MCU boot pin) is a recognizable design idiom worth calling out.
  (signal_analysis)
- FB1 (120Ω ferrite bead) is placed in series between the +3.3V digital rail and the +3.3VA analog supply. On the +3.3VA side there are C12 (1µF) and C11 (10nF) decoupling capacitors, while the +3.3V side has its own decoupling caps. This is a classic ferrite bead pi-filter for analog supply isolation. The analyzer correctly identifies FB1 as a ferrite_bead component and shows the separate +3.3VA decoupling analysis, but the lc_filters array is empty — the FB1 + C11/C12 combination is not identified as an LC filter / analog supply isolation circuit. A design_observation noting the VDDA filtering would be appropriate.
  (signal_analysis)

### Suggestions
(none)

---
