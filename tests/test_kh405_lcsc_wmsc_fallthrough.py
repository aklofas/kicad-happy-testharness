"""KH-405 — jlcsearch no longer returns `extra`; a hit with no datasheet URL
must be enriched from the wmsc product-detail endpoint instead of failing.
The old fallback only fired when jlcsearch returned NO hit at all."""

TIER = "unit"

import os
import sys
from pathlib import Path
from unittest import mock

_HARNESS = Path(__file__).resolve().parent.parent
_KH = os.environ.get("KICAD_HAPPY_DIR", str(_HARNESS.parent / "kicad-happy"))
sys.path.insert(0, os.path.join(_KH, "skills", "lcsc", "scripts"))

import fetch_datasheet_lcsc as fdl  # noqa: E402

HIT = {"lcsc": 318884, "mfr": "TS-1187A-B-A-B", "package": "SMD-4P", "is_basic": True,
       "description": "Tactile Switch", "stock": 1683297, "price": 0.0197}
WMSC = {"mfr": "TS-1187A-B-A-B", "datasheet": "https://datasheet.lcsc.com/x.pdf?productCode=C318884",
        "stock": 597040, "price": [{"ladder": 20, "usdPrice": 0.0207}], "lcsc": "318884",
        "extra": {"number": "C318884", "mpn": "TS-1187A-B-A-B",
                  "manufacturer": {"name": "XKB Connection"},
                  "datasheet": {"pdf": "https://datasheet.lcsc.com/x.pdf?productCode=C318884"}}}


def test_hit_without_datasheet_is_enriched():
    with mock.patch.object(fdl, "search_lcsc_direct", return_value=WMSC) as m:
        out = fdl.enrich_with_wmsc(dict(HIT))
    m.assert_called_once_with("C318884")
    assert fdl._get_datasheet_url(out).endswith("productCode=C318884")
    assert fdl._get_manufacturer(out) == "XKB Connection"
    assert out["stock"] == 1683297  # jlcsearch figure kept


def test_hit_with_datasheet_is_left_alone():
    hit = dict(HIT, extra={"datasheet": {"pdf": "https://a/b.pdf"}})
    with mock.patch.object(fdl, "search_lcsc_direct") as m:
        assert fdl.enrich_with_wmsc(hit) is hit
    m.assert_not_called()


def test_empty_extra_datasheet_block_falls_through_to_wmsc():
    """KH-405: a jlcsearch hit can carry extra={"datasheet": {}} (present but
    empty, e.g. a stale/partial cache entry) rather than no `extra` key at
    all. The old shallow merge ({**direct_extra, **component_extra}) let
    that empty block clobber wmsc's populated one at the extra.datasheet
    level -- masked for _get_datasheet_url() by the separate top-level
    fallback, but real: any consumer reading extra.datasheet.pdf directly
    got nothing. wmsc's datasheet block must win whenever the hit's own has
    no pdf URL."""
    hit = dict(HIT, extra={"datasheet": {}})
    with mock.patch.object(fdl, "search_lcsc_direct", return_value=WMSC) as m:
        out = fdl.enrich_with_wmsc(hit)
    m.assert_called_once_with("C318884")
    assert fdl._get_datasheet_url(out).endswith("productCode=C318884")
    assert out["extra"]["datasheet"].get("pdf", "").endswith("productCode=C318884")


def test_wmsc_miss_returns_original():
    with mock.patch.object(fdl, "search_lcsc_direct", return_value=None):
        out = fdl.enrich_with_wmsc(dict(HIT))
    assert fdl._get_datasheet_url(out) == ""


if __name__ == "__main__":
    import sys
    import traceback
    ok = fail = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
                ok += 1
            except Exception:  # noqa: BLE001
                fail += 1
                print(f"FAIL {name}")
                traceback.print_exc()
    print(f"{ok} passed, {fail} failed")
    sys.exit(1 if fail else 0)
