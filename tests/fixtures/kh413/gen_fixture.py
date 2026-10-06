#!/usr/bin/env python3
"""KH-413: a capacitive-touch footprint whose only copper is ONE through-hole
pad (layers "*.Cu" "*.Mask"), centred at (120,120), pad diameter 2.0 mm.
A GND zone on F.Cu is filled as two rectangles leaving a horizontal band
y in [118.5, 121.5] clear → nearest copper edge from the pad OUTLINE
(top point y=119) is 0.5 mm; from the footprint ORIGIN it is 1.5 mm.
No B.Cu zone, so the footprint has no opposite-layer copper and CP-003
considers it. Pre-fix CP-003 reported 1.5 (origin fallback)."""
import pathlib

GND, TOUCH = 1, 2
X0, X1, Y0, Y1 = 110.0, 130.0, 110.0, 130.0
BAND_LO, BAND_HI = 118.5, 121.5


def rect(x0, y0, x1, y1):
    return f'    (filled_polygon (layer "F.Cu") (pts (xy {x0} {y0}) (xy {x1} {y0}) (xy {x1} {y1}) (xy {x0} {y1})))'


BODY = f"""  (net 0 "")
  (net {GND} "GND")
  (net {TOUCH} "TOUCH_A")
  (footprint "Touch:Pad_THT_D2.0" (layer "F.Cu") (at 120 120)
    (property "Reference" "TOUCH1" (at 0 -2 0) (layer "F.SilkS") (effects (font (size 1 1))))
    (property "Value" "TouchPad" (at 0 2 0) (layer "F.Fab") (effects (font (size 1 1))))
    (attr through_hole)
    (pad "1" thru_hole circle (at 0 0) (size 2.0 2.0) (drill 1.0) (layers "*.Cu" "*.Mask") (net {TOUCH} "TOUCH_A"))
  )
  (zone (net {GND}) (net_name "GND") (layer "F.Cu") (hatch edge 0.5)
    (connect_pads (clearance 0.5))
    (min_thickness 0.25)
    (fill yes (thermal_gap 0.5) (thermal_bridge_width 0.5))
    (polygon (pts (xy {X0} {Y0}) (xy {X1} {Y0}) (xy {X1} {Y1}) (xy {X0} {Y1})))
{rect(X0, Y0, X1, BAND_LO)}
{rect(X0, BAND_HI, X1, Y1)}
  )
)"""

if __name__ == "__main__":
    here = pathlib.Path(__file__).parent
    src = (here.parent / "kh392-antipad" / "board.kicad_pcb").read_text().splitlines()
    header = "\n".join(src[: next(i for i, l in enumerate(src) if l.lstrip().startswith("(net "))])
    (here / "tht_touch_pad.kicad_pcb").write_text(header + "\n" + BODY + "\n")
    print("wrote tht_touch_pad.kicad_pcb")
