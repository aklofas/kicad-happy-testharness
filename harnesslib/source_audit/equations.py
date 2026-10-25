"""Equation scan engine: `# EQ-NNN:` tags and untagged math in product sources.
The registry and its CLI live in validate/audit_equations.py."""
import ast
import hashlib
import re
import tokenize
from pathlib import Path

from .sources import iter_product_sources

# Heuristic indicators that a function contains engineering math
MATH_INDICATORS = frozenset({
    "math.sqrt", "math.log", "math.log10", "math.pi", "math.sin",
    "math.cos", "math.atan2", "math.exp", "**2", "**0.5",
    "2*math.pi", "2.0*math.pi", "1e-", "2e-",
})

# EQ tag pattern: # EQ-NNN: <formula description>
EQ_TAG_RE = re.compile(r"#\s*EQ-(\d{3}):\s*(.+)")
# Source citation pattern: # Source: <reference>
SOURCE_RE = re.compile(r"#\s*Source:\s*(.+)")


def _hash_function_body(source, func_node):
    """Hash the AST of a function body for change detection."""
    body = ast.dump(func_node, annotate_fields=False)
    return "sha256:" + hashlib.sha256(body.encode()).hexdigest()[:16]


def _find_enclosing_function(tree, line):
    """Find the function definition enclosing a given line number."""
    best = None
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            end = getattr(node, "end_lineno", node.lineno + 100)
            if node.lineno <= line <= end:
                if best is None or node.lineno > best.lineno:
                    best = node
    return best


def _tagged_statement(tree, line):
    """For a tag outside any function: the innermost class, else the first top-level
    statement at or after the tag line (the code the comment describes)."""
    best = None
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            end = getattr(node, "end_lineno", node.lineno)
            if node.lineno <= line <= end and (best is None or node.lineno > best.lineno):
                best = node
    if best is not None:
        return best
    return next((n for n in tree.body if getattr(n, "end_lineno", n.lineno) >= line), None)


class ScanError(Exception):
    """A source file could not be parsed: the scan must not save."""


def read_source_text(filepath):
    """Source text decoded per PEP 263 (coding cookie / BOM), as the compiler would."""
    try:
        with tokenize.open(filepath) as f:
            return f.read()
    except (OSError, SyntaxError, UnicodeDecodeError) as e:
        raise ScanError(f"could not read {filepath}: {e}") from None


def scan_file(filepath, source_text=None, product_root=None):
    """Scan a file for EQ-NNN tags and extract equation metadata.

    Returns list of equation info dicts.
    """
    if source_text is None:
        source_text = read_source_text(filepath)

    lines = source_text.splitlines()
    try:
        tree = ast.parse(source_text)
    except SyntaxError as e:
        raise ScanError(f"syntax error in {filepath}: {e}") from None

    equations = []
    filename = (Path(filepath).resolve().relative_to(Path(product_root).resolve()).as_posix()
                if product_root else filepath.name)

    for i, line in enumerate(lines):
        m = EQ_TAG_RE.search(line)
        if not m:
            continue

        eq_num = int(m.group(1))
        eq_id = f"EQ-{eq_num:03d}"
        formula = m.group(2).strip()
        lineno = i + 1  # 1-indexed

        # Collect source citations from subsequent lines
        sources = []
        for j in range(i + 1, min(i + 10, len(lines))):
            sm = SOURCE_RE.search(lines[j])
            if sm:
                sources.append(sm.group(1).strip())
            elif not lines[j].strip().startswith("#"):
                break  # Stop at first non-comment line

        # Find enclosing function
        func_node = _find_enclosing_function(tree, lineno)
        func_name = func_node.name if func_node else None
        # a tag outside a function still needs a hash, or its verification can never go stale
        hash_node = func_node or _tagged_statement(tree, lineno)
        func_hash = _hash_function_body(source_text, hash_node) if hash_node else None

        equations.append({
            "id": eq_id,
            "formula": formula,
            "file": filename,
            "line": lineno,
            "function": func_name,
            "sources": sources,
            "content_hash": func_hash,
        })

    return equations


def find_untagged(filepath, source_text=None, product_root=None):
    """Find functions with math operations but no EQ-NNN tag.

    Returns list of (function_name, line, math_op_count, indicators_found).
    """
    if source_text is None:
        source_text = read_source_text(filepath)

    try:
        tree = ast.parse(source_text)
    except SyntaxError as e:
        raise ScanError(f"syntax error in {filepath}: {e}") from None

    # Find all EQ-tagged lines
    tagged_functions = set()
    for i, line in enumerate(source_text.splitlines()):
        if EQ_TAG_RE.search(line):
            func = _find_enclosing_function(tree, i + 1)
            if func:
                tagged_functions.add(func.name)

    untagged = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.FunctionDef):
            continue
        if node.name in tagged_functions:
            continue
        # Get function source
        try:
            func_src = ast.get_source_segment(source_text, node)
        except Exception:
            func_src = None
        if not func_src:
            continue

        indicators = sorted(ind for ind in MATH_INDICATORS if ind in func_src)
        if len(indicators) >= 1:
            untagged.append({
                "function": node.name,
                "file": (Path(filepath).resolve().relative_to(Path(product_root).resolve()).as_posix()
                         if product_root else filepath.name),
                "line": node.lineno,
                "math_ops": len(indicators),
                "indicators": indicators,
            })

    return untagged


def iter_source_files(product_root):
    """Every *.py under skills/**/scripts/** — the shared walker's file set."""
    return iter_product_sources(product_root)


def scan_all_tagged(product_root):
    """Tagged equations across every walked file (quiet; used by tests and source_scan)."""
    tagged = []
    for fpath in iter_source_files(product_root):
        tagged.extend(scan_file(fpath, product_root=product_root))
    return tagged


def iter_equations(product_root):
    """Plain-dict projection for other tools: eq_id, file, line, function."""
    return [{"eq_id": e["id"], "file": e["file"], "line": e["line"], "function": e["function"]}
            for e in scan_all_tagged(product_root)]
