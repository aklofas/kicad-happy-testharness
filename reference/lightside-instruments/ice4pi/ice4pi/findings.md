# Findings: lightside-instruments/ice4pi / ice4pi

## FND-00002215: SPI bus detected twice: once correctly as bus 'ICE', and again as duplicate 'pin_U2' with MOSI/MISO roles swapped; False positive I2C detection on PIO0_20/PIO0_21: FPGA GPIO pin-name aliases trigge...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: schematic_ice4pi_ice4pi.kicad_sch.json.json
- **Created**: 2026-03-24

### Correct
- Bus 'ICE' correctly identifies the iCE_MOSI, iCE_MISO, and iCE_SCK nets connecting U1 (ICE40HX1K-TQ144) and U2 (W25Q32JVSSIQ), with chip_select_count=1 (iCE_SS_B). This is the FPGA configuration flash bus, accurately identified.

### Incorrect
- The SPI bus between U1 (ICE40HX1K FPGA) and U2 (W25Q32 flash) is reported as two separate buses. Bus 'ICE' is correct (MOSI=iCE_MOSI, MISO=iCE_MISO, SCK=iCE_SCK, 1 chip select). Bus 'pin_U2' is a phantom detection anchored on the flash's pin perspective, with MOSI and MISO swapped and 0 chip selects. This is a false positive: there is only one SPI bus between FPGA and flash.
  (design_analysis)
- The analyzer reports an I2C bus on nets PIO0_20 (SDA) and PIO0_21 (SCL) because the ICE40HX1K FPGA has pins with alternate names 'SDA/GPIO2' and 'SCL/GPIO3'. However, PIO0_20 and PIO0_21 are generic FPGA I/O nets connected only to the Raspberry Pi connector (J2) — there is no external I2C peripheral or pull-up resistors. Both detected I2C signals have has_pull_up=false and only a single device (U1). This is a false positive based on FPGA pin-name aliases.
  (design_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00002216: 4-layer stackup with In1.Cu and In2.Cu correctly identified as power-type layers

- **Status**: new
- **Analyzer**: pcb
- **Source**: pcb_ice4pi_ice4pi.kicad_pcb.json.json
- **Created**: 2026-03-24

### Correct
- The PCB reports In1.Cu and In2.Cu with type='power', matching the source .kicad_pcb file where both inner layers are declared as 'power'. The board is a 65x30mm 4-layer design with 57 footprints and fully routed (routing_complete=true, unrouted_net_count=0).

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
