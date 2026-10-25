"""Root conftest.py marker derivation and default tier selection (B9, TH-053)."""
import ast
import json
import re
import os
import shutil
import subprocess
import sys
from pathlib import Path
from tests.product_root import PRODUCT_ROOT  # noqa: E402

HARNESS = Path(__file__).resolve().parent.parent
TREE = HARNESS / "tests" / "fixtures" / "h0" / "plan1" / "sample_tree"


def _collect(*extra, quiet=True):
    env = {**os.environ, "KICAD_HAPPY_DIR": str(PRODUCT_ROOT)}
    proc = subprocess.run(
        [sys.executable, "-m", "pytest", "--collect-only", *(["-q"] if quiet else []),
         "-p", "no:cacheprovider", str(TREE), *extra],
        capture_output=True, text=True, cwd=HARNESS, env=env)
    ids = [l for l in proc.stdout.splitlines() if "::" in l]
    return proc.returncode, ids, proc.stdout + proc.stderr


def test_default_selection_is_unit_and_offline_contract():
    rc, ids, out = _collect()
    names = {i.rsplit("::", 1)[1] for i in ids}
    assert names == {"test_unit_default", "test_cheap"}, out
    # -q suppresses the report header, so check it from a non-quiet run
    _, _, header = _collect(quiet=False)
    assert "default selection: unit or offline_contract" in header


def test_default_selection_excludes_online():
    _, ids, _ = _collect()
    assert not any("test_online_declared" in i for i in ids)


def test_explicit_marker_expression_overrides_default():
    _, ids, _ = _collect("-m", "online")
    assert [i.rsplit("::", 1)[1] for i in ids] == ["test_online_declared"]
    _, ids, _ = _collect("-m", "corpus")
    assert [i.rsplit("::", 1)[1] for i in ids] == ["test_corpus_marked"]
    _, ids, _ = _collect("-m", "perf")
    assert [i.rsplit("::", 1)[1] for i in ids] == ["test_slow_bound"]


def test_all_tiers_collects_everything():
    _, ids, _ = _collect("--all-tiers")
    assert len(ids) == 5


def test_unknown_marker_is_rejected():
    bad = HARNESS / "tests" / "fixtures" / "h0" / "plan1" / "bad_marker"
    bad.mkdir(parents=True, exist_ok=True)
    (bad / "test_typo.py").write_text(
        "import pytest\n@pytest.mark.uint\ndef test_x():\n    assert True\n")
    try:
        proc = subprocess.run([sys.executable, "-m", "pytest", "--collect-only", "-q",
                               "-p", "no:cacheprovider", str(bad)],
                              capture_output=True, text=True, cwd=HARNESS,
                              env={**os.environ, "KICAD_HAPPY_DIR": str(PRODUCT_ROOT)})
        assert proc.returncode != 0
        assert "'uint' not found in `markers`" in proc.stdout + proc.stderr
    finally:
        shutil.rmtree(bad, ignore_errors=True)  # includes __pycache__


def test_header_reports_product_sha():
    rc, _, out = _collect(quiet=False)
    assert "product_root:" in out and "sha=" in out


def test_script_style_integration_file_is_ignored():
    proc = subprocess.run(
        [sys.executable, "-m", "pytest", "--collect-only", "-q", "-p", "no:cacheprovider",
         "integration/"],
        capture_output=True, text=True, cwd=HARNESS,
        env={**os.environ, "KICAD_HAPPY_DIR": str(PRODUCT_ROOT)})
    assert proc.returncode in (0, 5), proc.stdout + proc.stderr
    assert "INTERNALERROR" not in proc.stdout + proc.stderr


def _run_skip_tree(tmp_path, known):
    """Run the tracked skip fixture under the root conftest with a given allowlist."""
    tree = HARNESS / "tests" / "fixtures" / "h0" / "plan1" / "skip_tree"
    allow = tmp_path / "known_skips.json"
    allow.write_text(json.dumps(known))
    env = {**os.environ, "HARNESS_KNOWN_SKIPS": str(allow),
           "KICAD_HAPPY_DIR": str(PRODUCT_ROOT)}
    return subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", str(tree)],
                          capture_output=True, text=True, cwd=HARNESS, env=env)


def test_unlisted_skip_fails_session(tmp_path):
    proc = _run_skip_tree(tmp_path, {})
    assert proc.returncode == 1, proc.stdout + proc.stderr
    assert "unlisted skips in required tiers" in proc.stdout


def test_listed_skip_is_allowed(tmp_path):
    nodeid = "tests/fixtures/h0/plan1/skip_tree/test_skipper.py::test_s"
    proc = _run_skip_tree(tmp_path, {nodeid: "fixture for the allowlist test"})
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert "unlisted skips" not in proc.stdout


_CORPUS_TOKENS = ("REPOS_DIR", "OUTPUTS_DIR", "results/outputs", 'HARNESS_DIR / "results"',
                  'HARNESS_DIR / "repos"', '"reference" /', "Projects/sandbox",
                  '"results" / "outputs"', '/ "repos"', '"repos/')


def _has_token(text):
    return any(tok in text for tok in _CORPUS_TOKENS)


def _is_corpus_marker(node):
    return "mark.corpus" in ast.unparse(node)


def _corpus_names(tree, text):
    """Module-level names bound to a corpus path (`_RESULTS = HARNESS / "results" / ...`),
    followed through later assignments that use them (`SCH = _RESULTS / "schematic"`)."""
    names = set()
    changed = True
    while changed:
        changed = False
        for n in tree.body:
            if not isinstance(n, (ast.Assign, ast.AnnAssign)):
                continue
            targets = n.targets if isinstance(n, ast.Assign) else [n.target]
            ids = {t.id for t in targets if isinstance(t, ast.Name)} - names
            if not ids or n.value is None:
                continue
            used = {x.id for x in ast.walk(n.value) if isinstance(x, ast.Name)}
            if _has_token(ast.get_source_segment(text, n.value) or "") or used & names:
                names |= ids
                changed = True
    return names


def _touches(node, text, names):
    if _has_token(ast.get_source_segment(text, node) or ""):
        return True
    return any(isinstance(x, ast.Name) and x.id in names for x in ast.walk(node))


def _corpus_offenders(tree, text):
    """Names of test functions that touch corpus paths (directly, via a module-level name
    bound to one, or via a module-level helper) without a corpus marker."""
    names = _corpus_names(tree, text)
    helpers = {n.name for n in tree.body
               if isinstance(n, ast.FunctionDef) and not n.name.startswith("test_")
               and _touches(n, text, names)}
    module_marked = any(
        isinstance(n, ast.Assign) and any(getattr(t, "id", "") == "pytestmark" for t in n.targets)
        and _is_corpus_marker(n.value) for n in tree.body)
    if module_marked:
        return []
    bad = []
    for n in ast.walk(tree):
        if not (isinstance(n, ast.FunctionDef) and n.name.startswith("test_")):
            continue
        calls = {c.func.id for c in ast.walk(n)
                 if isinstance(c, ast.Call) and isinstance(c.func, ast.Name)}
        touches = _touches(n, text, names) or bool(calls & helpers)
        if touches and not any(_is_corpus_marker(d) for d in n.decorator_list):
            bad.append(n.name)
    return bad


def test_corpus_paths_require_marker():
    allow = json.loads((HARNESS / "tests" / "corpus_marker_allowlist.json").read_text())
    offenders = []
    for f in sorted((HARNESS / "tests").rglob("test_*.py")):
        rel = f.relative_to(HARNESS).as_posix()
        if "/fixtures/" in rel or rel in allow:
            continue
        text = f.read_text(encoding="utf-8")
        if 'TIER = "online"' in text:
            continue
        offenders += [f"{rel}::{name}" for name in _corpus_offenders(ast.parse(text), text)]
    assert not offenders, f"corpus-reading tests without @pytest.mark.corpus or allowlist entry: {offenders}"


def test_pytest_floor_reads_strict_markers_from_ini(tmp_path):
    """requirements-dev pins pytest>=9.0: older pytest ignores `strict_markers` in pytest.ini,
    so a typo'd marker would silently select nothing."""
    req = (HARNESS / "requirements-dev.txt").read_text()
    assert "pytest>=9.0" in req.split()
    (tmp_path / "pytest.ini").write_text((HARNESS / "pytest.ini").read_text())
    (tmp_path / "test_typo.py").write_text("import pytest\n\n@pytest.mark.unitt\ndef test_x():\n    pass\n")
    proc = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider",
                           str(tmp_path / "test_typo.py")], cwd=tmp_path, capture_output=True,
                          text=True, timeout=120)
    assert proc.returncode != 0 and "unitt" in proc.stdout + proc.stderr


_PRINT_SKIP_RETURN = re.compile(r'^([ \t]+)print\(\s*f?["\'][^"\']*SKIP[^"\']*["\']\s*\)\n\1return\b', re.M)


def test_no_print_and_return_skips():
    """TH-062 / code A6-F2: a printed "SKIP" followed by return records a pass the known-skips
    allowlist never sees; skips go through pytest.skip."""
    offenders = []
    for f in sorted((HARNESS / "tests").rglob("test_*.py")):
        if "/fixtures/" in f.as_posix():
            continue
        text = f.read_text(encoding="utf-8")
        offenders += [f"{f.relative_to(HARNESS)}:{text[:m.start()].count(chr(10)) + 1}"
                      for m in _PRINT_SKIP_RETURN.finditer(text)]
    assert not offenders, offenders


def test_corpus_audit_resolves_module_level_names():
    """code A6-F4: a corpus path kept in a module constant escaped the audit."""
    src = (
        "from pathlib import Path\n"
        "HARNESS = Path(__file__).parent\n"
        "_RESULTS = HARNESS / \"results\" / \"outputs\"\n"
        "SCH = _RESULTS / \"schematic\"\n"
        "def _first():\n    return next(SCH.glob('*'))\n"
        "def test_direct():\n    assert _RESULTS.exists()\n"
        "def test_via_helper():\n    assert _first()\n"
        "def test_clean(tmp_path):\n    assert tmp_path\n"
    )
    assert sorted(_corpus_offenders(ast.parse(src), src)) == ["test_direct", "test_via_helper"]


_PRODUCT_FALLBACK = re.compile(r'os\.environ\.get\(\s*"KICAD_HAPPY_DIR"\s*,')


def test_product_root_comes_from_tests_product_root_only():
    """ruling R16 (code A6-F6): a test resolves the product through tests.product_root, never a
    silent sibling or ~/Projects fallback of its own."""
    offenders = sorted(str(f.relative_to(HARNESS)) for f in (HARNESS / "tests").rglob("*.py")
                       if f.name != "product_root.py"
                       and _PRODUCT_FALLBACK.search(f.read_text(encoding="utf-8")))
    assert not offenders, offenders
