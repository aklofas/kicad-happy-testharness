# Findings: StrawberryTurtle/AnothaOne / Kicad_AnothaOne_2

## FND-00000378: U1 pin-to-net mapping is incorrect throughout when global labels connect pins without wires; I2C bus falsely detected on K2/K3 nets due to wrong pin-net mapping; Bus width for K-prefix signals repo...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: Kicad_AnothaOne_2.kicad_sch.json
- **Created**: 2026-03-23

### Correct
- The schematic has total_wires=0 — all connectivity is via global labels placed directly at pin endpoints. The analyzer fails to resolve these label-to-pin connections and produces wrong net assignments for the XIAO (U1). Geometrically: left-side pin 1(A2)→K4, pin 2(A4)→K3, pin 3(A10)→K2, pin 6(A9_SCL)→GND; right-side pin 14(5V)→K5, pin 12(3V3)→K7, pin 13(GND)→K6, pin 9(A7_SCK)→GND. The analyzer instead reports pin 1→__unnamed_0, pin 2→GND, pin 3→__unnamed_1, pin 6→K3, pin 12→__unnamed_7, pin 13→GND, pin 14→__unnamed_6, etc. Pins 5(A8_SDA), 7(B8_TX), 8(B9_RX), 10(A5_MISO) are unconnected but the analyzer assigns them K2, K4, K5, K7 respectively. Only the center pins (4→K1, 11→K8) are correctly mapped.
- bus_topology.detected_bus_signals reports {prefix: 'K', width: 16, range: 'K1..K8'}. The range K1..K8 contains exactly 8 unique nets, so width should be 8. The overcounted value of 16 equals the total number of global label instances (each of K1–K8 appears twice in the schematic: once as 'output' shape near the switch side and once as 'input' shape near the XIAO side). The analyzer is counting label instances rather than unique net names for bus width.
- assembly_complexity reports smd_count=8 (for S1–S8) and tht_count=1 (for U1 XIAO). All 8 Kailh Choc V1 switches (footprints ScottoKeebs_Choc:Choc_V1_1.00u, Choc_V1_1.50u, Choc_V1_2.00u) are through-hole PCB-mount components, not SMD. The correct counts should be tht_count=9, smd_count=0. Additionally, unique_footprints is reported as 2 (likely collapsing all Choc variants to one group) rather than the correct 4 distinct footprints (Choc_V1_1.00u, Choc_V1_1.50u, Choc_V1_2.00u, XIAO-nRF52840-DIP).

### Incorrect
- design_analysis.bus_analysis.i2c reports an I2C bus on nets K2 (SDA) and K3 (SCL) because U1 pin 5 (A8_SDA) is incorrectly mapped to K2 and pin 6 (A9_SCL) is incorrectly mapped to K3. In reality, pin 6 (A9_SCL) connects to GND and pin 5 is unconnected. Even with correct connectivity, K2 and K3 are plain GPIO lines running to key switches S2 and S3 — there are no I2C peripheral devices present. There are no pull-up resistors anywhere in the design. This is a pure false positive.
  (design_analysis)

### Missed
(none)

### Suggestions
(none)

---
