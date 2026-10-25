"""audit_equations reads product sources like the constants audit: PEP 263 coding cookies are
honoured and an unparsable file is an error in both scans, never a silent skip."""
import sys
from pathlib import Path

import pytest

HARNESS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HARNESS / "validate"))
import audit_equations as ae  # noqa: E402

pytestmark = pytest.mark.unit

LATIN1 = (b"# -*- coding: latin-1 -*-\n"
          b"import math\n"
          b"\n"
          b"def tagged(r, c):\n"
          b"    # EQ-001: fc = 1 / (2 pi R C)  \xe9\n"
          b"    return 1 / (2 * math.pi * r * c)\n"
          b"\n"
          b"def untagged(x):\n"
          b"    label = '\xe9'\n"
          b"    return math.sqrt(x), label\n")


def _write(tmp_path, data, name="m.py"):
    p = tmp_path / name
    p.write_bytes(data)
    return p


def test_latin1_source_is_scanned_by_both_functions(tmp_path):
    p = _write(tmp_path, LATIN1)
    tagged = ae.scan_file(p, product_root=tmp_path)
    assert [e["id"] for e in tagged] == ["EQ-001"]
    assert tagged[0]["function"] == "tagged"
    untagged = ae.find_untagged(p, product_root=tmp_path)
    assert [u["function"] for u in untagged] == ["untagged"]


def test_unparsable_source_raises_from_find_untagged(tmp_path):
    p = _write(tmp_path, b"def broken(:\n")
    with pytest.raises(ae.ScanError):
        ae.find_untagged(p, product_root=tmp_path)


def test_undecodable_source_raises_from_both(tmp_path):
    p = _write(tmp_path, b"# coding: utf-8\nX = '\xe9'\n")
    with pytest.raises(ae.ScanError):
        ae.scan_file(p, product_root=tmp_path)
    with pytest.raises(ae.ScanError):
        ae.find_untagged(p, product_root=tmp_path)


def test_untagged_command_exits_2_on_an_unparsable_file(tmp_path, monkeypatch):
    scripts = tmp_path / "skills" / "x" / "scripts"
    scripts.mkdir(parents=True)
    (scripts / "ok.py").write_bytes(LATIN1)
    (scripts / "bad.py").write_bytes(b"def broken(:\n")
    monkeypatch.setattr(ae, "resolve_kicad_happy_dir", lambda: tmp_path)
    with pytest.raises(SystemExit) as ex:
        ae.cmd_untagged(type("A", (), {})())
    assert ex.value.code == 2


def test_untagged_indicators_do_not_depend_on_hash_seed(tmp_path):
    import json
    import os
    import subprocess
    p = _write(tmp_path, b"import math\n"
                         b"def f(x):\n"
                         b"    return (math.sqrt(x) + math.log(x) + math.pi + math.sin(x)\n"
                         b"            + math.cos(x) + math.exp(x) + x**2 + 1e-9)\n")
    code = ("import sys, json; sys.path.insert(0, %r);"
            "import audit_equations as ae;"
            "from pathlib import Path;"
            "print(json.dumps(ae.find_untagged(Path(%r), product_root=Path(%r))))"
            % (str(HARNESS / "validate"), str(p), str(tmp_path)))
    outs = set()
    for seed in ("0", "1", "2", "3"):
        r = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True,
                           env=dict(os.environ, PYTHONHASHSEED=seed))
        assert r.returncode == 0, r.stderr
        outs.add(r.stdout)
    assert len(outs) == 1
    indicators = json.loads(outs.pop())[0]["indicators"]
    assert indicators == sorted(indicators)
