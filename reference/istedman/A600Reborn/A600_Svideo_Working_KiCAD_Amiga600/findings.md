# Findings: istedman/A600Reborn / A600_Svideo_Working_KiCAD_Amiga600

## FND-00000348: X1 oscillator module misclassified as crystal_circuit; 0.33uF decoupling cap listed as load cap

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: A600_Svideo_Working_KiCAD_Sheet5.sch.json
- **Created**: 2026-03-23

### Correct
(none)

### Incorrect
- X1 (28.37516MHz) has lib_id 'MyLibrary:28.37516MHz', footprint 'MyLibrary:Oscillator', and pins including a 'VCC' power_in pin — it is a 4-pin oscillator module, not a 2-pin crystal. The analyzer detects it in crystal_circuits and assigns C199 (0.33uF) as a load cap. Crystal load caps are 10–33pF; 0.33uF is three orders of magnitude too large and is actually the +5V decoupling capacitor on the oscillator's VCC rail. Oscillator modules are self-contained and need no external load caps.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00000349: X1 oscillator module misclassified as crystal_circuit in multi-sheet analysis; 0.33uF cap listed as load cap; Real crystals Y451 (4.433619MHz PAL color burst) and Y621 (3MHz) not detected in crysta...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: A600_Svideo_Working_KiCAD_Amiga600.sch.json
- **Created**: 2026-03-23

### Correct
(none)

### Incorrect
- In the multi-sheet Amiga600.sch analysis (12 sheets), X1 is the same 4-pin oscillator module as in Sheet5 and is again listed in crystal_circuits with C199 (0.33uF) as a 'load cap'. A 330nF capacitor cannot be a crystal load cap. The oscillator footprint name 'Oscillator' and the presence of a VCC pin are reliable signals that distinguish oscillator modules from crystals.
  (signal_analysis)
- The 4 rf_matching entries all share the same cluster of components: R243 (10K), R242 (6.8K), R241 (4.7K), L241 (1.2uH), C244 (0.01uF), C242 (15pF), C241 (56pF), C243 (1000pF). The schematic note reads 'PAL GOODIES' and this circuit generates the PAL color-burst timing/dot-clock signal for the video chipset. R243 is a series termination resistor on a clock net, not an antenna. L241/C241/C242 form a low-pass filter on the +VID video supply rail. No antenna or transmission-line load is present. The rf_matching detector appears to trigger on any R+L+C cluster without checking for actual antenna/RF context.
  (signal_analysis)

### Missed
- Y451 uses lib_id 'Device:Crystal_GND3_Small' with footprint 'MyLibrary:Crystal' and value '4.433619MHz' — the PAL color subcarrier crystal. Y621 (in Sheet8) uses 'Device:Crystal_Small' with footprint 'MyLibrary:Resonator' and value '3MHz', with proper 22pF load caps C621/C622. Neither is detected in crystal_circuits of the multi-sheet Amiga600.sch output, even though both are standard Device:Crystal* lib IDs. The analyzer catches the oscillator module (X1) but misses both true crystals.
  (signal_analysis)
- Sheet2 contains U16 and U17, both 'MyLibrary:256Kx16' in SOJ-40-40 packages — 256Kx16 DRAM chips forming the Amiga 600's ChipRAM. The multi-sheet Amiga600.sch analysis has memory_interfaces: []. The DRAM address bus uses RAS/CAS multiplexing controlled by AGNUS. The custom IC names (256Kx16 in a private library) rather than standard DRAM part numbers may prevent the detector from recognizing these as memory devices.
  (signal_analysis)

### Suggestions
(none)

---
