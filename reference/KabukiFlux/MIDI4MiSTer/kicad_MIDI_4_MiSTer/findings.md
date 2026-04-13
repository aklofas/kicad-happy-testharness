# Findings: KabukiFlux/MIDI4MiSTer / kicad_MIDI_4_MiSTer

## FND-00000866: AMS1117 LDO correctly detected with +5V in, +3V3 out topology; 6N138 optocoupler not detected as isolation barrier; USB-C CC pull-down failures are false positives for a USB input-only device; foot...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: kicad_MIDI_4_MiSTer.kicad_sch.json
- **Created**: 2026-03-23

### Correct
- U2 AMS1117 detected as LDO with input_rail=+5V, output_rail=+3V3. Decoupling analysis on both rails correct. Power budget identifies U1 (74HC14) and U3 (6N138) on +3V3.

### Incorrect
- U3 is a 6N138 optocoupler which is the core MIDI input isolation device. The isolation_barriers list is empty. The 6N138 should be identified as an optical isolation barrier separating the MIDI IN signal from the MiSTer side. This is a meaningful missed detection for a MIDI interface board.
  (signal_analysis)
- USB1 is a TYPE-C 16PIN connector used as a power+data input from a MiSTer FPGA USB port. The analyzer flags cc1_pulldown_5k1 and cc2_pulldown_5k1 as fails. For a USB device (not host), 5.1k CC pull-downs would be correct — but this board uses the USB lines for MIDI data passthrough, not standard USB enumeration. The CC compliance check may be overly strict given the non-standard use. However, the actual CC pins (pins 3/13) are no-connects, which is a real compliance concern. The vbus_esd_protection fail is also real — no VBUS ESD is present.
  (signal_analysis)
- The 74HC14 is a multi-unit schematic symbol (6 gates + power). The footprint filter warning fires once per placed unit, resulting in 5 identical warnings for U1. This should be deduplicated to 1 warning per unique component reference.
  (signal_analysis)
- The bus_analysis.uart section on the MIDI4MiSTer output mistakenly identifies nets like TX_HPD, TX2_DP/DN, TX_CKN/P as UART. These are HDMI TMDS differential pairs. This is a false positive — these nets exist here due to test/label artifacts but on the MIPI-HDMI board are clearly HDMI diff pairs. The UART detector is picking up 'TX' prefix nets incorrectly.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00000867: PCB statistics and DFM analysis look correct for standard 2-layer board

- **Status**: new
- **Analyzer**: pcb
- **Source**: kicad_MIDI_4_MiSTer.kicad_pcb.json
- **Created**: 2026-03-23

### Correct
- 40 footprints, 2-layer, 44x44.75mm, fully routed. DFM tier 'standard', min track 0.2mm, no violations. Ground plane zones on both layers with single ground domain. These are all plausible for a MIDI interface board.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
