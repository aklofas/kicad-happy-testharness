# Findings: MechanicalKeyboard-KiCad-Template / Atmega32u4

## FND-00000885: Crystal component (ref='Crystal', value='16Mhz', lib_id='Device:Crystal_GND24_Small') misclassified as capacitor; USB compliance check not run despite USB_TYPEC connector (HRO-TYPE-C-31-M-12) being...

- **Status**: new
- **Analyzer**: schematic
- **Source**: Atmega32u4.sch.json
- **Created**: 2026-03-23

### Correct
- MCU correctly typed as ic. Decoupling analysis correct: 5 caps on +5V rail totaling 10.4uF, has_bulk=true, has_bypass=true. Fuse (F?, 500mA) correctly identified as protection device. annotation_issues correctly flags unannotated F? and J?. SPI bus_id='0' (the real ISP signals on named nets) is a reasonable finding.

### Incorrect
- The legacy .sch parser classifies the Crystal component as type='capacitor', which suppresses crystal_circuits detection. The lib_id 'Device:Crystal_GND24_Small' and reference 'Crystal' are unambiguous. C_XTAL1 and C_XTAL2 (22pF load caps) are present, so a crystal circuit should be detectable. The type='capacitor' misclassification is the root cause.
  (signal_analysis)
- bus_analysis.spi contains two entries. Bus 'pin_J?' has SCK correct but MISO='__unnamed_37' and MOSI='RST', which is clearly wrong — this is the AVR-ISP-6 ICSP programming connector being misidentified as a standalone SPI peripheral. The ICSP header shares SCK/MISO/MOSI with the MCU's ISP interface, not a separate SPI bus.
  (signal_analysis)

### Missed
- USB_TYPEC component (value='HRO-TYPE-C-31-M-12') is present along with D+/D- nets, ESD_PROTECTION (PRTR5V0U2X), and R_D+/R_D- series resistors. usb_compliance is absent from output. The legacy .sch parser likely does not trigger the USB compliance analyzer, or the non-standard reference 'USB_TYPEC' is not matched.
  (signal_analysis)
- This is a KiCad template file with only the ATmega32U4 MCU and support circuitry — the key matrix is expected to be added by the user. No key_matrices and no design observation noting this is a keyboard MCU template. This is a borderline miss — no matrix is present, but the design context (keyboard template, USB HID, ICSP) is not captured.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00000886: Empty stub PCB (KiCad v4, 51 bytes) correctly analyzed as zero footprints/tracks with no false errors

- **Status**: new
- **Analyzer**: pcb
- **Source**: Atmega32u4.kicad_pcb.json
- **Created**: 2026-03-23

### Correct
- File is '(kicad_pcb (version 4) (host kicad "dummy file") )' — an intentional placeholder. Analyzer reports footprint_count=0, no errors, no warnings. Correct behavior for a template that only has schematic content.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
