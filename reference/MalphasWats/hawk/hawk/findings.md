# Findings: MalphasWats/hawk / hawk

## FND-00002120: KiCad 5 power pin names reported swapped for U1 ATSAMD10 (VDD on GND net, GND on +3.3V net); LDO regulator AP7333-33 correctly identified with battery input and 3.3V output

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: schematic_hawk_hawk.sch.json.json
- **Created**: 2026-03-24

### Correct
- The analyzer correctly identified U2 (AP7333-33SRG-7) as an LDO regulator with topology='LDO', input_rail='+BATT', output_rail='+3.3V', and estimated_vout=3.3 via the fixed_suffix method from the part number. The decoupling capacitors on both input (+BATT: C2=1uF) and output (+3.3V: C1=0.1uF, C3=1uF) are also correctly detected.

### Incorrect
- In the nets output, the +3.3V net lists U1 with pin_name='GND', and the GND net lists U1 with pin_name='VDD'. From the cached library (hawk-cache.lib), pin 11 is named GND (at y=-700 relative, absolute y=4450 matching the GND power symbol) and pin 12 is named VDD (at y=+700 relative, absolute y=3050 matching the +3.3V power symbol). The actual electrical connections are correct, but the pin names reported in the net connectivity data are swapped. This is a KiCad 5 legacy format pin name resolution bug: the analyzer maps pin coordinate positions to pin definitions incorrectly when the component has a mirrored transform (matrix 1,0,0,-1).
  (nets)

### Missed
(none)

### Suggestions
(none)

---

## FND-00002121: Gerber alignment falsely reported as misaligned due to B.Cu containing only THT pad flashes

- **Status**: promoted
- **Analyzer**: gerber
- **Source**: gerber_hawk_gerbers.json.json
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
- The analyzer reports aligned=false with issues 'Width varies by 3.5mm across copper/edge layers' and 'Height varies by 4.1mm across copper/edge layers', comparing B.Cu extent (14.475x29.9mm) against Edge.Cuts (18.0x33.978mm). However, hawk is a single-sided SMD board with a front-side copper pour; B.Cu contains only THT component pad flashes (D03 flash commands from connectors and switch). The spatial extent of THT pads is necessarily smaller than the board outline. The alignment checker should not flag mismatch when B.Cu contains only pad flashes and no routed copper, as this is expected for single-sided or predominantly single-sided designs.
  (alignment)

### Missed
(none)

### Suggestions
(none)

---
