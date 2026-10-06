#!/usr/bin/env python3
"""KH-419 minimal pair: a Ø15 mm circular SMD touch pad TOUCH1 at (120,120) on
F.Cu inside a GND fill whose hole has a 1.0 mm clearance ring (hole radius 8.5,
drawn as a 64-gon via a keyhole slit toward -x), plus a 0.4 mm GND fill ISLAND
centred at (127.8, 127.8) — 0.1 mm from the pad's bbox corner (127.5, 127.5)
but 3.3 mm from the pad's circumference. Old sampler → ≈0.1 mm; outline
sampler → 1.0 mm. Two vias: V_IN at offset (7.0, 0) from centre (inside the
circle, distance 7.0 < r=7.5) and V_OUT at offset (7.3, 2.5) (distance
≈7.72 mm, OUTSIDE the r=7.5 circle but still inside the hw=hh=7.5 bbox on
both axes independently — the classic corner-region false positive; an
on-axis point can't show this since bbox and circle coincide on-axis when
hw == hh == r), both TOUCH_A net — via_in_pad must list only V_IN."""
import math, pathlib

GND, TOUCH = 1, 2
CX, CY, R = 120.0, 120.0, 7.5
HOLE_R = R + 1.0
X0, X1, Y0, Y1 = 100.0, 140.0, 100.0, 140.0
N = 64


def keyhole_ring():
    # Outer rect CCW starting at the slit entry on the left edge (y = CY),
    # go around the rect, come back to the slit, traverse the hole CW, exit.
    pts = [(X0, CY + 0.005), (X0, Y1), (X1, Y1), (X1, Y0), (X0, Y0), (X0, CY - 0.005)]
    pts.append((CX - HOLE_R, CY - 0.005))
    for k in range(N + 1):
        a = math.pi + 2 * math.pi * k / N  # start at the left of the hole, CW
        pts.append((round(CX + HOLE_R * math.cos(-a), 4), round(CY + HOLE_R * math.sin(-a), 4)))
    pts.append((CX - HOLE_R, CY + 0.005))
    return pts


def poly(pts):
    body = " ".join(f"(xy {x} {y})" for x, y in pts)
    return f'    (filled_polygon (layer "F.Cu") (pts {body}))'


def island():
    cx, cy, h = 127.8, 127.8, 0.2
    return poly([(cx - h, cy - h), (cx + h, cy - h), (cx + h, cy + h), (cx - h, cy + h)])


BODY = f"""  (net 0 "")
  (net {GND} "GND")
  (net {TOUCH} "TOUCH_A")
  (footprint "Touch:Pad_Round_D15" (layer "F.Cu") (at {CX} {CY})
    (property "Reference" "TOUCH1" (at 0 -9 0) (layer "F.SilkS") (effects (font (size 1 1))))
    (property "Value" "TouchPad" (at 0 9 0) (layer "F.Fab") (effects (font (size 1 1))))
    (attr smd)
    (pad "1" smd circle (at 0 0) (size 15 15) (layers "F.Cu" "F.Mask") (net {TOUCH} "TOUCH_A"))
  )
  (via (at {CX + 7.0} {CY}) (size 0.6) (drill 0.3) (layers "F.Cu" "B.Cu") (net {TOUCH}))
  (via (at {CX + 7.3} {CY + 2.5}) (size 0.6) (drill 0.3) (layers "F.Cu" "B.Cu") (net {TOUCH}))
  (zone (net {GND}) (net_name "GND") (layer "F.Cu") (hatch edge 0.5)
    (connect_pads (clearance 1.0))
    (min_thickness 0.25)
    (fill yes (thermal_gap 0.5) (thermal_bridge_width 0.5))
    (polygon (pts (xy {X0} {Y0}) (xy {X1} {Y0}) (xy {X1} {Y1}) (xy {X0} {Y1})))
{poly(keyhole_ring())}
{island()}
  )
)"""

if __name__ == "__main__":
    here = pathlib.Path(__file__).parent
    src = (here.parent / "kh392-antipad" / "board.kicad_pcb").read_text().splitlines()
    header = "\n".join(src[: next(i for i, l in enumerate(src) if l.lstrip().startswith("(net "))])
    (here / "circle_touch_pad.kicad_pcb").write_text(header + "\n" + BODY + "\n")
    print("wrote circle_touch_pad.kicad_pcb")
