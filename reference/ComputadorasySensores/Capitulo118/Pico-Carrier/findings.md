# Findings: ComputadorasySensores/Capitulo118 / Pico-Carrier

## FND-00000426: PWR_FLAG warning for GND is incorrect — PWR_FLAG IS connected to GND via wire; I2C bus not detected despite explicit SDA and SCL nets connecting four components; Assembly complexity misclassifies a...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: Pico-Carrier.kicad_sch.json
- **Created**: 2026-03-23

### Correct
(none)

### Incorrect
- The schematic has a PWR_FLAG symbol (#FLG01) at (71.12, 95.25) connected by a wire to the GND symbol at (71.12, 99.06). The PWR_FLAG pin is therefore on the GND net. However, the analyzer fails to include #FLG01's pin in the GND net's pin list and generates a spurious pwr_flag_warning: 'Power rail GND has power_in pins but no power_out or PWR_FLAG'. The wire connection (71.12,95.25)→(71.12,99.06) is present in the schematic file and the PWR_FLAG symbol is listed in power_symbols.
  (pwr_flag_warnings)
- All 9 components in this design are through-hole (THT): J1–J8 use Connector_PinSocket_2.54mm and Connector_PinHeader_2.54mm Vertical footprints (all THT), and SW1 uses Button_Switch_THT:SW_PUSH_6mm. The analyzer reports smd_count=8 and tht_count=1 with package_breakdown={other_SMD:8, THT:1}. The correct values are smd_count=0 and tht_count=9. The assembly SMD/THT classifier does not recognize 'PinSocket' and 'PinHeader' footprint library prefixes as THT.
  (assembly_complexity)
- The BOM has 9 components across 6 distinct footprint strings: PinSocket_1x20, PinSocket_1x04, PinSocket_1x06, PinHeader_1x03, PinHeader_1x20 (all Connector_*_2.54mm), and Button_Switch_THT:SW_PUSH_6mm. The analyzer reports unique_footprints=2, which is severely under-counted. This likely results from the same misclassification that treats most connectors as a single SMD 'other_SMD' bucket rather than counting distinct footprint strings.
  (assembly_complexity)

### Missed
- The schematic has nets explicitly named 'SDA' and 'SCL', each connecting four components: J3 (OLED connector), J6 (BMP-BME280 connector), J1 (Pico socket side 1), and J7 (Pico header side 1). This is a clear I2C bus topology. However, design_analysis.bus_analysis.i2c is an empty list. The test_coverage section correctly identifies SCL and SDA as 'i2c' category nets, confirming the omission in bus_analysis. The I2C detector likely requires an IC component with typed I2C pins rather than accepting named SDA/SCL nets on connectors.
  (design_analysis)

### Suggestions
(none)

---
