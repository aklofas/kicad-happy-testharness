# Mirror-transform oracle fixture

Regression fixture for the mirrored+rotated symbol pin transform fix
(main-repo `f57277d`, "KiCad matrix composition"; promised publicly in
PR #27 / issue #17). Consumed by
`tests/contract/test_mirror_transform_oracle.py`.

- `mir12.kicad_sch` — 12-combo fixture: an asymmetric 4-pin symbol
  (`mir:MIRTEST`, pins L/R/T/B = 1/2/3/4) instantiated as U1–U12 across
  4 rotations (0/90/180/270) × 3 mirror states (none, `mirror x`,
  `mirror y`), with a net label at each of the four cardinal positions
  around each instance (`{prefix}_{LEFT,RIGHT,UP,DOWN}`). Whichever pin
  lands on a cardinal point picks up that net.
- `mir12.net` — ground truth: kicad-cli 10.0.3 (Eeschema
  10.0.3-10.0.3~ubuntu24.04.1) netlist export of the fixture. 48 nets,
  one `(ref, pin)` node each. The oracle contract is
  `(ref, pin) → net-name suffix after the last '_'`.
- `mir12_manifest.json` — ref → (prefix, cx, cy, mirror, angle) map,
  emitted by the generator (main-repo `old/mirtest-oracle/gen12.py`,
  gitignored scratch).

Baseline expectation: any pre-fix analyzer (v1.3/v1.4/v2.0 ≤ `0d95d1a`)
scores 32/48 — the 16 failures are exactly U5/U6/U11/U12 (the four
mirror × 90/270 combos), where the decomposed flip-then-rotate order got
all 4 pins wrong. At `f57277d`+ the score is 48/48.

Note: KiCad normalizes orientations on save, so only `(mirror x)` with
`(at .. 90|270)` persists in real saved files; this generated fixture
deliberately covers the `(mirror y)` forms too since the parser must
handle whatever is on disk.
