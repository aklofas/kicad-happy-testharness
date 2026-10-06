#!/usr/bin/env python3
"""KH-412: J1 pad 1 drill 0.18 (the board minimum, pad-sourced), one via
drill 0.3, and J1 pad 3 with a degenerate (drill 0.00001) as in
HamedMasafi/MeloCar remote_3.kicad_pcb. Companion .kicad_pro sets
min_through_hole_diameter 0.3 so the design-rule check also fires.

Pad 1's drill is 0.18mm rather than the DFM standard-tier limit of
0.2mm exactly -- analyze_pcb.py's DFM-001 check is a strict `<` against
LIMITS_STD["min_drill"] (0.2), so a drill equal to the limit does not
violate it. 0.18 sits strictly between the advanced-tier limit (0.15)
and the standard-tier limit (0.2), which fires exactly one DFM-001
violation (the "requires advanced process" warning branch).

Fix round 1 (review): also generates a via-less variant
(pad_drill_min_novias.kicad_pcb, same footprint, the `via` line
omitted) -- analyze_vias() used to early-return {} for a board with
zero vias, silently dropping both degenerate_drills and
current_capacity.min_pad_drill_mm for boards like MeloCar's
remote_3.kicad_pcb, which has no vias at all.
"""
import pathlib

BODY = """  (net 0 "")
  (net 1 "GND")
  (footprint "Connector:TestHeader" (layer "F.Cu") (at 100 100)
    (property "Reference" "J1" (at 0 -3 0) (layer "F.SilkS") (effects (font (size 1 1))))
    (property "Value" "HDR" (at 0 3 0) (layer "F.Fab") (effects (font (size 1 1))))
    (attr through_hole)
    (pad "1" thru_hole circle (at 0 0) (size 0.6 0.6) (drill 0.18) (layers "*.Cu" "*.Mask") (net 1 "GND"))
    (pad "2" thru_hole circle (at 2.54 0) (size 1.0 1.0) (drill 0.6) (layers "*.Cu" "*.Mask") (net 1 "GND"))
    (pad "3" thru_hole circle (at 5.08 0) (size 1.0 1.0) (drill 0.00001) (layers "*.Cu" "*.Mask") (net 1 "GND"))
  )
  (via (at 110 110) (size 0.6) (drill 0.3) (layers "F.Cu" "B.Cu") (net 1))
)"""

BODY_NOVIAS = """  (net 0 "")
  (net 1 "GND")
  (footprint "Connector:TestHeader" (layer "F.Cu") (at 100 100)
    (property "Reference" "J1" (at 0 -3 0) (layer "F.SilkS") (effects (font (size 1 1))))
    (property "Value" "HDR" (at 0 3 0) (layer "F.Fab") (effects (font (size 1 1))))
    (attr through_hole)
    (pad "1" thru_hole circle (at 0 0) (size 0.6 0.6) (drill 0.18) (layers "*.Cu" "*.Mask") (net 1 "GND"))
    (pad "2" thru_hole circle (at 2.54 0) (size 1.0 1.0) (drill 0.6) (layers "*.Cu" "*.Mask") (net 1 "GND"))
    (pad "3" thru_hole circle (at 5.08 0) (size 1.0 1.0) (drill 0.00001) (layers "*.Cu" "*.Mask") (net 1 "GND"))
  )
)"""

PRO = """{
  "board": {"design_settings": {"rules": {"min_through_hole_diameter": 0.3, "min_via_diameter": 0.4, "min_track_width": 0.1}}},
  "meta": {"filename": "pad_drill_min.kicad_pro", "version": 1}
}
"""

if __name__ == "__main__":
    here = pathlib.Path(__file__).parent
    src = (here.parent / "kh392-antipad" / "board.kicad_pcb").read_text().splitlines()
    header = "\n".join(src[: next(i for i, l in enumerate(src) if l.lstrip().startswith("(net "))])
    (here / "pad_drill_min.kicad_pcb").write_text(header + "\n" + BODY + "\n")
    (here / "pad_drill_min.kicad_pro").write_text(PRO)
    (here / "pad_drill_min_novias.kicad_pcb").write_text(header + "\n" + BODY_NOVIAS + "\n")
    print("wrote pad_drill_min.kicad_pcb + .kicad_pro + pad_drill_min_novias.kicad_pcb")
