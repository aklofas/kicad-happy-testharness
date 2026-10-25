"""Corpus readers and assertion-prefix counts, pinned on a fixture data root."""
TIER = "unit"

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FIXTURE = ROOT / "tests" / "fixtures" / "wave10" / "corpus_read"
GOLDEN = ROOT / "tests" / "fixtures" / "wave10" / "corpus_read_golden.json"

# utils resolves the data root at import time, so the readers run in a child
# process started with the override set.
CAPTURE = r"""
import json, sys
from pathlib import Path
root = Path(sys.argv[1])
for sub in ("validate", "tools"):
    sys.path.insert(0, sub)
import utils
import validate_schema, generate_catalog, generate_health_report
import coverage_report, coverage_detector_map

def plain(x):
    if isinstance(x, (set, frozenset)):
        return sorted(plain(i) for i in x)
    if isinstance(x, dict):
        return {str(k): plain(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [plain(i) for i in x]
    return x

repos = ["o/r"]
out = {
    "schema_inventory": validate_schema.build_inventory(repos, jobs=1),
    "catalog_entry": generate_catalog.build_repo_entry(
        "o/r", {"o/r": "Test"}, {"o/r": {"url": "https://example.test/o/r", "hash": "abc"}}),
    "health_counts": generate_health_report._count_assertions(),
    "coverage_by_prefix": coverage_report._count_assertions_by_prefix(
        utils.DATA_DIR / "o" / "r" / "p" / "assertions"),
    "detector_map_counts": coverage_detector_map.count_assertions(),
}
print(json.dumps(plain(out), indent=1, sort_keys=True))
"""


def capture(tmp_path):
    shutil.copytree(FIXTURE / "outputs", tmp_path / "results" / "outputs")
    shutil.copytree(FIXTURE / "reference", tmp_path / "reference")
    env = dict(os.environ, KICAD_HAPPY_TESTHARNESS_DATA_DIR=str(tmp_path))
    r = subprocess.run([sys.executable, "-c", CAPTURE, str(tmp_path)], cwd=ROOT, env=env,
                       capture_output=True, text=True, timeout=120)
    assert r.returncode == 0, r.stderr
    return r.stdout


def test_corpus_readers_match_golden(tmp_path):
    assert json.loads(capture(tmp_path)) == json.loads(GOLDEN.read_text(encoding="utf-8"))
