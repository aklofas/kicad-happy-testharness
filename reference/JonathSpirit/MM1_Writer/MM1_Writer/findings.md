# Findings: MM1_Writer / MM1_Writer

## FND-00000878: UC_RX net incorrectly assigned to U1 VBUS pin instead of UART RX; U1 power domain wrongly includes UC_RX and unnamed nets as power rails; False positive level-shifter warnings for SRCLK and RCLK; C...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: MM1_Writer.sch.json
- **Created**: 2026-03-23

### Correct
- statistics.total_components=23, component_types match. BOM grouping is correct. All 3 shift registers (74AHC595) and the MCU (C8051F385-GQ) correctly identified.
- signal_analysis.decoupling_analysis correctly groups capacitors by rail with correct values and SRF estimates. Both rails have bulk and bypass caps noted correctly.

### Incorrect
- In the nets section, 'UC_RX' maps to only U1 pin 8 (VBUS, input). The design_observations also flags it as a single-pin net. In reality UC_RX is a UART signal on J5 pin 3 and U1 pin 29. The PCB output correctly shows J5 pad 3 = UC_RX and U1 pad 29 = /UC_RX, confirming the schematic analyzer has a label-to-net resolution bug for this net in KiCad 5 legacy format.
  (signal_analysis)
- design_analysis.power_domains.ic_power_rails.U1 lists '+5V', 'UC_RX', and '__unnamed_12' as power rails. UC_RX is a UART signal, not a power rail. The C8051F385 has VDD (pin 6) and REGIN (pin 7) power pins — these become unnamed nets that the power domain detector incorrectly classifies as power_internal. The result is false 'needs_level_shifter' warnings for SRCLK and RCLK.
  (signal_analysis)
- cross_domain_signals flags SRCLK and RCLK as needing level shifters across '+3.3V' and '+5V' domains. However, 74AHC595 is tolerant of 5V inputs when powered at 3.3V (it is a USB-to-memory writer with the MCU on +5V USB power). More critically, the large list of power domains (7 domains per signal) arises from the broken power domain detection for U1, making this finding unreliable.
  (signal_analysis)
- In the nets section, 'C2CK' lists only U1 pin 31 (P0.3) and 'C2D' lists only U1 pin 32 (P0.2) with point_count=2 but no J2 connector pins. J2 is the JTAG debug connector with pads 3=/C2CK and 4=/C2D, confirmed by the PCB output. This is a KiCad 5 legacy net parsing failure for these label-connected nets.
  (signal_analysis)

### Missed
- Three 74AHC595 shift registers driving 24 address bits to a memory connector is a classic SPI-like serial-to-parallel topology. The analyzer found no bus protocol (spi: [], memory_interfaces: []) for this daisy-chained shift register arrangement, missing an opportunity to describe the serial-to-parallel address expansion pattern.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00000879: Board dimensions, layer count, and routing completeness correctly reported; Net-pad mapping for J3 (30-pin connector) and shift registers correctly extracted; Edge clearance warnings report negativ...

- **Status**: promoted
- **Analyzer**: pcb
- **Source**: MM1_Writer.kicad_pcb.json
- **Created**: 2026-03-23

### Correct
- 101.5 x 55.5mm, 2 copper layers, routing_complete=true, 41 vias, 479 track segments, dual GND pours on both layers — all consistent with a well-routed 2-layer board.
- J3 pad_nets correctly maps all 30 pins to their respective MEMADDRESS/MEMDATA/power nets, consistent with the schematic.

### Incorrect
- J1 has -3.01mm edge clearance and J2 has -0.55mm — these are horizontal connectors intentionally extending past the board edge (USB-B and pin socket). The analyzer flags them as warnings with no indication that this may be intentional for through-board connectors, potentially generating false alarms.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00000880: Layer completeness correctly reported: 7 gerbers present, F.Paste missing as expected for all-THT/SMD board; Alignment reported as true despite F.SilkS extending 4mm beyond board outline in Y-axis;...

- **Status**: promoted
- **Analyzer**: gerber
- **Source**: documents_MM1_Writer_gerbert.json
- **Created**: 2026-03-23

### Correct
- completeness.complete=true with F.Paste in missing_recommended. For a board with 0% SMD ratio (smd_ratio=0.0 based on x2 attributes), missing F.Paste is expected. Layer identification and X2 attribute parsing all correct.
- Via drill=0.2mm (41 holes), component holes in 3 sizes (0.92/1.0/1.168mm = 51 total), mounting holes 2 PTH at 2.33mm + 4 NPTH at 3.0mm. All consistent with the PCB output.

### Incorrect
- board_dimensions height=55.5mm but F.SilkS layer_extents height=59.552mm — 4.05mm taller than the board outline. B.Cu/F.Cu are within the board at 54.08mm. The alignment check passes (aligned=true, issues=[]) despite this discrepancy. Silkscreen overhanging by ~4mm is notable and likely real (reference designators or text extend past edge), but the checker does not flag it.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---
