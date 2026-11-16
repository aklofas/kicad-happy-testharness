#!/usr/bin/env python3
"""Scan corpus KiCad files for two text markers that no analyzer run reports.

  transform   a `(transform` s-expression token outside quoted strings in a .kicad_pcb
              (KiCad 11 footprint transform); counts files and token lines.
  conflict    a line-leading git conflict marker (`<<<<<<< `, `|||||||`, `=======`, `>>>>>>> `)
              in a .kicad_sch, .kicad_pcb, .sch, .kicad_sym or .lib file. Legacy .sch / .lib
              count only with their EESchema header (Eagle .sch and SPICE .lib are not KiCad).

Usage:
    python3 tools/corpus_marker_scan.py [--root DIR] [--conflict-tsv OUT] [--json OUT]

Walks repos/ (or --root), skipping .git. Exit 0 always; the counts are the result.
"""
import argparse
import json
import os
import re
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

HARNESS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HARNESS))

from utils import REPOS_DIR  # noqa: E402

KICAD_EXTS = (".kicad_sch", ".kicad_pcb", ".sch", ".kicad_sym", ".lib")
LEGACY_HEADER = {".sch": b"EESchema", ".lib": b"EESchema-LIBRARY"}
CONFLICT = re.compile(r"^(<{7}|\|{7}|>{7})(?: |$)|^={7}$")
TRANSFORM = re.compile(r"\(transform(?=[\s)])")


def outside_strings(line, pos):
    """True when line[pos] is not inside a double-quoted s-expression string."""
    quoted, i = False, 0
    while i < pos:
        c = line[i]
        if c == "\\" and quoted:
            i += 2
            continue
        if c == '"':
            quoted = not quoted
        i += 1
    return not quoted


def scan_file(path):
    """Return (transform_lines, conflicts) for one file; conflicts = [(line_no, kind)]."""
    ext = next((e for e in KICAD_EXTS if path.lower().endswith(e)), "")
    try:
        data = Path(path).read_bytes()
    except OSError:
        return 0, []
    if ext in LEGACY_HEADER and LEGACY_HEADER[ext] not in data[:4096]:
        return 0, []
    text = data.decode("utf-8", errors="replace")
    transform, conflicts = 0, []
    for n, line in enumerate(text.splitlines(), 1):
        m = CONFLICT.match(line)
        if m:
            conflicts.append((n, line[:7]))
        if ext == ".kicad_pcb":
            if any(outside_strings(line, t.start()) for t in TRANSFORM.finditer(line)):
                transform += 1
    return transform, conflicts


def kicad_files(root):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d != ".git"]
        for f in filenames:
            if f.lower().endswith(KICAD_EXTS):
                yield os.path.join(dirpath, f)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--root", type=Path, default=REPOS_DIR)
    ap.add_argument("--conflict-tsv", type=Path, help="write path<TAB>line<TAB>marker rows")
    ap.add_argument("--json", type=Path, help="write the summary as JSON")
    ap.add_argument("--jobs", type=int, default=os.cpu_count())
    args = ap.parse_args(argv)

    paths = sorted(kicad_files(args.root))
    with ProcessPoolExecutor(max_workers=args.jobs) as ex:
        results = list(ex.map(scan_file, paths, chunksize=64))
    by_ext = {}
    transform_files, conflict_rows = [], []
    for p, (t, c) in zip(paths, results):
        ext = next(e for e in KICAD_EXTS if p.lower().endswith(e))
        by_ext[ext] = by_ext.get(ext, 0) + 1
        rel = os.path.relpath(p, args.root)
        if t:
            transform_files.append({"path": rel, "lines": t})
        conflict_rows += [(rel, n, kind) for n, kind in c]
    summary = {
        "root": str(args.root), "files_scanned": len(paths), "files_by_ext": by_ext,
        "pcb_transform_files": len(transform_files), "pcb_transform": transform_files,
        "conflict_files": len({r[0] for r in conflict_rows}), "conflict_markers": len(conflict_rows),
    }
    if args.conflict_tsv:
        args.conflict_tsv.parent.mkdir(parents=True, exist_ok=True)
        args.conflict_tsv.write_text("path\tline\tmarker\n" + "".join(
            f"{p}\t{n}\t{k}\n" for p, n, k in conflict_rows), encoding="utf-8")
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(json.dumps(summary, indent=1) + "\n", encoding="utf-8")
    print(f"scanned {len(paths)} files {by_ext}")
    print(f"pcb (transform: {len(transform_files)} files")
    print(f"conflict markers: {len(conflict_rows)} lines in {summary['conflict_files']} files")
    return 0


if __name__ == "__main__":
    sys.exit(main())
