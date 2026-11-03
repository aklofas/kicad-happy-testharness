"""KH-800 — the analysis must not depend on the order sheet blocks are stored in the root.

Fixture (tests/fixtures/kh800_sheet_order/, built with the product's own test helpers): sibling
sheets "Amplifier" (hierarchical label EN) and "Video" (AMP_STB) joined at the root, stored with
Amplifier first although Video's sheet uuid sorts first. KiCad names the net from the shallower
sheet, then the lower full sheet-qualified name, so kicad-cli 10 calls it /Amplifier/EN in either
order. tools/sheet_order_check.py runs the same comparison over the corpus repro roots
(reference/sheet_order_roots.txt).
"""
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from tests.product_root import PRODUCT_ROOT
from tools.sheet_order_check import _stable, reverse_sheets

pytestmark = pytest.mark.unit

FIXTURE = Path(__file__).resolve().parent / "fixtures" / "kh800_sheet_order"
AMPLIFIER = "00000000-0000-4000-8000-000000000220"
ANALYZER = Path(str(PRODUCT_ROOT)) / "skills" / "kicad" / "scripts" / "analyze_schematic.py"


def _analyze(proj: Path) -> dict:
    out = proj.parent / "out.json"
    subprocess.run([sys.executable, str(ANALYZER), str(proj / "p.kicad_sch"), "--output", str(out)],
                   cwd=str(proj.parent), check=True, capture_output=True, timeout=120,
                   env={"PYTHONHASHSEED": "0", "PATH": "/usr/bin:/bin"})
    return json.loads(out.read_text(encoding="utf-8"))


def _copy(tmp_path: Path, variant: str) -> Path:
    proj = tmp_path / variant / "proj"
    shutil.copytree(FIXTURE, proj)
    if variant == "rev":
        root = proj / "p.kicad_sch"
        root.write_text(reverse_sheets(root.read_text(encoding="utf-8")), encoding="utf-8")
    return proj


def _net_name(doc: dict, pins: list) -> str:
    [name] = [n for n, net in doc["nets"].items()
              if sorted(f'{p["component"]}.{p["pin_number"]}' for p in net["pins"]) == pins]
    return name


def test_reverse_sheets_swaps_only_the_sheet_blocks():
    text = (FIXTURE / "p.kicad_sch").read_text(encoding="utf-8")
    rev = reverse_sheets(text)
    assert rev != text and sorted(rev) == sorted(text)
    assert rev.index(f'(uuid "{AMPLIFIER}")') > rev.index('(uuid "00000000-0000-4000-8000-000000000210")')
    assert reverse_sheets(rev) == text
    assert rev.index("(lib_symbols") == text.index("(lib_symbols")


def test_both_sheet_orders_give_the_same_analysis_and_kicads_net_name(tmp_path):
    docs = {}
    for variant in ("orig", "rev"):
        proj = _copy(tmp_path, variant)
        docs[variant] = _analyze(proj)
        assert _net_name(docs[variant], ["R1.1", "R2.1"]) == f"/{AMPLIFIER}/EN"
    assert (_stable(docs["orig"], str(tmp_path / "orig" / "proj"))
            == _stable(docs["rev"], str(tmp_path / "rev" / "proj")))
