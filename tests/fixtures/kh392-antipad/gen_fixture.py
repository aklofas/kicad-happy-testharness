#!/usr/bin/env python3
"""Minimal-pair fixture for GitHub issues #39 and #40 (KH-392 / KH-393).

Board geometry: four 1.5 mm horizontal stubs on F.Cu, each ending at a via.
A GND zone fills B.Cu with a square void (antipad) hand-carved around each
via, sized to KiCad's void = via_diameter/2 + clearance (0.15 mm clearance).
A fifth stub (SENSE3) sits entirely outside the GND zone's x-range with no
via and no nearby copper at all — a genuine reference-plane gap, used to
confirm the KH-392 antipad fix doesn't mask real GP-001 findings.

  net       y    via    void half-width   expectation
  SENSE1   100   0.8    0.55  (> 0.5)     GP-001 sampler: via-end sample MISSES -> 50.0%
  SENSE2   104   0.6    0.45  (< 0.5)     via-end sample HITS -> clean        (issue #39 pair)
  P1_VBUS  108   0.8    0.55              read as SIGNAL -> sampled -> 50.0%
  VBUS     112   0.8    0.55              read as power  -> skipped           (issue #40 pair)
  SENSE3   100   (none) (no zone nearby)  no reference plane at all -> 0.0%   (KH-392 real-gap control)
"""

STUB_X0, STUB_LEN = 140.0, 1.5
VIA_X = STUB_X0 + STUB_LEN            # 141.5
ROWS = [  # (net_id, name, y, via_size, void_half_width)
    (1, "SENSE1", 100.0, 0.8, 0.55),
    (2, "SENSE2", 104.0, 0.6, 0.45),
    (3, "P1_VBUS", 108.0, 0.8, 0.55),
    (4, "VBUS", 112.0, 0.8, 0.55),
]
GND_ID = 5

# SENSE3: a lone stub far from the GND zone (x-range below), no via — the
# opposite layer has no copper anywhere nearby, so both samples must MISS.
SENSE3_ID = 6
SENSE3_X0 = 170.0
SENSE3_Y = 100.0

ZX0, ZX1, ZY0, ZY1 = 130.0, 160.0, 90.0, 120.0


def rect(x0, y0, x1, y1):
    pts = f"(xy {x0} {y0}) (xy {x1} {y0}) (xy {x1} {y1}) (xy {x0} {y1})"
    return f'    (filled_polygon (layer "B.Cu") (pts {pts}))'


def build():
    nets = "\n".join(f'  (net {i} "{n}")' for i, n, *_ in ROWS)
    tracks, vias = [], []
    for i, name, y, via, _h in ROWS:
        tracks.append(
            f'  (segment (start {STUB_X0} {y}) (end {VIA_X} {y}) '
            f'(width 0.3) (layer "F.Cu") (net {i}))')
        vias.append(
            f'  (via (at {VIA_X} {y}) (size {via}) (drill 0.4) '
            f'(layers "F.Cu" "B.Cu") (net {i}))')

    # SENSE3: track only, no via, well clear of the GND zone (x >= 170 vs.
    # zone x-range [130,160]).
    sense3_net = f'  (net {SENSE3_ID} "SENSE3")'
    sense3_track = (
        f'  (segment (start {SENSE3_X0} {SENSE3_Y}) '
        f'(end {SENSE3_X0 + STUB_LEN} {SENSE3_Y}) '
        f'(width 0.3) (layer "F.Cu") (net {SENSE3_ID}))')

    # Fill = full-width slabs between void rows + left/right slabs beside voids
    fills, prev_y = [], ZY0
    for _i, _n, y, _v, h in ROWS:
        fills.append(rect(ZX0, prev_y, ZX1, y - h))          # slab above void row
        fills.append(rect(ZX0, y - h, VIA_X - h, y + h))     # left of void
        fills.append(rect(VIA_X + h, y - h, ZX1, y + h))     # right of void
        prev_y = y + h
    fills.append(rect(ZX0, prev_y, ZX1, ZY1))                # bottom slab

    zone = (
        f'  (zone (net {GND_ID}) (net_name "GND") (layer "B.Cu")\n'
        f'    (connect_pads (clearance 0.15))\n'
        f'    (fill yes (thermal_gap 0.5) (thermal_bridge_width 0.5))\n'
        f'    (polygon (pts (xy {ZX0} {ZY0}) (xy {ZX1} {ZY0}) '
        f'(xy {ZX1} {ZY1}) (xy {ZX0} {ZY1})))\n'
        + "\n".join(fills) + "\n  )")

    return (
        '(kicad_pcb (version 20221018) (generator pcbnew)\n'
        '  (general (thickness 1.6))\n'
        '  (layers (0 "F.Cu" signal) (31 "B.Cu" signal)\n'
        '    (44 "Edge.Cuts" user))\n'
        '  (net 0 "")\n'
        f'{nets}\n'
        f'  (net {GND_ID} "GND")\n'
        f'{sense3_net}\n'
        + "\n".join(tracks) + "\n"
        + sense3_track + "\n"
        + "\n".join(vias) + "\n"
        + zone + "\n)\n")


if __name__ == "__main__":
    import sys
    out = sys.argv[1]
    with open(out, "w") as f:
        f.write(build())
    print(f"wrote {out}")
