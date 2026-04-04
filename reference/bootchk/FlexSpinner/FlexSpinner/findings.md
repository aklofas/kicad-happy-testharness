# Findings: FlexSpinner / FlexSpinner

## FND-00000557: SC1-SC4 (lib_id='D', solar cells) misclassified as switch instead of diode; VMon1 (TPS3839 voltage supervisor) misclassified as varistor; MOSFET Q1 transistor circuit detection is mostly correct; N...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: FlexSpinner.sch.json
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
