# Findings: SparkFun_GNSS_LG580P / Hardware_Production_SparkFun_GNSS_LG580P_panelized

## FND-00001427: Component count, power rails, and regulator detection are accurate; SPI bus not enumerated in signal_analysis despite PICO/POCI/SCK/~{CS} nets present; LC filter double-counting: each inductor appe...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: Hardware_SparkFun_GNSS_LG580P.kicad_sch
- **Created**: 2026-03-24

### Correct
- 77 total components matches the sum of component_types exactly. Power rails [3.3V, 5V, GND] are correct — unlike DAN-F10N, the LG580P design does not expose VCC_RF or VDD as separate named rails. The RT9080-3.3 LDO (U2) is correctly identified as 5V→3.3V. RC filters on both ANT_IN1 and ANT_IN2 supply lines (R12+C14||C15 and R6+C3||C4) are correctly detected at 159 kHz each.

### Incorrect
- L1 and L2 (both 68nH) each appear in two LC filter entries: once paired with a single 100pF cap (61 MHz resonance) and once with a parallel 100pF+100pF network (1.93 MHz resonance). The actual circuit has each inductor forming a Pi-network supply filter with two caps on the output node. The same inductor being reported in two separate LC filter instances inflates the lc_filters count from 2 to 4 and the lower-frequency 1.93 MHz entries are an artifact of the parallel cap expansion logic treating the combined node as a separate LC pair.
  (signal_analysis)

### Missed
- The design has SPI nets PICO, POCI, SCK, ~{CS} (visible in net list and test_coverage uncovered_key_nets which lists SCK as category 'spi'). The signal_analysis.spi_buses key is None rather than a list of detected SPI buses. The I2C bus with SCL/SDA (connecting to U3 LG580P module) appears only in design_observations as i2c_bus category items, not as a structured i2c_buses list. Both bus detectors produce no structured output despite clear evidence of both buses in the netlist.
  (statistics)

### Suggestions
(none)

---

## FND-00001428: Board dimensions, footprint count, and routing are accurate for a dual-GNSS breakout; Layers list incorrectly counts Edge.Cuts as a copper layer, showing 5 instead of 4

- **Status**: promoted
- **Analyzer**: pcb
- **Source**: Hardware_SparkFun_GNSS_LG580P.kicad_pcb
- **Created**: 2026-03-24

### Correct
- Board 50.8×43.18 mm = exactly 2.0"×1.7" (SparkFun standard). 160 footprints for 77 schematic components reflects ~70 kibuzzard decoration footprints. 232 vias is appropriate for a 51×43 mm 4-layer board with a high-pin-count GNSS module (U3 has 747 gerber pad entries in the panelized view). The thermal_pad_vias analysis correctly detects U4's 2.7×2.7 mm heatsink pad on GND.

### Incorrect
- The layers list contains 5 entries matching 'Cu' in name: F.Cu (0), In1.Cu (4), In2.Cu (6), B.Cu (2), and Edge.Cuts (25). The string 'Cu' is a substring of 'Edge.Cuts', causing Edge.Cuts to be included in copper layer counts derived by string matching. The statistics.copper_layers_used=4 is correct. The layers list count of 5 is wrong for consumers doing their own filtering. This affects all three designs identically.
  (statistics)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001429: HeatsinkPad aperture function detection and F.Cu net count are accurate; GKO layer_type incorrectly assigned as B.Mask (same issue as DAN-F10N and Flex_pHAT)

- **Status**: promoted
- **Analyzer**: gerber
- **Source**: Hardware_Production
- **Created**: 2026-03-24

### Correct
- The F.Cu (GTL) layer correctly identifies HeatsinkPad aperture function with 9 flashes — matching the LG580P module's large thermal pad (U3, 3×3 via array). The x2_net_count=100 on the F.Cu layer matches the schematic's total_nets=99 (within 1, likely due to net 0 / no-net pads). The 154 unique component refs in the panelized gerber with 72 kibuzzard items leaves 80 real components matching the LG580P's 77 schematic components (plus 3 extra for multi-part or mechanical items).

### Incorrect
- The SparkFun_GNSS_LG580P_panelized.GKO file has X2 FileFunction='Soldermask,Bot' and layer_type='B.Mask' in the output, while its aperture_analysis shows Profile=1 confirming it is the board outline (Edge.Cuts). This is the same bug as in the other two repos. The GKO extension is a recognized KiCad/RS-274X convention for Edge.Cuts, and the Profile aperture function attribute is the definitive indicator. The analyzer should prioritize the Profile aperture function or .GKO extension over the X2 FileFunction for layer type classification.
  (completeness)

### Missed
(none)

### Suggestions
(none)

---
