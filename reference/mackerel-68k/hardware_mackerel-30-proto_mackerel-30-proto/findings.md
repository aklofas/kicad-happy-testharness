# Findings: mackerel-68k / hardware_mackerel-30-proto_mackerel-30-proto

## ?: MC68030 retro computer with DRAM, Flash, SRAM, dual UART, FPU, CPLDs, and DIN41612 expansion bus; analyzer correctly identifies power topology and oscillators but misses memory interfaces and bus architecture

- **Status**: new
- **Analyzer**: schematic
- **Source**: hardware_mackerel-30-proto_mackerel-30-proto.kicad_sch.json
- **Created**: 2026-03-23

### Correct
- MC68030RC CPU correctly identified as IC with 128 pins, all connected
- LM2576T-5 correctly classified as switching regulator with +12V input
- AMS1117-3.3 correctly classified as LDO with +5V input and +3.3V output
- Three active oscillators correctly detected (X1 CPU clock, X2 UART 3.6864MHz, X3 DRAM clock)
- X2 frequency correctly parsed as 3.6864MHz from value string
- Total component count of 131 matches actual schematic across 8 sheets
- 16 ICs correctly identified
- All 8 hierarchical sheets correctly parsed
- Bus signals detected: 32-bit address A0..A31, 32-bit data D0..D31, DRAM_A0..A11, IDE_D0..D15
- Three power rails correctly identified: +12V, +5V, +3.3V plus GND
- +5V decoupling analysis correctly counts 53 capacitors totaling 3364.6uF
- Five 74HC245 bus buffers correctly identified (U12-U16)

### Incorrect
- LM2576T-5 output_rail reported as __unnamed_68 (switching node) instead of +5V; the fixed 5V buck regulator output is on the +5V rail after inductor L1; fb_net correctly shows +5V but output_rail should also be +5V
  (signal_analysis.power_regulators)
- Design observation flags U6 as having missing output caps on __unnamed_68, but C26 (1000uF) and C25 (10uF) are on the +5V rail after the inductor - correct buck converter output cap placement
  (signal_analysis.design_observations)
- Multi-driver net warnings for U15 B-side pins are false positives; U15 is a 74HC245 with DIR=GND connecting CPU bus signals to expansion connector - tri-state pins sharing nets with CPU outputs is expected
  (connectivity_issues.multi_driver_nets)
- ERC no_driver warnings for TXA/TXB nets are caused by custom XR68C681 symbol marking TXDA/TXDB pins as 'input' when they are actually UART transmit outputs
  (design_analysis.erc_warnings)

### Missed
- No memory_interfaces detected despite AS6C4008-55PCN 512KB SRAM (U4), SST39SF040 512KB Flash (U3), and SIMM72 DRAM module (U10) all on the MC68030 address/data bus
  (signal_analysis.memory_interfaces)
- DS1233 reset supervisor (U8) not detected as a protection/supervisory device; monitors +5V and drives /RESET to CPU, CPLDs, DUART, and expansion bus
  (signal_analysis.protection_devices)
- DIN41612 96-pin expansion bus (J14) not characterized as system bus with address A0-A19, buffered data EXP_D16-D31, control signals, chip select, and interrupt
  (bus_topology)
- IDE/CompactFlash interface not detected; J13 (Conn_02x20) with 74HC245 buffers U12/U13 for 16-bit IDE bus IDE_D0..IDE_D15
  (signal_analysis)
- XR68C681 dual UART (U5) not characterized as complete peripheral with two channels: A (TXA/RXA/RTSA on J4) and B (TXB/RXB/RTSB on J5), 3.6864MHz clock, GPIO ports
  (design_analysis.bus_analysis.uart)
- Two EPM7128 CPLDs (U2,U9) as address decoder/glue logic generating chip selects (/CS_SRAM, /CS_FLASH, /CS_DRAM, /CS_DUART), DTACK, and interrupt encoding not characterized
  (subcircuits)

### Suggestions
- For fixed-output switching regulators like LM2576T-5, trace through the inductor to find the actual output rail rather than reporting the switching node
- Detect memory ICs by lib_id patterns like Memory_RAM:*, Memory_Flash:*, and SIMM/DIMM symbols; report as memory_interfaces with bus widths
- Recognize reset supervisor ICs (DS1233, MAX693, TPS386x) as protection_devices with monitored rail and reset output net
- Suppress multi_driver_net warnings when one driver is a 74HC245 tri-state pin, as bidirectional bus buffers sharing nets is expected
- Characterize large multi-pin connectors (DIN41612, ISA, VME) as bus interfaces by analyzing signal groupings

---
