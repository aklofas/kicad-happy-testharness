# kh409-altium-bus

Synthetic Altium-flat (`.kicad_pro` `top_level_sheets`) fixture for KH-409:
"does the hybrid-merge path's missing `_sheet` tag on peer-sheet
`bus_wires`/`bus_entries` cause a wrong cross-page net join?"

## Shape

`synthetic.kicad_pro` lists two `top_level_sheets`: `page1.kicad_sch` and
`page2.kicad_sch`. Neither file contains a `(sheet ...)` reference, so
`analyze_schematic.py` discovers both as Altium-flat peers (the pure-flat
case of the hybrid merge path — no recursive sub-sheet walk needed).

Both pages carry an **identical** two-member bus at **identical**
coordinates: a vertical `(bus ...)` trunk at `x=50.8`, a `"DATA[0..1]"`
bus-name label, two `(bus_entry ...)` taps feeding two horizontal member
wires labelled `"DATA0"` and `"DATA1"`, and one `Device:R` per member
(`R1`/`R3` on page1, `R2`/`R4` on page2) with pin 1 landing on the member
wire. This is deliberate: KH-409 says the hybrid-merge loop tags
components/wires/labels/junctions/no-connects with `_sheet = sheet_idx`
for peer sheets but **not** `bus_wires`/`bus_entries`, so the bus
resolver (`bw.get("_sheet", 0)` in `build_net_map`'s bus pass) reads
page2's bus geometry as sheet 0 — the same key page1's bus geometry
uses. Making the two pages' bus geometry coincide exactly is the most
aggressive way to expose any resulting cross-page conflation: if the
bug caused a real net join, it would join R1/R3 (page1) with R2/R4
(page2) through the shared sheet-0 `BusGraph`.

**Resistor placement note:** `Device:R`'s pin "1" is at local
`(0, +3.81)`. Empirically verified via `kicad-cli sch export netlist`
(10.0.6): at symbol rotation 0°, the PAGE-space offset is `(0, -3.81)`
for pin "1" (`page_Y = symbol_Y - local_y`), the opposite sign of what
was assumed when this fixture was speced — and the originally-speced
7.62mm vertical pitch between the two member wires exactly equals one
full pin-to-pin span, so placing both resistors per the original spec
made resistor A's free pin 2 land exactly on resistor B's wire,
bridging DATA0 and DATA1 into one net. Fixed here by computing
`symbol_Y = wire_Y + 3.81` (puts pin "1", not pin "2", on the member
wire) and moving the second member's wire/entry/resistor +20mm further
down the bus so the first resistor's free pin 2 (at `wire_Y + 7.62`)
no longer coincides with the second member's wire.

## KiCad semantics (ground truth)

KiCad keeps bus member nets **page-local** here: `kicad-cli` (10.0.6)
does not resolve `.kicad_pro` `top_level_sheets` — given either
`page1.kicad_sch` or `page2.kicad_sch` alone it exports that file's own
nets only, which is itself the proof that nothing links the two pages'
`DATA0`/`DATA1` together. Oracle output:

```
page1: /DATA0 [('R1','1')]   /DATA1 [('R3','1')]
page2: /DATA0 [('R2','1')]   /DATA1 [('R4','1')]
(R*'s pin 2 unconnected on both pages)
```

The analyzer must **not** join R1/R2 (or R3/R4) into one net, and must
not report page2's bus data as unresolved or misattributed to sheet 0.

**Round 1 verdict (this construct alone): NOT REPRODUCED.** See
`kh409-repro.md` for why — page2's bus-name and member-name labels are
correctly `_sheet`-tagged (only `bus_wires`/`bus_entries` are affected)
and route around the broken shared `BusGraph` via the ordinary
per-sheet local-label path, so net identity comes out right anyway.

## Round 2 construct: CTRL[0..1] (REPRODUCED)

Each page also carries an **independent** `CTRL[0..1]` bus (page1 at
`x=100`, page2 at `x=150` — deliberately NOT coincident, see below) with
one `bus_entry`-tapped member wire plainly labelled `"CTRL0"`, feeding
one `Device:R` each (`R5` page1, `R6` page2). `kicad-cli` confirms both
are genuinely connected (`/CTRL0 [('R5','1')]` on page1 in isolation;
symmetric for R6 on page2).

This exposes a DIFFERENT, real defect: the bus pass's tap-resolution
mechanism (`analyze_schematic.py`'s mechanism B1/B2) calls
`add_point()`/`union_with_overlapping_wires()` using the *shared
`BusGraph`'s dict key* as the "sheet" argument, not the tap's true
sheet. For page1 (root, key 0) this is correct. For page2 (peer, whose
bus elements default to key 0 too, per the KH-409 tagging gap) it is
wrong: page2's own member wire is correctly tagged `_sheet=1`, so the
tap's sheet-0 search never finds it, `root_names` comes back empty,
and the tap is flagged `"unlabeled_entry_tap"` — a false positive,
since `R6`'s `CTRL0` label is right there and perfectly valid. Verified
in isolation (page1's identical construct, analyzed completely
standalone with no `.kicad_pro` at all) that the correct behavior is
`bus_topology.unresolved == []`.

**Why the two constructs diverge:** DATA[0..1]'s connectivity is
carried entirely by the ordinary per-sheet label path (unaffected by
this bug), so cross-page identity collapses to "do two independent,
correctly-sheet-scoped labels stay separate" — which they do, trivially.
CTRL[0..1]'s tap-based connectivity routes through the bus pass's own
sheet-keyed coordinate lookups, which *are* broken for any peer sheet,
regardless of whether its label text happens to be shared with another
page. Deliberately non-coincident coordinates between page1's and
page2's CTRL constructs were necessary to see this: identical
coordinates (as in the DATA[0..1] construct) let a peer's tap
accidentally land on the root's real sheet-0 geometry and mask the bug,
exactly as happened with Round 1.

Fixed in `analyze_schematic.py`'s hybrid merge loop (commit `42c14bb`
on `v2.3.x-dev`): peer-sheet `bus_wires`/`bus_entries` are now tagged
`_sheet = sheet_idx`, same as components/wires/labels/junctions/
no-connects already were. `bus_aliases` are deliberately left untagged
(KH-395 oracle finding: kicad-cli resolves `bus_alias` across files, so
aliases are project-wide, not sheet-scoped).

Test: `tests/test_kh409_peer_bus_sheet.py`. Full evidence (oracle
output, pre-fix and post-fix analyzer output) in `kh409-repro.md`
(main-repo working tree,
`.superpowers/sdd/2026-10-04-v2.3.1-maintenance-batch/`).
