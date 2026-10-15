"""tools/inventory_spice_caches.py: read-only sha256 inventory of spice/models dirs (TH-059)."""
TIER = "unit"

import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TOOL = ROOT / "tools" / "inventory_spice_caches.py"


def _tree(tmp_path):
    d = tmp_path / "root" / "o" / "r" / "hw" / "spice" / "models"
    d.mkdir(parents=True)
    (d / "manifest.json").write_text('{"TL074": {"file": "TL074.sub"}}')
    (d / "TL074.sub").write_text(".subckt TL074\n.ends\n")
    (d / "sub").mkdir()
    (d / "sub" / "x.lib").write_text("lib")
    w = tmp_path / "root" / "o" / "r" / "hw2" / "spice" / "work"
    w.mkdir(parents=True)
    (w / "net.cir").write_text("* c")
    (tmp_path / "root" / "o" / "r" / "not_spice").mkdir(parents=True)
    return tmp_path / "root"


def test_inventory_lists_dirs_and_hashes(tmp_path):
    repos = _tree(tmp_path)
    out = tmp_path / "inv.json"
    r = subprocess.run([sys.executable, str(TOOL), "--repos-root", str(repos), "-o", str(out)],
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    doc = json.loads(out.read_text())
    assert doc["dir_count"] == 2 and doc["file_count"] == 4
    entry = doc["dirs"]["o/r/hw/spice"]
    assert len(entry["manifest_sha256"]) == 64
    assert set(entry["files"]) == {"models/manifest.json", "models/TL074.sub", "models/sub/x.lib"}
    other = doc["dirs"]["o/r/hw2/spice"]
    assert other["manifest_sha256"] is None and set(other["files"]) == {"work/net.cir"}


def test_check_detects_changed_and_new_files(tmp_path):
    repos = _tree(tmp_path)
    out = tmp_path / "inv.json"
    subprocess.run([sys.executable, str(TOOL), "--repos-root", str(repos), "-o", str(out)], check=True)
    r = subprocess.run([sys.executable, str(TOOL), "--repos-root", str(repos), "--check", str(out)],
                       capture_output=True, text=True)
    assert r.returncode == 0
    (repos / "o" / "r" / "hw2" / "spice" / "work" / "NEW.sub").write_text("x")
    r = subprocess.run([sys.executable, str(TOOL), "--repos-root", str(repos), "--check", str(out)],
                       capture_output=True, text=True)
    assert r.returncode == 1 and "NEW.sub" in r.stdout


def test_inventory_never_writes_under_repos(tmp_path):
    repos = _tree(tmp_path)

    def snap():
        return sorted((str(p.relative_to(repos)), p.stat().st_mtime_ns,
                       p.read_bytes() if p.is_file() else None) for p in repos.rglob("*"))

    before = snap()
    subprocess.run([sys.executable, str(TOOL), "--repos-root", str(repos), "-o", str(tmp_path / "i.json")], check=True)
    subprocess.run([sys.executable, str(TOOL), "--repos-root", str(repos), "--check", str(tmp_path / "i.json")], check=True)
    assert before == snap()
