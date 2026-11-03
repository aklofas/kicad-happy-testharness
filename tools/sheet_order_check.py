#!/usr/bin/env python3
"""Sheet-order determinism check: a project and its sheet-reversed copy must analyze the same.

KiCad names nets and orders the hierarchy independently of the order the (sheet ...) blocks
are stored in the root file. For each root schematic, the project directory is copied twice
into a scratch directory, the root's sheet blocks are reversed in one copy, and
analyze_schematic.py runs on both copies under the same path; the outputs must be equal once
the run ids, input hashes and timings are dropped.

Usage:
    python3 tools/sheet_order_check.py --product DIR ROOTS.txt [--jobs N] [--json OUT]

ROOTS.txt lists root schematics relative to repos/ (default: reference/sheet_order_roots.txt).
Exit 0 when every root is identical in both orders, 1 otherwise.
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HARNESS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HARNESS))

from utils import DATA_ROOT  # noqa: E402

DEFAULT_ROOTS = HARNESS / "reference" / "sheet_order_roots.txt"
TIMEOUT_S = 600


def _children(text: str) -> list[tuple[int, int]]:
    """Spans of the direct children of the outermost s-expression in ``text``."""
    spans, depth, start, i, n = [], 0, None, 0, len(text)
    while i < n:
        c = text[i]
        if c == '"':
            i += 1
            while i < n and text[i] != '"':
                i += 2 if text[i] == "\\" else 1
        elif c == "(":
            depth += 1
            if depth == 2:
                start = i
        elif c == ")":
            if depth == 2:
                spans.append((start, i + 1))
            depth -= 1
        i += 1
    return spans


def reverse_sheets(text: str) -> str:
    """``text`` with the root-level (sheet ...) blocks stored in reverse order."""
    spans = [(a, b) for a, b in _children(text)
             if text[a + 1:a + 6] == "sheet" and text[a + 6] in " \t\r\n"]
    if len(spans) < 2:
        return text
    blocks = [text[a:b] for a, b in spans][::-1]
    out, last = [], 0
    for (a, b), block in zip(spans, blocks):
        out.append(text[last:a])
        out.append(block)
        last = b
    out.append(text[last:])
    return "".join(out)


def _stable(doc: dict, proj: str) -> str:
    inputs = doc.get("inputs") or {}
    inputs.pop("run_id", None)
    inputs.pop("source_hashes", None)  # the reversed root is a different file
    doc.pop("capability_mode_ref", None)
    doc.pop("elapsed_s", None)
    return json.dumps(doc, sort_keys=True, default=str).replace(proj, "<proj>")


def _analyze(product: Path, root: Path, out: Path) -> tuple[int, str]:
    env = dict(os.environ, PYTHONHASHSEED="0", PYTHONDONTWRITEBYTECODE="1")
    for k in [k for k in env if k.startswith(("DIGIKEY_", "MOUSER_", "ELEMENT14_", "NEXAR_"))]:
        env.pop(k)
    r = subprocess.run([sys.executable, str(product / "skills" / "kicad" / "scripts" / "analyze_schematic.py"),
                        str(root), "--output", str(out)],
                       cwd=str(out.parent), env=env, capture_output=True, text=True, timeout=TIMEOUT_S)
    return r.returncode, r.stderr[-400:]


def check_root(product: Path, repos: Path, rel: str) -> dict:
    src = repos / rel
    with tempfile.TemporaryDirectory(prefix="sheet-order-") as tmp:
        docs, rows = [], {"root": rel}
        for variant in ("orig", "rev"):
            base = Path(tmp) / variant
            proj = base / "proj"
            shutil.copytree(src.parent, proj, ignore=shutil.ignore_patterns(".git"), symlinks=True)
            root = proj / src.name
            if variant == "rev":
                text = root.read_text(encoding="utf-8")
                rev = reverse_sheets(text)
                rows["sheets_reversed"] = rev != text
                root.write_text(rev, encoding="utf-8")
            out = base / "out.json"
            rc, err = _analyze(product, root, out)
            if rc != 0 or not out.exists():
                return {**rows, "status": "error", "variant": variant, "exit_code": rc, "stderr": err}
            docs.append(_stable(json.loads(out.read_text(encoding="utf-8")), str(proj)))
        return {**rows, "status": "identical" if docs[0] == docs[1] else "differs"}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("roots", nargs="?", type=Path, default=DEFAULT_ROOTS)
    ap.add_argument("--product", type=Path, required=True, help="kicad-happy checkout to analyze with")
    ap.add_argument("--jobs", type=int, default=4)
    ap.add_argument("--json", type=Path, help="write the per-root results here")
    args = ap.parse_args(argv)
    repos = Path(DATA_ROOT) / "repos"
    roots = [l.strip() for l in args.roots.read_text(encoding="utf-8").splitlines()
             if l.strip() and not l.startswith("#")]
    with ThreadPoolExecutor(args.jobs) as ex:
        results = list(ex.map(lambda r: check_root(args.product.resolve(), repos, r), roots))
    for r in results:
        print(f"{r['status']:9s} {r['root']}" + ("" if r.get("sheets_reversed", True) else "  (one sheet block)"))
    same = sum(r["status"] == "identical" for r in results)
    print(f"{same}/{len(results)} identical in both sheet orders")
    if args.json:
        args.json.write_text(json.dumps(results, indent=1) + "\n", encoding="utf-8")
    return 0 if same == len(results) else 1


if __name__ == "__main__":
    sys.exit(main())
