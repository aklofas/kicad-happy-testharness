# Findings: embeddedalpha/PCB-Design / GEOLOCX_Trax

## FND-00002605: GPS/LoRa tracker with STM32G473, SX1278, TESEO-LIV3F GNSS, BGA725L6 LNA, PE4259 RF switch, SPI display, and LT1083-3.3 LDO. Analyzer correctly detected RF chain, matching networks, and regulators, but rf_matching has excessive combinatorial explosion.

- **Status**: confirmed
- **Analyzer**: schematic
- **Source**: GEOLOCX_Trax.sch.json

### Correct
- Correctly parsed 5-sheet hierarchy with 92 components including 12 ICs
- RF chain correctly identified with PE4259 switch (U3) and SX1278 transceiver (IC2)
- U4 (LT1083-3.3) correctly detected as LDO with topology=LDO, input_rail=VDD, output_rail=+3.3V, estimated_vout=3.3
- Voltage divider R7/R8 (1K/1K) at 0.5 ratio feeding J9 pin 2 and C51 correctly detected
- ESD protection D1 (SP0503BAHT) correctly detected on USB data lines
- Crystal circuits Y1, Y2 at 32 MHz correctly detected (though load caps missing - likely due to schematic using generic C_Small symbols)
- Decoupling observation for IC1 (W25Q128), IC2 (SX1278), IC3 (STM32G473), U7 (TESEO-LIV3F) noting missing caps is useful design feedback
- USB data net D- correctly flagged with ESD protection, D+ without - accurate since SP0503BAHT only covers 3 lines

### Incorrect
- rf_matching produces 17 entries with massive combinatorial explosion - every LC component in the RF path is treated as a potential antenna with all neighbors listed. L6, L5, C25, C23, C21, L2, C19, C18, C26, C28 each get their own entry. The real matching network is one chain from antenna through L6/L5 to PE4259 and from PE4259 through L3/L2 to SX1278
  (signal_analysis.rf_matching)
- R3 (R_Small) incorrectly listed as antenna in rf_matching with pi_match topology targeting IC2 (SX1278). R3 is a series resistor, not an antenna
  (signal_analysis.rf_matching)
- Components with generic C_Small/L_Small/R_Small values have no actual component values, making matching network analysis meaningless - all values show as 'C_Small' or 'L_Small'
  (signal_analysis.rf_matching)

### Missed
- BGA725L6 (U5) is a GPS LNA, not detected in rf_chains despite being in the RF signal path between antenna and TESEO-LIV3F
  (signal_analysis.rf_chains)
- STC3117 (U8) is a battery fuel gauge IC connected to the battery monitoring circuit - not classified or noted in design_observations
  (signal_analysis.design_observations)
- MCP73113 (U3) is a LiPo battery charger IC - should be detected in bms_systems or at minimum noted as a charger
  (signal_analysis.bms_systems)

### Suggestions
- RF matching detection needs deduplication - instead of N^2 permutations, trace from actual antenna connectors through the matching network to the RF IC
- Add BGA725L6 and similar GPS LNA parts to the rf_chains amplifier detection list
- Add MCP73113/MCP73831 family to bms_systems or charger detection

---
