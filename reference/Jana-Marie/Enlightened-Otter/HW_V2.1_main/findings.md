# Findings: Jana-Marie/Enlightened-Otter / HW_V2.1_main

## FND-00000533: T2 (tactile button) misclassified as 'transformer' type due to 'T' reference prefix; U3 (BY25Q64ASSIG SPI flash) has pins:[] due to unresolved custom library symbol; SPI bus between U5 (ESP8266EX) ...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: HW_V2.1_cpu.sch.json
- **Created**: 2026-03-23

### Correct
(none)

### Incorrect
- T2 is a Panasonic_EVQPUL_EVQPUC tactile push button. The analyzer classifies it as component_type='transformer' because it matches the T-prefix heuristic intended for transformers. The lib_id is 'otter:Panasonic_EVQPUL_EVQPUC' and the value is 'Panasonic_EVQPUL_EVQPUC'. This misclassification also propagates to the aggregated main.sch.json output. The T-prefix rule should only apply when the lib_id or value also suggest a transformer (e.g., contains 'trafo', 'transformer', 'xfmr'), not blindly to all T-prefixed refs.
  (signal_analysis)
- U3 uses lib_id 'otter:W25Q64', a custom library symbol. The analyzer outputs pins:[] for U3, meaning no pin-to-net mappings were resolved. The schematic source shows U3 has pins connected to named nets: ESP_SO, ESP_SI, ESP_CLK, ESP_CS, VCC/3V3ESP, GND. The empty pins list is a consequence of the analyzer not being able to load the custom 'otter' library. This is a known limitation but causes cascading failures in SPI detection and power domain analysis.
  (signal_analysis)
- In main.sch.json, the design_observations section for the I2C SDA net reports has_pullup:false and similarly for SCL. However, the bus_analysis.i2c section correctly identifies R20 and R22 as pullup resistors on SDA and SCL respectively (connecting to 3V3). The two analysis passes produce contradictory results for the same property. The bus_analysis result is correct per the schematic source. The design_observations pullup detection appears to have a bug where it fails to find pullups that bus_analysis finds correctly.
  (signal_analysis)
- In cpu.sch.json (single-sheet parse), U1's NRST pin is reported as connected to net 'ICOMP2'. The schematic source shows a Text GLabel 'NRST' at the pin, meaning the pin should be on the 'NRST' net. The 'ICOMP2' mapping is incorrect and appears to be a net-resolution error in the single-sheet parse context where global labels may not be fully resolved. In the aggregated main.sch.json the mapping may differ. This could indicate a positional wire-tracing bug where the nearest label to a pin is incorrectly associated.
  (signal_analysis)
- In main.sch.json power_domains, U3 (BY25Q64ASSIG SPI flash) is shown connected only to GND with no positive supply rail listed. The schematic connects U3's VCC pin to the 3V3ESP net. Because U3 has pins:[], the power domain analyzer cannot find the VCC pin and therefore cannot determine the positive supply rail. A component with a known VCC/power supply pin connected to a power net should have that rail reflected in its power domain entry.
  (signal_analysis)
- FB1 and FB2 are ferrite beads using lib_id 'otter:BLM18AG601SN1D' (custom library). Both show pins:[] in the analyzer output. The schematic source shows each ferrite bead has two pins (1 and 2) connecting the 3V3 rail to the 3V3ESP and 3V3MCU filtered rails respectively. The empty pins list prevents the analyzer from understanding the power filtering topology these components implement.
  (signal_analysis)
- U6 is a BS801B capacitive touch sensor using lib_id 'otter:BS801B'. It shows pins:[] in the analyzer output. The schematic source shows U6 has pins connected to VDD (3V3MCU), GND, and a touch sense output connected to an STM32 GPIO. The empty pins list means U6's net connections are invisible to the analyzer's signal path and power domain analysis.
  (signal_analysis)

### Missed
- The schematic has explicit named nets ESP_SO, ESP_SI, ESP_CLK, ESP_CS connecting U5 (ESP8266EX, the SPI master) to U3 (BY25Q64ASSIG SPI flash). The analyzer outputs spi:[] in both cpu.sch.json and main.sch.json. The root cause is U3's pins:[] preventing the detector from finding the shared nets, combined with the SPI signal-name heuristic apparently not triggering on U5's pin-net mappings alone. The memory_interfaces section in main.sch.json does partially recognize the U3↔U5 connection (2 shared_signal_nets) but does not promote this to a full SPI bus detection.
  (signal_analysis)
- cpu.sch contains two crystal circuits: XT1 (6MHz, lib: Crystal) with load capacitors C10 and C12 connected to STM32F334 U1 pins OSC_IN/OSC_OUT, and XT2 (6MHz, lib: Crystal) with load capacitors C39 and C44 connected to ESP8266EX U5 pins XTAL_I/XTAL_O. The analyzer outputs crystal_circuits:[] in both cpu.sch.json and main.sch.json. The crystals do appear in the BOM as component_type='crystal', so the classification is correct, but the circuit topology (crystal + capacitors + IC pins) is not assembled into a crystal_circuits detection entry.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00000534: SK6812 LEDs (LED1-LED5, LED9) not detected as a daisy chain — all appear as chain_length=1; AnodeW1, AnodeC1, KathodeW1, KathodeC1 (M3 mechanical screw anodes/cathodes) misclassified as 'ic' type; ...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: HW_V2.1_power.sch.json
- **Created**: 2026-03-23

### Correct
(none)

### Incorrect
- power.sch contains four mechanical connection points (M3 screw terminals used as anode/cathode contacts for the electroluminescent wire drive circuit): AnodeW1, AnodeC1, KathodeW1, KathodeC1. Their lib_id values are custom 'otter:*' symbols. The analyzer classifies all four as component_type='ic'. These are mechanical/connector components, not ICs. The misclassification is likely due to the 'ic' being the fallback type when the lib_id and value do not match any known component pattern and no reference prefix heuristic applies.
  (signal_analysis)
- power.sch contains U4, a MCP6L2T-E/MS dual op-amp (using lib_id 'Device:LM358'). The analyzer detects 3 op-amp units (U4, U4A?, U4B? — the dual op-amp appears split into sub-units). All three units report configuration='unknown' in the op_amp_circuits analysis. The schematic shows one unit wired as a comparator (with feedback) and the power unit. A correct analysis should identify at least one unit as a comparator configuration based on the feedback network present.
  (signal_analysis)

### Missed
- power.sch contains 6 SK6812 MINI-E addressable LEDs (LED1, LED2, LED3, LED4, LED5, LED9) wired in a daisy chain with DOUT of each LED connected to DIN of the next. The analyzer reports each LED as a separate addressable_led_chains entry with chain_length=1 rather than detecting the DOUT→DIN topology and reporting a single chain of length 6. The same issue is present in main.sch.json. The daisy-chain detection requires tracing DOUT nets to DIN pins across components; the same failure likely affects other SK6812/WS2812 designs in the corpus.
  (signal_analysis)
- power.sch contains two MIC4416YC5-TR MOSFET gate driver ICs (IC2, IC3, SOT-143) driving Q2 and Q3 (NTMS4816NR2G N-channel MOSFETs) via gate resistors R35/R38. The transistor_circuits section correctly detects Q2 and Q3 with their gate resistors, but reports gate_driver_ics:[] for both — IC2 and IC3 are not identified as the gate drivers. The MIC4416 output pins are connected to the gate resistors and should be traced back to IC2/IC3 to populate gate_driver_ics.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00000535: IC1 (RT9466 battery charger) missing from SCL net in I2C bus analysis

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: HW_V2.1_main.sch.json
- **Created**: 2026-03-23

### Correct
(none)

### Incorrect
(none)

### Missed
- main.sch contains IC1 (RT9466 battery charger IC) which has both SDA and SCL pins connected to the I2C bus. The bus_analysis.i2c section in main.sch.json correctly lists IC1 on the SDA net, but the SCL net analysis only lists U1 (STM32F334) as a device — IC1 is absent from the SCL entry. This asymmetry (IC1 on SDA but not SCL) suggests an incomplete net trace for the SCL global label in the hierarchical context, or a pin-mapping issue where IC1's SCL pin is not resolved to the SCL net.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00000536: T2 (Panasonic_EVQPUL_EVQPUC tactile switch) classified as 'transformer'; FDN360P P-channel MOSFETs (Q1, Q4) have is_pchannel=False; XT1 and XT2 (6 MHz crystals with lib_id EO:Crystal_6MHz_HC49_US) ...

- **Status**: new
- **Analyzer**: schematic
- **Source**: HW_V2.1_cpu.sch.json
- **Created**: 2026-03-23

### Correct
(none)

### Incorrect
- T2 has lib_id 'EO:TS-1136EVW' and footprint 'Button_Switch_SMD:Panasonic_EVQPUL_EVQPUC'. The reference prefix 'T' is being interpreted as transformer, but the footprint and lib name clearly indicate a tactile switch. Should be classified as 'switch' or 'other'.
  (signal_analysis)
- FDN360P has 'P' suffix indicating P-channel, and the lib_id is 'EO:PEMOS-GSD-3' (PEMOS = P-channel EMOS/enhancement MOSFET). The analyzer reports is_pchannel=False for both Q1 and Q4. Additionally Q1 shows drain_net==source_net ('__unnamed_19'), suggesting a net tracing issue for that device.
  (signal_analysis)
- Two HC-49 crystals (XT1, XT2) are present with load capacitors C12/C10/C9/C44/C39/C59 (18p 50V), but crystal_circuits is empty. The crystal detector is likely missing these because the library prefix is 'EO:' (custom library) rather than a standard KiCad Crystal library identifier.
  (signal_analysis)
- U2 Vout pin is on net '__unnamed_16' which only has U2 connected — the LDO output is not traced through to the 3V3 power net. This is likely because the output wire connects to the #3V0108 power symbol (3V3) nearby (at 9800,1600) but the net tracer doesn't associate the LDO output wire with the named power rail. The output_rail should be '3V3'.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00000537: SPI bus between ESP8266 (U5) and W25Q64 flash (U3) not detected in bus_analysis.spi; Hierarchical schematic correctly parsed all 3 sheets (main, power, cpu); Addressable LED chains (SK6812) correct...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: HW_V2.1_main.sch.json
- **Created**: 2026-03-23

### Correct
- main.sch reports sheets_parsed=3 covering main.sch, power.sch, cpu.sch. Component totals (173 components, 49 unique parts, 213 nets) are plausible for this multi-sheet design. Power rails include all expected rails: 3V3, GND, VBAT, VBAT+, VBUS, VSYS, VSYS_SK6812, GNDD.
- Six single-LED SK6812 chains detected (LED1-LED5 on power sheet, plus related chains). Protocol correctly identified as 'single-wire (WS2812)' with 60mA estimated current per LED. The SK6812_EN gate-switched power supply (Q4) is also correctly identified.

### Incorrect
- Nets ESP_CS, ESP_CLK, ESP_SI, ESP_SO clearly form an SPI bus between U5 (ESP8266EX) and U3 (BY25Q64ASSIG flash). The memory_interfaces detector correctly identifies the U3/U5 link (with shared_signal_nets=2, which itself seems low — 4 SPI signals exist), but the SPI bus analyzer returns an empty list. The bus detector is likely missing SPI because the signal names use 'ESP_' prefix rather than conventional MOSI/MISO/SCK names.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00000538: Power sheet opamp detection (U4 MCP6L2T-E/MS) and RC filter detection look correct

- **Status**: new
- **Analyzer**: schematic
- **Source**: HW_V2.1_power.sch.json
- **Created**: 2026-03-23

### Correct
- 3 opamp circuit instances detected for U4 (dual-opamp used in 3 configurations). RC filters on KathodeW line detected correctly at 15.92 kHz cutoff. These findings are consistent with a motor current-sense + comparator circuit.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
