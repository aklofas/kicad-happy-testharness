# Findings: ArakelTheDragon/LIbrary_KiCad / KiCad basic microprocessor system

## FND-00000814: LM2596 feedback voltage divider misclassified as RC low-pass filter at 0.16 Hz; annotation_issues correctly detects duplicate_references for all unannotated '?' refs including U?

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: KiCad_ESP_WebServer_circuit_circuit.sch.json
- **Created**: 2026-03-23

### Correct
- Both WeMos D1 mini and LM2596T-ADJ share the reference 'U?' (unannotated design). The analyzer correctly reports duplicate_references=[...'U?'...] and unannotated=[...'U?'...]. The resulting power_domain confusion (LM2596 mapped to RX rail) is expected behavior given merged pin tables — not a separate bug.

### Incorrect
- The 10k potentiometer (RV?) + 100uF cap forming the LM2596T-ADJ feedback network is reported as an RC filter with fc=0.16Hz and output_net=Adjustable. The Adjustable net is the regulator output rail, not a filter output. This is a false positive RC filter detection caused by the feedback divider topology matching the RC filter pattern. The actual LM2596 feedback circuit should be captured under power_regulators instead.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00000815: IRLZ34N N-MOSFET drain and source nets are swapped — drain=GND, source=relay coil

- **Status**: new
- **Analyzer**: schematic
- **Source**: KiCad basic relay control_Relay.sch.json
- **Created**: 2026-03-23

### Correct
(none)

### Incorrect
- In the relay driver circuit (Q?), the analyzer reports drain_net=GND and source_net=__unnamed_43 (relay coil). The correct wiring is source→GND (low-side switch), drain→relay coil. Same swap appears for Q1 in Project17_Greenhouse/Circuit. This is a consistent drain/source pin assignment error for this symbol, likely from how KiCad 5 legacy pin numbers are mapped for this orientation/mirror combination. The transistor_circuits entry incorrectly sets drain_is_power=true (GND being flagged as 'power') while the real drain carries the relay current.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00000816: Stub PCB files (all 4) correctly yield zero footprints, zero tracks, zero nets

- **Status**: new
- **Analyzer**: pcb
- **Source**: KiCad_ESP_WebServer_circuit_circuit.kicad_pcb.json
- **Created**: 2026-03-23

### Correct
- All .kicad_pcb files in this repo are single-line stubs: (kicad_pcb (version 4) (host kicad "dummy file")). The analyzer returns footprint_count=0, routing_complete=true, empty connectivity — all correct. The silkscreen warning about missing board name is a minor false alarm on a non-existent board.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00000817: Crystal load cap (22pF) + series resistor (1k) reported as RC filter at 7.2 MHz

- **Status**: new
- **Analyzer**: schematic
- **Source**: KiCad basic relay control_KiCad basic relay control.sch.json
- **Created**: 2026-03-23

### Correct
(none)

### Incorrect
- In the relay control top-sheet, a 1k resistor and 22pF capacitor associated with crystal Y? (20MHz) are reported as an RC low-pass filter with fc=7234315 Hz and output_net=PIN (the MOSFET gate). The 22pF caps are crystal load caps; the 1k is a gate resistor. These components are connected across the crystal but not forming a standalone signal path filter. They are part of the crystal circuit which is also correctly detected in SA.crystal_circuits — making this a duplicate/false positive.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---
