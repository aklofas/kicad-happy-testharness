# simple-project — contract-test fixture

Minimal KiCad 9 project consumed by every test under `tests/contract/`. Exercises every analyzer's happy path without the noise of a real design.

**Circuit:** J1 2-pin header → R1 330Ω (0603) → D1 LED → GND. +5V rail from J1 pin 1, GND from J1 pin 2.

**Footprint refs match schematic refs.** R1 carries MPN `RC0603FR-07330RL` and Manufacturer `Yageo` so MPN+footprint coverage is non-empty.

## Files

- `simple.kicad_pro` — minimal project file
- `simple.kicad_sch` — hand-authored schematic, `version 20241228`
- `simple.kicad_pcb` — hand-authored PCB, 35×25 mm, F.Cu + B.Cu + GND pour
- `gerbers/` — 6 layers + Excellon drill + `gbrjob`, exported via `kicad-cli`

## Regenerating gerbers after editing `simple.kicad_pcb`

```bash
export XDG_CONFIG_HOME=/tmp/kicad-cfg
mkdir -p /tmp/kicad-cfg/kicad/10.0
rm -f tests/fixtures/simple-project/gerbers/*
kicad-cli pcb export gerbers \
    --output tests/fixtures/simple-project/gerbers/ \
    tests/fixtures/simple-project/simple.kicad_pcb
kicad-cli pcb export drill \
    --output tests/fixtures/simple-project/gerbers/ \
    tests/fixtures/simple-project/simple.kicad_pcb
```

Authored against `kicad-cli` 10.0.1. Any `simple.kicad_prl` side-effect file should be deleted before committing.

## Known analyzer behavior on this fixture

- No ICs → `analyze_thermal.py` output is sparse (no hot components). If later contract tests need richer thermal coverage, add an SOT-23 LDO rather than stretching the thermal envelope to declare every field optional.
- Tracks occupy ~18×2.5 mm inside a 35×25 mm outline → `analyze_gerbers.py` emits two GR-002 width/height-variation warnings. Non-blocking; contract tests assert envelope shape, not finding counts.
