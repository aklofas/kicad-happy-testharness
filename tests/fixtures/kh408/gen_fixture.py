#!/usr/bin/env python3
"""KH-408 minimal pair: the same QFN-style footprint (one wide GND thermal
pad, three vias along the pad's long axis) placed twice — U1 at 0°, U2 at
30°. KiCad writes a pad's (at x y ANGLE) as the ABSOLUTE board angle, so
the rotated instance has footprint angle 30 AND pad angle 30.

Pre-fix, analyze_thermal_pad_vias rotates the via-to-pad offset by
-(fp_angle + pad_angle) = -2a. Composed with the via's true placement
rotation (-a, from board_xy below), the net spurious rotation applied to
the local via offset (lx, 0) is -3a, landing it at
(lx*cos(3a), -lx*sin(3a)). At a=30, 3a=90 degrees, sin(90)=1: the outer
vias (lx=+-1.6) land at |dy|=1.6 mm > 1.5*(PAD_H/2)=1.2 mm, outside the
containment box -> via_count 1 (only the untouched center via) instead
of 3.

Deviation from the task brief's angle choice (60 degrees, same for fp and
pad): at a=60, 3a=180 and sin(180)=0, so the pre-fix bug's net rotation
reduces to a point-reflection that the containment test's abs()-symmetric
bounding box cannot distinguish from the correct placement -- the bug is
coincidentally invisible at exactly 60 degrees (and any multiple of 60).
30 degrees is clear of that coincidence with maximal margin (sin(3*30)=1).

Deviation from the task brief's generator: the brief's footprint had
only the one EP pad. `_find_thermal_pads` requires `len(pads) >= 3` and
also disqualifies a candidate pad unless its area is >= 2x the
footprint's average SMD pad area (`analyze_pcb.py`'s
`avg_area > 0 and area < avg_area * 2.0` check) — with only one pad,
avg_area equals the EP pad's own area, so that check always disqualifies
it. Two small non-thermal signal pads (numbers "1"/"2", 0.3x0.3mm,
unconnected) are added to each footprint so the EP pad clears both the
pad-count floor and the average-area ratio test; they are not involved
in the rotation math under test.
"""
import math

PAD_W, PAD_H = 4.0, 1.6
VIA_LOCAL_X = (-1.6, 0.0, 1.6)
INSTANCES = [("U1", 100.0, 100.0, 0), ("U2", 130.0, 100.0, 30)]
GND = 1


def board_xy(cx, cy, lx, ly, angle_deg):
    # Same convention as analyze_pcb's pad placement: local -> board uses -angle.
    r = math.radians(-angle_deg)
    return (round(cx + lx * math.cos(r) - ly * math.sin(r), 4),
            round(cy + lx * math.sin(r) + ly * math.cos(r), 4))


def footprint(ref, x, y, a):
    at = f"(at {x} {y} {a})" if a else f"(at {x} {y})"
    pad_at = f"(at 0 0 {a})" if a else "(at 0 0)"
    return f"""  (footprint "Package_DFN_QFN:QFN-16_EP" (layer "F.Cu") {at}
    (property "Reference" "{ref}" (at 0 -3 0) (layer "F.SilkS") (effects (font (size 1 1))))
    (property "Value" "QFN16" (at 0 3 0) (layer "F.Fab") (effects (font (size 1 1))))
    (attr smd)
    (pad "17" smd rect {pad_at} (size {PAD_W} {PAD_H}) (layers "F.Cu" "F.Paste" "F.Mask") (net {GND} "GND"))
    (pad "1" smd rect (at 0 1.5) (size 0.3 0.3) (layers "F.Cu" "F.Paste" "F.Mask"))
    (pad "2" smd rect (at 0 -1.5) (size 0.3 0.3) (layers "F.Cu" "F.Paste" "F.Mask"))
  )"""


def vias(x, y, a):
    out = []
    for lx in VIA_LOCAL_X:
        bx, by = board_xy(x, y, lx, 0.0, a)
        out.append(f'  (via (at {bx} {by}) (size 0.6) (drill 0.3) (layers "F.Cu" "B.Cu") (net {GND}))')
    return "\n".join(out)


def build(header):
    body = [header, f'  (net 0 "")', f'  (net {GND} "GND")']
    for ref, x, y, a in INSTANCES:
        body.append(footprint(ref, x, y, a))
        body.append(vias(x, y, a))
    body.append(")")
    return "\n".join(body)


if __name__ == "__main__":
    import pathlib, sys
    here = pathlib.Path(__file__).parent
    # Header (kicad_pcb/version/generator/general/paper/layers/setup) copied from the
    # kh392-antipad fixture up to but excluding its first "(net " line.
    src = (here.parent / "kh392-antipad" / "board.kicad_pcb").read_text().splitlines()
    header = "\n".join(l for l in src[: next(i for i, l in enumerate(src) if l.lstrip().startswith("(net "))])
    (here / "qfn_rotated.kicad_pcb").write_text(build(header) + "\n")
    print("wrote qfn_rotated.kicad_pcb")
