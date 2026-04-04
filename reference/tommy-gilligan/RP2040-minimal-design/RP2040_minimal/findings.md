# Findings: RP2040-minimal-design / RP2040_minimal

## FND-00001188: LDO regulator U1 (NCP1117-3.3) detected with correct topology, input/output rails; Crystal Y1 detected with correct load cap circuit (C14/C15 = 27pF, CL_eff = 16.5pF); Crystal frequency parsed as n...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: RP2040_minimal.kicad_sch.json
- **Created**: 2026-03-23

### Correct
- VBUS->+3V3 via NCP1117-3.3, topology=LDO, vref_source=fixed_suffix, estimated_vout=3.3V. All correct.
- Crystal load capacitor pair correctly identified with series combination formula. 16.5pF effective load is reasonable for a 12MHz crystal.
- 27Ω USB series resistors on both D+ and D- detected correctly as dp_series_resistor=pass and dm_series_resistor=pass. VBUS decoupling (C2=10uF) also detected correctly.
- memory_interfaces correctly identifies W25Q128JVS connected to RP2040 via 6 nets (QSPI bus). Total pins=8 is correct for SOIC-8 flash.

### Incorrect
- The crystal value 'ABLS-12.000MHZ-B4-T' contains the frequency '12.000MHZ' but frequency=null in the output. The analyzer fails to extract frequency from this common Abracon part-number format.
  (signal_analysis)
- The schematic analyzer classifies all 34 components as SMD (tht=0), but J1 (2x18 PinHeader), J2 (1x02 PinHeader), and J4 (2x18 PinHeader) use through-hole footprints, consistent with the PCB analyzer which correctly reports tht=3. The schematic-side assembly_complexity is not reading PinHeader footprint names as THT.
  (signal_analysis)
- R1 has value='DNF' which is a common convention for 'Do Not Fit', but dnp=false and it appears in missing_mpn. The analyzer should detect 'DNF' as a do-not-fit indicator and either set dnp=true or exclude from sourcing warnings.
  (signal_analysis)
- The design uses LCSC field for sourcing (not MPN field), which is standard KiCad practice for JLCPCB/LCSC ordering. The sourcing audit reports 0% MPN coverage because 'mpn' is empty, even though LCSC part numbers are present for all parts except R1. The audit should surface LCSC coverage separately or count it in overall sourcing coverage.
  (signal_analysis)

### Missed
- bus_analysis.spi=[] even though U3 (RP2040) connects to U2 (W25Q128JVS) via 6 shared signal nets (QSPI_SS, QSPI_SCLK, QSPI_SD0-SD3). The memory_interfaces section correctly identifies the connection, but the SPI bus detector misses it — likely because the net names use 'QSPI_' prefix rather than 'SPI_' or 'MOSI/MISO/SCK/CS'.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00001189: Legacy .sch parser reports total_nets=79 but design only has ~52 unique nets

- **Status**: new
- **Analyzer**: schematic
- **Source**: RP2040_minimal.sch.json
- **Created**: 2026-03-23

### Correct
(none)

### Incorrect
- The legacy KiCad 5 parser counts 79 nets (48 named + 31 unnamed), significantly overcounting compared to the KiCad 6+ parser (52) and the PCB netlist (52). Many unnamed nets in the legacy parser correspond to wire segments that are really the same net. This inflated net count could mislead assertions.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001190: PCB statistics correct: 34 footprints (27 SMD, 3 THT, 4 mounting holes), 2-layer, fully routed; RP2040 (U3) thermal pad correctly identified with 9 thermal vias, connected to GND; DFM tier=standard...

- **Status**: new
- **Analyzer**: pcb
- **Source**: RP2040_minimal.kicad_pcb.json
- **Created**: 2026-03-23

### Correct
- 34 footprints (27 SMD + 3 THT + 4 mounting holes), 52 nets, 0 unrouted nets, routing_complete=true. Via count 34, track segments 327. All correct.
- thermal_pads detects U3 pad 57 (3.2x3.2mm, 10.24mm²) with 9 footprint via pads on GND. This is the exposed pad / center thermal pad of the QFN-56 package. Correct.
- 0.15mm min track, 0.35mm min drill (via size), 0.125mm annular ring. These are within standard JLCPCB tolerances. dfm_tier=standard is appropriate.
- 17 components flagged as medium tombstoning risk — these are 0402 capacitors where one pad connects to a power rail and the other to GND pour, creating thermal asymmetry. This is a legitimate concern for reflow soldering.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001191: Gerber layer set complete: all required layers present, alignment checks pass; Drill classification correctly separates vias (34×0.35mm PTH), component holes (87 PTH), mounting holes (4×2.7mm NPTH)...

- **Status**: promoted
- **Analyzer**: gerber
- **Source**: gerbers.json
- **Created**: 2026-03-23

### Correct
- All 9 gerber layers detected (F.Cu, B.Cu, F.Mask, B.Mask, F.Paste, B.Paste, F.SilkS, B.SilkS, Edge.Cuts). Missing required and missing recommended are both empty. Alignment=true.
- Via count 34 matches PCB analyzer. NPTH mounting holes (4×2.7mm) match the 4 MountingHole_2.7mm footprints in the schematic. PTH component holes 87 = 74×1.0mm (header pins) + 9×0.35mm + 2×0.65mm + 2×0.7mm. All plausible.
- PCB statistics show back_side=0 (all 34 footprints on F.Cu), so an empty B.Paste gerber is expected and correct. The analyzer correctly reports 0 apertures/flashes without flagging it as an error.

### Incorrect
- Two drill map Gerbers (NPTH-drl_map.gbr, PTH-drl_map.gbr) have x2_attributes FileFunction='Drillmap' but are classified as layer_type='unknown'. The analyzer should recognize the 'Drillmap' FileFunction and assign an appropriate layer type rather than 'unknown'. These files inflate the gerber_files count without contributing to layer completeness.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---
