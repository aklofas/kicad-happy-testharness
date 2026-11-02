# multi-unit

`dual_opamp.kicad_sch` (KiCad 9 format, self-authored) places one dual op-amp, U1
(LM358, SOIC-8), as three units:

- unit 1: voltage follower, `SIG_IN` (pin 3) to `BUF_OUT` (pins 1 and 2)
- unit 2: non-inverting stage, `BUF_OUT` (pin 5) to `AMP_OUT` (pin 7), feedback `FB`
  (pin 6) through R1 (`AMP_OUT`-`FB`) and R2 (`FB`-`GND`), 10k each
- unit 3: supply, `+5V` (pin 8) and `GND` (pin 4)

Nets join through global labels placed on the pin ends; there are no wires. Pinned by
`tests/test_multi_unit_fixture.py`.
