# Findings: fire-h0und/FlatPort / FlatPort

## FND-00000553: BT1 (SW_Push, value='BOOT') misclassified as battery instead of switch; RS1 (SW_Push, value='RESET') misclassified as resistor instead of switch; component_types reports battery:1 and resistor:9 du...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: FlatPort.kicad_sch.json
- **Created**: 2026-03-23

### Correct
- Y1 and Y2 crystal load cap calculations (13pF and 8pF effective), U4 LDO detection, and 3V3 decoupling cap enumeration all match the source schematic accurately.

### Incorrect
- BT1 uses lib_id 'Switch:SW_Push' and is a push button for BOOT mode, but the analyzer classifies it as type='battery' and category='battery', presumably because the ref prefix 'BT' triggers battery detection. This inflates battery count to 1 and undercounts switches.
  (signal_analysis)
- RS1 uses lib_id 'Switch:SW_Push' and is a push button for RESET, but the analyzer classifies it as type='resistor' and category='resistor'. The ref prefix 'RS' apparently triggers resistor detection. This inflates resistor count from 8 to 9.
  (signal_analysis)
- Correct counts should be: resistor:8, switch:2, battery:0. The statistics section reflects the individual component misclassifications of BT1 and RS1.
  (signal_analysis)
- The differential_pairs entry for USB_D+/USB_D- shows has_esd:false. However, U3 (USBLC6-2SC6) is correctly detected as an ESD protection device in protection_devices. The two detectors are not cross-linked, causing the false negative on USB ESD coverage.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00000554: SC1-SC4 (lib_id='D', solar cells) misclassified as switch instead of diode; VMon1 (TPS3839 voltage supervisor) misclassified as varistor; MOSFET Q1 transistor circuit detection is mostly correct; N...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: _home_aklofas_Projects_kicad-happy-testharness_repos_FlexSpinner_FlexSpinner.sch.json
- **Created**: 2026-03-23

### Correct
- Q1 N-MOSFET is correctly identified with gate_net=VTrig, gate_pulldown=Rpd1(1M), and drain/source nets identified. The detection of gate resistors and pulldown is accurate.

### Incorrect
- The four solar cell components use the KiCad 5 'D' diode symbol. The analyzer classifies them as type='switch' and the BOM groups them as type='switch'. They should be type='diode'. The component_types shows switch:4 and diode:1 (DHold1), but it should be diode:5.
  (signal_analysis)
- VMon1 uses lib_id 'TPS3839-SOT-23', a voltage supervisor/watchdog IC. The analyzer classifies it as type='varistor' and in protection_devices as type='varistor'. It should be classified as an IC or voltage monitor. This also causes it to appear in protection_devices with an irrelevant 'clamp_net' framing.
  (signal_analysis)

### Missed
- DHold1 (Schottky) + CHold1 (47nF) form a peak-hold/sample circuit off VSense, but neither voltage_dividers nor rc_filters detects this. The snubbers list is also empty. This is a meaningful signal path that the analyzer misses.
  (signal_analysis)

### Suggestions
(none)

---
