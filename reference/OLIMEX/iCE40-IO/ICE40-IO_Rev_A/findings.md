# Findings: iCE40-IO / ICE40-IO_Rev_A

## FND-00002146: VGA15-F connector (VGA1) misclassified as 'varistor' component type; VGA video output interface not detected despite 9 VGA signal nets and R-2R DAC resistor networks; UART detection reports IrDA_Tx...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: schematic_iCE40-IO_ICE40-IO_Rev_A.sch.json.json
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
- The VGA15-F(CD0515S21J0) is a 15-pin D-sub VGA female connector used for VGA video output. It is classified by the analyzer as type 'varistor' in the BOM and component list. This is a component type inference error — the symbol prefix in the cache library is 'VGA' and the reference designator is 'VGA1', which apparently triggers a varistor classification heuristic. The component should be classified as 'connector'. The connector has 17 pins carrying VGA color signals (RED, GREEN, BLUE with 3-bit R-2R DAC networks), sync signals, and shield connections.
  (statistics)
- The analyzer detects IrDA_Tx and IrDA_Rx as UART signals but reports 'devices: []' for both. The TFDU4100 IrDA transceiver (IrDA1) has TXD (pin 3) and RXD (pin 4) pins which are the actual UART-like signals. However, the IrDA_Tx net connects to IrDA1 pin IRED_CATHODE (the IR LED anode drive, pin 2), and IrDA_Rx connects to IrDA1 pin NC. The nets are named after the IrDA function but do not carry the standard UART TXD/RXD signals — the actual TXD/RXD pins of IrDA1 are on different (unnamed) nets. The UART detection is responding to net name patterns rather than pin types, leading to a misleading result.
  (design_analysis)

### Missed
- The design implements a 3-bit VGA video output (VGA_RED1/2/3, VGA_GREEN1/2/3, VGA_BLUE1/2/3) using R-2R resistor DAC networks (R8/R9/R12, R13/R15/R16, R17/R19/R20 with 470R/1k/1.8k values) plus VGA_HSYNC and VGA_VSYNC lines. The VGA connector (VGA1) drives all signals. The analyzer does not detect this as a display or video interface in hdmi_dvi_interfaces or any other detector. A VGA interface detector or at minimum a video signal net pattern matcher would flag this.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00002147: PCB reports tht_count=0 but gerber drill file shows 161 component through-holes

- **Status**: promoted
- **Analyzer**: pcb
- **Source**: pcb_iCE40-IO_ICE40-IO_Rev_A.kicad_pcb.json.json
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
- The PCB statistics show tht_count=0 and all 43 footprints classified as 'smd'. However the gerber drill file has 161 component holes (70x 0.6mm, 23x 0.9mm, 68x 1.0mm), accounting for connectors with through-hole mounting pins (IDC34R, BH34R box headers, PS2 MDR6 mini-DIN, VGA D-sub). The .kicad_pcb source confirms these footprints have 'thru_hole' pad entries even though the module-level 'attr' is 'smd'. The analyzer only reads the footprint-level 'attr' attribute, missing the mixed THT/SMD nature of these connector footprints.
  (statistics)

### Missed
(none)

### Suggestions
(none)

---

## FND-00002148: Gerber layer set complete with correct X2 attributes for 2-layer board

- **Status**: promoted
- **Analyzer**: gerber
- **Source**: gerber_iCE40-IO_Gerbers.json.json
- **Created**: 2026-03-24

### Correct
- The iCE40-IO gerber set contains all 9 expected layers (F.Cu, B.Cu, F/B Mask, F/B Paste, F/B SilkS, Edge.Cuts) plus one drill file. All layers have correct X2 FileFunction attributes. Gerber/drill alignment is confirmed. Board dimensions (45x50mm) match the PCB analyzer output. The F.SilkS layer extents (59.1 x 63.1mm) exceed the board boundary, which is normal for silkscreen text/logos placed outside the board edge.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
