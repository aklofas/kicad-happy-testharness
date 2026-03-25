# Findings: MSCP / QBusH723Z-JLCPCB-0.1_QBusH723Z

## FND-00000925: Bus topology width values are consistently 2x the actual signal count; STM32 PG11 GPIO pin misidentified as a power_good signal; FMC (Flexible Memory Controller) parallel bus to FPGA not detected; ...

- **Status**: new
- **Analyzer**: schematic
- **Source**: QBusH723Z-JLCPCB-0.1_QBusH723Z.kicad_sch.json
- **Created**: 2026-03-23

### Correct
- U7 (AP7361C-33Y5, +3V3 LDO) EN pin is driven by the +1V2 rail (output of U6 TLV74312PDBVR), creating a correct power-up sequence: +5V → U6 → +1V2 → enables U7 → +3V3. The STM32H7 requires VCAP/+1V2 (internal regulator output) before VDD, so this sequencing is intentional and correctly captured.
- All 50 SSM3K35AMFV MOSFETs are detected in transistor_circuits with type=mosfet, source_is_ground=true, and gate_driver_ics pointing to U2 (FPGA). This correctly models the FPGA-driven open-drain output topology used for bus signaling.

### Incorrect
- Every detected bus has width reported as exactly double the actual net count: DA=16 nets→reported 32, A[16:22]=7 nets→reported 14, LD=8 nets→reported 16, QSPI_IO=4 nets→reported 8, TRACED=4 nets→reported 8, LED=3 nets→reported 6, NBL=2 nets→reported 5 (close to 2x+1). The range strings are correct but the width field is doubled. This is a systematic bug in the bus width calculation in bus_topology.
  (signal_analysis)
- power_sequencing.power_good_signals reports U1 (STM32H723ZGTx) as having a pg_pin='PG11' on net 'PG11_SD_D2_SPI1_SCK'. PG11 is the STM32 GPIO name for Port G pin 11, used here as SD card D2/SPI1_SCK. The 'PG' prefix is a false match for Power Good — STM32 GPIO names always follow P+port+pin convention. This is a false positive.
  (signal_analysis)

### Missed
- The STM32H723 drives an FPGA (U2, T8Q144I4) via what appears to be a parallel FMC bus: DA[0:15] (16-bit data), A[16:22] (7-bit address), NBL[0:1] (byte enable). These nets are correctly found as label groups in bus_topology but are not identified as an FMC/parallel memory interface in bus_analysis or signal_analysis.memory_interfaces. The FMC bus is a significant STM32 peripheral.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00000926: 4-layer stackup correctly identified with In1/In2 as power plane layers; DFM correctly flags board size exceeding 100×100mm JLCPCB pricing threshold

- **Status**: new
- **Analyzer**: pcb
- **Source**: QBusH723Z-JLCPCB-0.1_QBusH723Z.kicad_pcb.json
- **Created**: 2026-03-23

### Correct
- In1.Cu and In2.Cu are typed as 'power' layers. Zone stitching confirms GND spans B.Cu/F.Cu/In1.Cu and +5V occupies In2.Cu, which is the expected split-plane 4-layer stackup for this density of design.
- Board is 131.75×214.122mm. The DFM violation message correctly identifies this exceeds the 100×100mm standard tier at JLCPCB, requiring higher fabrication pricing. Board is otherwise standard tier (min_annular_ring=0.125mm, min_drill=0.2mm).

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
