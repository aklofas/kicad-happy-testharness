# Findings: sporkus/le_chiffre_keyboard_stm32 / kicad_pcb_stm32_hotswap_chiffre

## FND-00002375: USB CC1/CC2 pulldown check incorrectly fails — 5.1k resistors are present but on unnamed nets; Decoupling observations incorrectly flag missing caps for STM32 and LDO that actually have decoupling;...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: schematic_le_chiffre_keyboard_stm32_kicad_pcb_stm32_hotswap_chiffre.kicad_sch.json
- **Created**: 2026-03-24

### Correct
- The 36-key le_chiffre keyboard matrix is correctly detected with all 4 row nets and 10 column nets. The analyzer correctly reports 36 switches on the matrix against a 4x10=40-capacity grid, accurately reflecting the partially-populated layout. The 11-LED SK6812MINI addressable chain (D101-D111) is also correctly identified with single-wire WS2812 protocol and 660mA estimated current.

### Incorrect
- The USB compliance check reports cc1_pulldown_5k1 and cc2_pulldown_5k1 as 'fail', but there are two unannotated 5.1k R? resistors that connect directly to J1 pin A5 (CC1) and J1 pin B5 (CC2) via unnamed nets __unnamed_0 and __unnamed_2. The other ends connect to GND (confirmed in the GND net pin list). The correct resistors exist — the analyzer fails to find them because the USB compliance checker does not resolve CC pin connections through unnamed intermediate nets to locate pulldown resistors.
  (usb_compliance)
- design_observations reports that U1 (STM32F072CBT6) lacks +3V3 decoupling and U? (XC6206 LDO) lacks both +5V and +3V3 caps. However, there are 9 unannotated C? capacitors (100nF and 1uF) all on the GND net, some also on +3V3. Because the components are unannotated (reference = 'C?'), the analyzer cannot resolve their net connections via pin_connections (which is empty for all C?), so it treats them as unconnected. The decoupling check fails to handle unannotated components connected via net membership in the pins list.
  (signal_analysis)

### Missed
- The schematic has a full USB 2.0 device stack: USB-C connector (J1), PRTR5V0U2X ESD protection on D_P/D_N, a polyfuse (F1) on VBUS, and an STM32F072CBT6 which has a built-in USB FS peripheral. Despite having all these signals (VBUS, D_P, D_N), the bus_topology.detected_bus_signals contains only GPIO port prefixes (A, B, C, F) and the key matrix signals. No USB peripheral interface is reported in bus_topology or signal_analysis.
  (signal_analysis)

### Suggestions
(none)

---
