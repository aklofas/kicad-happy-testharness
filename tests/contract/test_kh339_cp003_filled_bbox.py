#!/usr/bin/env python3
"""KH-339: CP-003 must measure touch-pad GND clearance against filled
copper (filled_bbox) when available, not the zone outline.

KH-373 changed `_nearest_zone_copper_distance`'s signature to
(fp, fp_layer, gnd_zones, zones, zone_fills) and added a filled_polygon
basis that takes priority when zone_fills has polygon data. These tests
pass zone_fills=None to exercise the bbox-only fallback paths KH-339
added, which are unchanged."""

import sys

from tests.contract._paths import MAIN_REPO_ROOT

sys.path.insert(0, str(MAIN_REPO_ROOT / "skills" / "kicad" / "scripts"))
from analyze_pcb import _nearest_zone_copper_distance


def _fp(x, y):
    return {"x": x, "y": y, "pads": []}


def test_prefers_filled_bbox():
    """SacMap repro: outline says 0.0mm, filled copper is 1.0mm away."""
    gz = [{"layers": ["F.Cu"], "net_name": "GND",
           "outline_bbox": [0.0, 0.0, 10.0, 10.0],
           "filled_bbox": [2.0, 2.0, 10.0, 10.0]}]
    d, basis = _nearest_zone_copper_distance(_fp(1.0, 5.0), "F.Cu", gz, gz, None)
    assert basis == "filled_bbox"
    assert abs(d - 1.0) < 1e-9


def test_outline_fallback_when_no_fill():
    gz = [{"layers": ["F.Cu"], "net_name": "GND",
           "outline_bbox": [0.0, 0.0, 10.0, 10.0]}]
    d, basis = _nearest_zone_copper_distance(_fp(1.0, 5.0), "F.Cu", gz, gz, None)
    assert basis == "outline_bbox"
    assert d == 0.0


def test_layer_filter():
    gz = [{"layers": ["B.Cu"], "net_name": "GND",
           "outline_bbox": [0.0, 0.0, 10.0, 10.0]}]
    d, basis = _nearest_zone_copper_distance(_fp(1.0, 5.0), "F.Cu", gz, gz, None)
    assert basis is None and d == float("inf")
