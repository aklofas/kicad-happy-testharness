#!/usr/bin/env python3
"""Audit hardcoded constants in kicad-happy analyzer scripts.

Scans analyzer source using Python AST, builds a registry of all constants,
and tracks verification status over time.  Constants include lookup tables,
keyword lists/sets, numeric thresholds, regex patterns, and inline keyword
tuples inside any()/all() calls.

Usage:
    python3 validate/audit_constants.py scan              # Scan scripts, update registry
    python3 validate/audit_constants.py scan --diff        # Show what changed

    python3 validate/audit_constants.py list               # All constants
    python3 validate/audit_constants.py list --unverified   # Unverified only
    python3 validate/audit_constants.py list --risk critical  # Critical risk constants
    python3 validate/audit_constants.py list --risk high     # High+ risk constants
    python3 validate/audit_constants.py list --category datasheet_lookup
    python3 validate/audit_constants.py list --file signal_detectors.py
    python3 validate/audit_constants.py show CONST-001      # Detail view

    python3 validate/audit_constants.py verify CONST-001 --source "KiCad stdlib docs"
    python3 validate/audit_constants.py verify CONST-001 --entry TPS5430 --source "datasheet SLVS632L"

    python3 validate/audit_constants.py corpus              # Cross-reference against outputs
    python3 validate/audit_constants.py stats              # Summary numbers
    python3 validate/audit_constants.py report             # Full report to stdout
    python3 validate/audit_constants.py render             # Generate constants_registry.md
"""

import argparse
import ast
import hashlib
import json
import re
import sys
import textwrap
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from utils import DATA_DIR, OUTPUTS_DIR, resolve_kicad_happy_dir

REGISTRY_PATH = DATA_DIR / "constants_registry.json"
MARKDOWN_PATH = DATA_DIR / "constants_registry.md"

SCRIPTS_SUBDIR = Path("skills") / "kicad" / "scripts"
SPICE_SCRIPTS_SUBDIR = Path("skills") / "spice" / "scripts"
EMC_SCRIPTS_SUBDIR = Path("skills") / "emc" / "scripts"

# Analyzer source files to scan (relative to kicad-happy repo root)
ANALYZER_FILES = [
    "analyze_schematic.py",
    "analyze_pcb.py",
    "analyze_gerbers.py",
    "kicad_utils.py",
    "kicad_types.py",
    "signal_detectors.py",
    "sexp_parser.py",
]

# SPICE skill source files to scan
SPICE_FILES = [
    "spice_templates.py",
    "spice_results.py",
    "spice_models.py",
    "spice_part_library.py",
    "spice_model_generator.py",
    "spice_model_cache.py",
    "simulate_subcircuits.py",
]

# EMC skill source files to scan
EMC_FILES = [
    "emc_formulas.py",
    "emc_rules.py",
    "analyze_emc.py",
]


# ---------------------------------------------------------------------------
# AST Scanner
# ---------------------------------------------------------------------------

class ConstantInfo:
    """Represents a detected constant from source analysis."""

    __slots__ = (
        "name", "file", "line", "end_line", "scope", "func", "cls",
        "const_type", "value_repr", "entry_count", "content_hash",
        "entries",
    )

    def __init__(self, *, name, file, line, end_line=None, scope="module",
                 func=None, cls=None, const_type="unknown", value_repr=None,
                 entry_count=0, content_hash=None, entries=None):
        self.name = name
        self.file = file
        self.line = line
        self.end_line = end_line or line
        self.scope = scope
        self.func = func
        self.cls = cls
        self.const_type = const_type
        self.value_repr = value_repr
        self.entry_count = entry_count
        self.content_hash = content_hash
        self.entries = entries  # dict for lookup tables

    def to_dict(self):
        d = {
            "name": self.name,
            "file": self.file,
            "line": self.line,
            "end_line": self.end_line,
            "scope": self.scope,
            "type": self.const_type,
            "entry_count": self.entry_count,
            "content_hash": self.content_hash,
        }
        if self.func:
            d["function"] = self.func
        if self.cls:
            d["class"] = self.cls
        if self.entries is not None:
            d["entries"] = self.entries
        return d


def _hash_value(obj):
    """Compute SHA-256 of a canonical JSON representation."""
    canonical = json.dumps(obj, sort_keys=True, separators=(",", ":"))
    return "sha256:" + hashlib.sha256(canonical.encode()).hexdigest()[:16]


def _extract_literal(node):
    """Try to extract a Python literal value from an AST node.

    Returns the value or None if the node is not a pure literal.
    """
    try:
        return ast.literal_eval(node)
    except (ValueError, TypeError):
        return None


def _node_end_line(node):
    """Get end_lineno from a node, falling back to lineno."""
    return getattr(node, "end_lineno", None) or node.lineno


def _is_upper_case_name(name):
    """Check if a name looks like a constant (UPPER_CASE or _UPPER_CASE)."""
    stripped = name.lstrip("_")
    if not stripped:
        return False
    return (stripped == stripped.upper()) and ("_" in stripped or stripped.isupper())


def _count_string_literals(node):
    """Count string literal elements in a tuple/list/set AST node."""
    count = 0
    for elt in getattr(node, "elts", []):
        if isinstance(elt, ast.Constant) and isinstance(elt.value, str):
            count += 1
    return count


class ConstantVisitor(ast.NodeVisitor):
    """Walk AST to find hardcoded constants."""

    def __init__(self, filename):
        self.filename = filename
        self.constants = []
        self._scope_stack = []  # list of (kind, name) tuples

    @property
    def _current_func(self):
        for kind, name in reversed(self._scope_stack):
            if kind == "func":
                return name
        return None

    @property
    def _current_cls(self):
        for kind, name in reversed(self._scope_stack):
            if kind == "class":
                return name
        return None

    @property
    def _scope(self):
        if self._scope_stack:
            parts = []
            for kind, name in self._scope_stack:
                parts.append(name)
            return ".".join(parts)
        return "module"

    def visit_FunctionDef(self, node):
        self._scope_stack.append(("func", node.name))
        self.generic_visit(node)
        self._scope_stack.pop()

    visit_AsyncFunctionDef = visit_FunctionDef

    def visit_ClassDef(self, node):
        self._scope_stack.append(("class", node.name))
        self.generic_visit(node)
        self._scope_stack.pop()

    def visit_Assign(self, node):
        """Detect named constant assignments."""
        # Get the target name
        names = []
        for target in node.targets:
            if isinstance(target, ast.Name):
                names.append(target.id)

        for name in names:
            self._check_assignment(name, node.value, node.lineno)

        # Continue walking into the value to find nested constructs
        self.generic_visit(node)

    def visit_AnnAssign(self, node):
        """Detect annotated assignments like _REGULATOR_VREF: dict[str, float] = {...}."""
        if node.value and isinstance(node.target, ast.Name):
            self._check_assignment(node.target.id, node.value, node.lineno)
        self.generic_visit(node)

    # Names that are clearly local result-builder variables, not constants.
    # Only skip these inside functions — module-level assignments still detected.
    _RESULT_BUILDER_NAMES = frozenset({
        "result", "results", "entry", "item", "record", "row",
        "output", "data", "info", "details", "response",
        "comp", "component", "circuit", "pin", "net",
        "merged", "combined",
    })

    def _check_assignment(self, name, value_node, lineno):
        """Check if an assignment looks like a constant definition."""
        # Skip generic result-builder names inside functions
        if self._current_func and name in self._RESULT_BUILDER_NAMES:
            return

        # Dict with 3+ entries
        if isinstance(value_node, ast.Dict) and len(value_node.keys) >= 3:
            literal = _extract_literal(value_node)
            entries = None
            if literal and isinstance(literal, dict):
                # For dicts with numeric values, extract entries
                if all(isinstance(v, (int, float)) for v in literal.values()):
                    entries = {str(k): {"value": v} for k, v in literal.items()}
                content_hash = _hash_value(literal)
            else:
                content_hash = f"sha256:ast_{lineno}"
            self.constants.append(ConstantInfo(
                name=name, file=self.filename, line=lineno,
                end_line=_node_end_line(value_node),
                scope=self._scope, func=self._current_func, cls=self._current_cls,
                const_type="lookup_table",
                entry_count=len(value_node.keys),
                content_hash=content_hash,
                entries=entries,
            ))
            return

        # Tuple/List of 3+ string literals
        if isinstance(value_node, (ast.Tuple, ast.List)):
            str_count = _count_string_literals(value_node)
            if str_count >= 3:
                literal = _extract_literal(value_node)
                if literal:
                    content_hash = _hash_value(list(literal) if isinstance(literal, tuple) else literal)
                else:
                    content_hash = f"sha256:ast_{lineno}"
                self.constants.append(ConstantInfo(
                    name=name, file=self.filename, line=lineno,
                    end_line=_node_end_line(value_node),
                    scope=self._scope, func=self._current_func, cls=self._current_cls,
                    const_type="keyword_list",
                    entry_count=len(value_node.elts),
                    content_hash=content_hash,
                ))
                return

        # List/Tuple of 3+ tuple entries (e.g., lookup tables like _CAP_ESR_TABLE)
        if isinstance(value_node, (ast.Tuple, ast.List)):
            tuple_count = sum(1 for elt in value_node.elts
                              if isinstance(elt, ast.Tuple))
            if tuple_count >= 3:
                literal = _extract_literal(value_node)
                if literal:
                    content_hash = _hash_value([list(t) if isinstance(t, tuple) else t for t in literal])
                else:
                    content_hash = f"sha256:ast_{lineno}"
                self.constants.append(ConstantInfo(
                    name=name, file=self.filename, line=lineno,
                    end_line=_node_end_line(value_node),
                    scope=self._scope, func=self._current_func, cls=self._current_cls,
                    const_type="tuple_table",
                    entry_count=tuple_count,
                    content_hash=content_hash,
                ))
                return

        # Set literal or frozenset() call with 3+ string entries
        if isinstance(value_node, ast.Set) and _count_string_literals(value_node) >= 3:
            literal = _extract_literal(value_node)
            content_hash = _hash_value(sorted(literal)) if literal else f"sha256:ast_{lineno}"
            self.constants.append(ConstantInfo(
                name=name, file=self.filename, line=lineno,
                end_line=_node_end_line(value_node),
                scope=self._scope, func=self._current_func, cls=self._current_cls,
                const_type="keyword_set",
                entry_count=len(value_node.elts),
                content_hash=content_hash,
            ))
            return

        # frozenset({...}) call
        if (isinstance(value_node, ast.Call)
                and isinstance(value_node.func, ast.Name)
                and value_node.func.id == "frozenset"
                and value_node.args):
            inner = value_node.args[0]
            if isinstance(inner, ast.Set) and _count_string_literals(inner) >= 3:
                literal = _extract_literal(inner)
                content_hash = _hash_value(sorted(literal)) if literal else f"sha256:ast_{lineno}"
                self.constants.append(ConstantInfo(
                    name=name, file=self.filename, line=lineno,
                    end_line=_node_end_line(value_node),
                    scope=self._scope, func=self._current_func, cls=self._current_cls,
                    const_type="keyword_set",
                    entry_count=len(inner.elts),
                    content_hash=content_hash,
                ))
                return

        # Numeric constant with UPPER_CASE name
        if (isinstance(value_node, ast.Constant)
                and isinstance(value_node.value, (int, float))
                and _is_upper_case_name(name)):
            content_hash = _hash_value(value_node.value)
            self.constants.append(ConstantInfo(
                name=name, file=self.filename, line=lineno,
                end_line=_node_end_line(value_node),
                scope=self._scope, func=self._current_func, cls=self._current_cls,
                const_type="threshold",
                entry_count=1,
                content_hash=content_hash,
            ))
            return

        # re.compile() call
        if self._is_re_compile(value_node):
            pattern = self._extract_re_pattern(value_node)
            content_hash = _hash_value(pattern) if pattern else f"sha256:ast_{lineno}"
            self.constants.append(ConstantInfo(
                name=name, file=self.filename, line=lineno,
                end_line=_node_end_line(value_node),
                scope=self._scope, func=self._current_func, cls=self._current_cls,
                const_type="regex_pattern",
                entry_count=1,
                content_hash=content_hash,
            ))
            return

    def visit_Call(self, node):
        """Detect inline keyword tuples in any()/all() calls."""
        if (isinstance(node.func, ast.Name)
                and node.func.id in ("any", "all")
                and node.args):
            self._check_inline_keywords(node)
        self.generic_visit(node)

    def _check_inline_keywords(self, call_node):
        """Check for any(x in val for x in ("kw1", "kw2", ...)) patterns."""
        arg = call_node.args[0]
        if not isinstance(arg, ast.GeneratorExp):
            return
        # Look for the iterable in the generator's comprehension
        for comp in arg.generators:
            iter_node = comp.iter
            if isinstance(iter_node, (ast.Tuple, ast.List)):
                str_count = _count_string_literals(iter_node)
                if str_count >= 3:
                    # Synthetic name from function and line
                    func = self._current_func or "module"
                    name = f"{func}:{call_node.lineno}"
                    literal = _extract_literal(iter_node)
                    if literal:
                        content_hash = _hash_value(list(literal) if isinstance(literal, tuple) else literal)
                    else:
                        content_hash = f"sha256:ast_{call_node.lineno}"
                    self.constants.append(ConstantInfo(
                        name=name, file=self.filename, line=call_node.lineno,
                        end_line=_node_end_line(call_node),
                        scope=self._scope, func=self._current_func,
                        cls=self._current_cls,
                        const_type="inline_keywords",
                        entry_count=len(iter_node.elts),
                        content_hash=content_hash,
                    ))

    @staticmethod
    def _is_re_compile(node):
        """Check if node is a re.compile(...) call."""
        if not isinstance(node, ast.Call):
            return False
        func = node.func
        if isinstance(func, ast.Attribute) and func.attr == "compile":
            if isinstance(func.value, ast.Name) and func.value.id == "re":
                return True
        return False

    @staticmethod
    def _extract_re_pattern(node):
        """Extract the pattern string from re.compile(pattern)."""
        if node.args:
            first = node.args[0]
            # Handle raw strings and joined strings
            if isinstance(first, ast.Constant) and isinstance(first.value, str):
                return first.value
            if isinstance(first, ast.JoinedStr):
                return None  # f-string, can't extract statically
        return None


def scan_file(filepath):
    """Scan a single Python file for constants. Returns list of ConstantInfo."""
    try:
        source = filepath.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as e:
        print(f"  Warning: could not read {filepath}: {e}", file=sys.stderr)
        return []

    try:
        tree = ast.parse(source, filename=str(filepath))
    except SyntaxError as e:
        print(f"  Warning: syntax error in {filepath}: {e}", file=sys.stderr)
        return []

    visitor = ConstantVisitor(filepath.name)
    visitor.visit(tree)
    return visitor.constants


def scan_all(scripts_dir):
    """Scan all analyzer and SPICE source files. Returns list of ConstantInfo."""
    all_constants = []
    for fname in ANALYZER_FILES:
        fpath = scripts_dir / fname
        if not fpath.exists():
            print(f"  Skipping {fname} (not found)", file=sys.stderr)
            continue
        constants = scan_file(fpath)
        all_constants.extend(constants)
        print(f"  {fname}: {len(constants)} constants")

    # Also scan SPICE skill scripts
    spice_dir = scripts_dir.parent.parent / "spice" / "scripts"
    if spice_dir.exists():
        for fname in SPICE_FILES:
            fpath = spice_dir / fname
            if not fpath.exists():
                continue
            constants = scan_file(fpath)
            all_constants.extend(constants)
            print(f"  spice/{fname}: {len(constants)} constants")

    # Also scan EMC skill scripts
    emc_dir = scripts_dir.parent.parent / "emc" / "scripts"
    if emc_dir.exists():
        for fname in EMC_FILES:
            fpath = emc_dir / fname
            if not fpath.exists():
                continue
            constants = scan_file(fpath)
            all_constants.extend(constants)
            print(f"  emc/{fname}: {len(constants)} constants")

    return all_constants


# ---------------------------------------------------------------------------
# Category Classification
# ---------------------------------------------------------------------------

def classify_category(info):
    """Auto-classify a constant into a verification category."""
    name_upper = info.name.upper()
    name_lower = info.name.lower()

    # Physics / unit conversions
    if any(tok in name_upper for tok in ("EPSILON", "TOLERANCE", "_MM", "_MIL", "COORD")):
        return "physics"
    if info.const_type == "threshold" and any(tok in name_upper for tok in ("SNAP", "DIST", "GAP")):
        return "heuristic_threshold"

    # Regex patterns for format matching → standard
    if info.const_type == "regex_pattern":
        return "standard"

    # KiCad format codes and file extensions
    if any(tok in name_lower for tok in ("pin_type", "legacy", "gerber", "extension")):
        return "standard"

    # Type maps and classification tables (map ref designator → type, etc.)
    if any(tok in name_lower for tok in ("type_map", "type_label", "letter_name",
                                          "type_counts", "multiplier")):
        return "standard"

    # Internal control/scoring dicts — must be checked before datasheet_lookup
    if info.const_type == "lookup_table":
        if any(tok in name_lower for tok in ("order", "difficulty", "check", "count",
                                              "adequacy", "risk_")):
            return "heuristic_threshold"
        # DFM limits with numeric values
        if any(tok in name_lower for tok in ("limit", "dfm")):
            return "standard"

    # Datasheet lookup: numeric tables where keys look like part numbers
    # Must have string keys and float values, and keys should look like MPN prefixes
    if info.const_type == "lookup_table" and info.entries:
        all_numeric = all(isinstance(v.get("value"), (int, float)) for v in info.entries.values())
        if all_numeric:
            # Check if keys look like part number prefixes (letters + digits)
            part_like = sum(1 for k in info.entries
                           if re.match(r'^[A-Z][A-Z0-9]{2,}$', k, re.IGNORECASE))
            if part_like > len(info.entries) * 0.5:
                return "datasheet_lookup"
            # Named as vref, current, esl, esr → datasheet
            if any(tok in name_lower for tok in ("vref", "_iq_", "current", "esl", "esr")):
                return "datasheet_lookup"

    # Keyword lists/sets
    if info.const_type in ("keyword_list", "keyword_set", "inline_keywords"):
        return "keyword_classification"

    # Named thresholds without clear physics meaning
    if info.const_type == "threshold":
        return "heuristic_threshold"

    # Large lookup tables without numeric values → likely classification
    if info.const_type == "lookup_table":
        return "keyword_classification"

    return "unknown"


# ---------------------------------------------------------------------------
# Risk Scoring — two independent dimensions
# ---------------------------------------------------------------------------

def compute_overfit_score(info, category):
    """Compute overfitting risk (0.0-1.0).

    Measures how likely the constant is to be over-fitted to specific projects
    rather than being genuinely general.
    """
    score = 0.0
    flags = []

    # Specificity: full MPNs in what should be a prefix table
    if info.entries:
        long_keys = [k for k in info.entries if len(k) > 10]
        if long_keys:
            ratio = len(long_keys) / len(info.entries)
            specificity = min(ratio * 0.3, 0.3)
            score += specificity
            if specificity > 0.1:
                flags.append(f"specific_keys:{len(long_keys)}/{len(info.entries)}")

    # Inline keywords suggest reactive bug fixes
    if info.const_type == "inline_keywords":
        score += 0.2
        flags.append("inline_definition")

    # Very small keyword lists (2-4 entries) inside functions
    if info.const_type in ("keyword_list", "keyword_set") and info.entry_count <= 4 and info.func:
        score += 0.1
        flags.append("small_local_list")

    # Arbitrary round-number thresholds
    if info.const_type == "threshold" and category == "heuristic_threshold":
        score += 0.1
        flags.append("empirical_threshold")

    return min(score, 1.0), flags


def compute_impact_score(info, category):
    """Compute impact score (0.0-1.0): how bad is it if this constant is wrong?

    Impact tiers:
      critical (0.8-1.0) — Numeric values from datasheets that feed directly
                           into electrical calculations (voltage, current, power).
                           Wrong values produce silently incorrect designs.
      high     (0.5-0.7) — Classification tables that determine analysis paths.
                           Wrong values cause missed or phantom detections.
      medium   (0.3-0.4) — Keyword lists for IC family matching.
                           Wrong values misclassify but don't corrupt numbers.
      low      (0.0-0.2) — Format codes, unit conversions, file extensions.
                           Wrong values cause obvious failures, not silent errors.
    """
    score = 0.0
    flags = []
    name_lower = info.name.lower()

    # --- Category-based base impact ---

    if category == "datasheet_lookup":
        # Numeric values sourced from datasheets — highest impact
        score = 0.7
        flags.append("datasheet_values")

        # Voltage/current/power keywords → critical (drives electrical calcs)
        if any(tok in name_lower for tok in ("vref", "voltage", "vout")):
            score = 1.0
            flags.append("voltage_critical")
        elif any(tok in name_lower for tok in ("current", "_iq_", "_ua", "quiescent")):
            score = 0.9
            flags.append("current_critical")
        elif any(tok in name_lower for tok in ("esr", "esl", "impedance")):
            score = 0.8
            flags.append("impedance_values")

    elif category == "heuristic_threshold":
        # Empirical cutoffs — wrong values cause false pos/neg
        score = 0.4
        flags.append("empirical_cutoff")

    elif category == "keyword_classification":
        # Keyword lists — misclassification impact
        score = 0.3
        flags.append("classification_keywords")

        # Large keyword sets have more surface area for error
        if info.entry_count >= 15:
            score = min(score + 0.1, 0.5)
            flags.append("large_keyword_set")

    elif category == "standard":
        # Format codes, SI prefixes — wrong values cause obvious failures
        score = 0.1
        flags.append("standard_format")

        # Component type_map is critical — drives all downstream analysis
        if "type_map" in name_lower:
            score = 0.6
            flags.append("component_classification")

    elif category == "physics":
        # Well-known constants — low risk of being wrong
        score = 0.1
        flags.append("physics_constant")

    # --- Size amplifier: more entries = more chances for error ---
    if info.entry_count >= 30:
        score = min(score + 0.1, 1.0)
        if "large_table" not in flags:
            flags.append(f"large_table:{info.entry_count}")

    return min(score, 1.0), flags


def compute_risk_score(impact, overfit, verified_frac):
    """Combine impact and overfit into a single risk score.

    Risk represents "how urgently does this need attention?"

    Formula: max(impact * (1 - verified_fraction), overfit)

    A fully-verified high-impact constant drops to low risk.
    An overfitted constant stays risky regardless of verification.
    """
    residual_impact = impact * (1.0 - verified_frac)
    return round(max(residual_impact, overfit), 2)


def verified_fraction(entry):
    """Compute what fraction of a registry entry has been verified."""
    if entry.get("status") == "verified":
        return 1.0
    entries = entry.get("entries")
    if entries:
        total = len(entries)
        verified = sum(1 for v in entries.values() if v.get("status") == "verified")
        return verified / total if total else 0.0
    return 0.0


def risk_level(score):
    """Convert risk score to a level string."""
    if score >= 0.7:
        return "critical"
    if score >= 0.5:
        return "high"
    if score >= 0.3:
        return "medium"
    return "low"


# ---------------------------------------------------------------------------
# Registry Management
# ---------------------------------------------------------------------------

def load_registry():
    """Load the constants registry from disk."""
    if REGISTRY_PATH.exists():
        return json.loads(REGISTRY_PATH.read_text())
    return {"version": 1, "last_scan": None, "constants": []}


def save_registry(registry):
    """Save the constants registry to disk."""
    REGISTRY_PATH.parent.mkdir(parents=True, exist_ok=True)
    REGISTRY_PATH.write_text(
        json.dumps(registry, indent=2, ensure_ascii=False) + "\n"
    )


def _next_id(registry):
    """Get the next CONST-NNN ID."""
    existing = set()
    for c in registry.get("constants", []):
        cid = c.get("id", "")
        m = re.match(r"CONST-(\d+)", cid)
        if m:
            existing.add(int(m.group(1)))
    n = 1
    while n in existing:
        n += 1
    return f"CONST-{n:03d}"


def _match_existing(registry, file, scope, name):
    """Find an existing registry entry by (file, scope, name)."""
    for c in registry.get("constants", []):
        if c.get("file") == file and c.get("scope", "module") == scope and c.get("name") == name:
            return c
    return None


def update_registry(registry, scanned):
    """Merge scanned constants into the registry. Returns (added, updated, removed) counts."""
    added = updated = removed = 0

    # Build lookup of scanned by (file, scope, name) — keep first occurrence
    # Use scope to disambiguate same-named locals in different functions
    scanned_map = {}
    for info in scanned:
        key = (info.file, info.scope, info.name)
        if key not in scanned_map:
            scanned_map[key] = info

    # Update existing entries
    existing_keys = set()
    for entry in registry["constants"]:
        key = (entry["file"], entry.get("scope", "module"), entry["name"])
        existing_keys.add(key)
        if key in scanned_map:
            info = scanned_map[key]
            cat = classify_category(info)
            oscore, oflags = compute_overfit_score(info, cat)
            cscore, cflags = compute_impact_score(info, cat)
            new_data = info.to_dict()

            # Detect changes
            changed = (entry.get("content_hash") != new_data["content_hash"]
                       or entry.get("line") != new_data["line"]
                       or entry.get("entry_count") != new_data["entry_count"])

            if changed:
                updated += 1
                # Preserve verification data
                old_status = entry.get("status", "unverified")
                old_source = entry.get("source")
                old_notes = entry.get("notes")
                old_verified = entry.get("verified_entries", 0)
                old_entries_data = entry.get("entries", {})

                entry.update(new_data)
                entry["category"] = cat
                entry["overfit_score"] = round(oscore, 2)
                entry["overfit_flags"] = oflags
                entry["impact_score"] = round(cscore, 2)
                entry["impact_flags"] = cflags

                # If content hash changed, mark as needs re-verification
                if entry.get("content_hash") != new_data["content_hash"]:
                    if old_status == "verified":
                        entry["status"] = "stale"
                else:
                    entry["status"] = old_status
                    entry["source"] = old_source
                    entry["notes"] = old_notes
                    entry["verified_entries"] = old_verified

                # Merge per-entry verification for lookup tables
                if new_data.get("entries") and old_entries_data:
                    for k, v in new_data["entries"].items():
                        if k in old_entries_data:
                            old_e = old_entries_data[k]
                            v.setdefault("status", old_e.get("status", "unverified"))
                            v.setdefault("source", old_e.get("source"))
                    entry["entries"] = new_data["entries"]
            else:
                # No change — just update line numbers and scores
                entry["line"] = new_data["line"]
                entry["end_line"] = new_data["end_line"]
                entry["overfit_score"] = round(oscore, 2)
                entry["overfit_flags"] = oflags
                entry["impact_score"] = round(cscore, 2)
                entry["impact_flags"] = cflags
        # else: entry no longer found in source — will be marked removed

    # Add new entries
    for key, info in scanned_map.items():
        if key not in existing_keys:
            cat = classify_category(info)
            oscore, oflags = compute_overfit_score(info, cat)
            cscore, cflags = compute_impact_score(info, cat)
            entry = info.to_dict()
            entry["id"] = _next_id(registry)
            entry["category"] = cat
            entry["status"] = "unverified"
            entry["verified_entries"] = 0
            entry["source"] = None
            entry["notes"] = None
            entry["overfit_score"] = round(oscore, 2)
            entry["overfit_flags"] = oflags
            entry["impact_score"] = round(cscore, 2)
            entry["impact_flags"] = cflags
            if entry.get("entries"):
                for v in entry["entries"].values():
                    v["status"] = "unverified"
                    v["source"] = None
            registry["constants"].append(entry)
            added += 1

    # Mark removed entries
    to_remove = []
    for i, entry in enumerate(registry["constants"]):
        key = (entry["file"], entry.get("scope", "module"), entry["name"])
        if key not in scanned_map:
            to_remove.append(i)
            removed += 1

    for i in reversed(to_remove):
        registry["constants"].pop(i)

    # Recompute combined risk scores (depends on verification status)
    for entry in registry["constants"]:
        vf = verified_fraction(entry)
        cs = entry.get("impact_score", 0)
        os_ = entry.get("overfit_score", 0)
        entry["risk_score"] = compute_risk_score(cs, os_, vf)

    # Sort by file, then line
    registry["constants"].sort(key=lambda c: (c["file"], c.get("line", 0)))

    registry["last_scan"] = datetime.now(timezone.utc).isoformat()
    return added, updated, removed


# ---------------------------------------------------------------------------
# CLI: scan
# ---------------------------------------------------------------------------

def cmd_scan(args):
    """Scan analyzer scripts and update the registry."""
    kicad_happy = resolve_kicad_happy_dir()
    scripts_dir = kicad_happy / SCRIPTS_SUBDIR

    if not scripts_dir.exists():
        print(f"Error: {scripts_dir} not found", file=sys.stderr)
        sys.exit(1)

    print(f"Scanning {scripts_dir}")
    scanned = scan_all(scripts_dir)
    print(f"\nTotal constants found: {len(scanned)}")

    registry = load_registry()
    old_hashes = {(c["file"], c["name"]): c.get("content_hash") for c in registry["constants"]}

    added, updated, removed = update_registry(registry, scanned)
    save_registry(registry)

    print(f"\nRegistry updated: {added} added, {updated} updated, {removed} removed")
    print(f"Total entries: {len(registry['constants'])}")

    if args.diff:
        print("\n--- Changes ---")
        new_hashes = {(c["file"], c["name"]): c.get("content_hash") for c in registry["constants"]}
        for key in sorted(set(old_hashes) | set(new_hashes)):
            old_h = old_hashes.get(key)
            new_h = new_hashes.get(key)
            if old_h is None:
                print(f"  + {key[0]}:{key[1]}")
            elif new_h is None:
                print(f"  - {key[0]}:{key[1]}")
            elif old_h != new_h:
                print(f"  ~ {key[0]}:{key[1]} (hash changed)")


# ---------------------------------------------------------------------------
# CLI: list
# ---------------------------------------------------------------------------

def cmd_list(args):
    """List constants from the registry."""
    registry = load_registry()
    entries = registry.get("constants", [])

    if not entries:
        print("No constants in registry. Run 'scan' first.")
        return

    # Apply filters
    if args.unverified:
        entries = [e for e in entries if e.get("status") != "verified"]
    if args.risk:
        min_score = {"low": 0.0, "medium": 0.3, "high": 0.5,
                     "critical": 0.7}.get(args.risk, 0.0)
        entries = [e for e in entries if e.get("risk_score", 0) >= min_score]
    if args.category:
        entries = [e for e in entries if e.get("category") == args.category]
    if args.file:
        entries = [e for e in entries if e.get("file") == args.file]
    if args.type:
        entries = [e for e in entries if e.get("type") == args.type]

    if not entries:
        print("No matching constants.")
        return

    # Table output
    print(f"{'ID':<10} {'File':<25} {'Name':<30} {'Cat':<22} {'#':<4} {'Status':<10} {'Impact':<9} {'Overfit':<9} {'Risk'}")
    print("-" * 140)
    for e in entries:
        cid = e.get("id", "?")
        fname = e.get("file", "?")
        name = e.get("name", "?")
        cat = e.get("category", "?")
        count = e.get("entry_count", 0)
        status = e.get("status", "unverified")
        cscore = e.get("impact_score", 0)
        oscore = e.get("overfit_score", 0)
        rscore = e.get("risk_score", 0)
        risk = risk_level(rscore)

        # Truncate long names
        if len(name) > 29:
            name = name[:26] + "..."
        if len(fname) > 24:
            fname = fname[:21] + "..."

        print(f"{cid:<10} {fname:<25} {name:<30} {cat:<22} {count:<4} {status:<10} {cscore:<9.1f} {oscore:<9.1f} {risk:<9} ({rscore:.1f})")

    print(f"\n{len(entries)} constants")


# ---------------------------------------------------------------------------
# CLI: show
# ---------------------------------------------------------------------------

def cmd_show(args):
    """Show detail for a single constant."""
    registry = load_registry()
    entry = None
    for e in registry.get("constants", []):
        if e.get("id") == args.const_id:
            entry = e
            break

    if not entry:
        print(f"Not found: {args.const_id}", file=sys.stderr)
        sys.exit(1)

    print(f"ID:         {entry['id']}")
    print(f"Name:       {entry['name']}")
    print(f"File:       {entry['file']}:{entry['line']}-{entry.get('end_line', entry['line'])}")
    print(f"Scope:      {entry.get('scope', 'module')}")
    if entry.get("function"):
        print(f"Function:   {entry['function']}")
    if entry.get("class"):
        print(f"Class:      {entry['class']}")
    print(f"Type:       {entry['type']}")
    print(f"Category:   {entry.get('category', 'unknown')}")
    print(f"Entries:    {entry.get('entry_count', 0)}")
    print(f"Hash:       {entry.get('content_hash', 'N/A')}")
    print(f"Status:     {entry.get('status', 'unverified')}")
    if entry.get("source"):
        print(f"Source:     {entry['source']}")
    if entry.get("notes"):
        print(f"Notes:      {entry['notes']}")

    iscore = entry.get("impact_score", 0)
    oscore = entry.get("overfit_score", 0)
    rscore = entry.get("risk_score", 0)
    print(f"\nImpact:     {iscore:.2f}  {', '.join(entry.get('impact_flags', []))}")
    print(f"Overfit:    {oscore:.2f}  {', '.join(entry.get('overfit_flags', []))}")
    print(f"Risk:       {risk_level(rscore)} ({rscore:.2f})")

    # Show per-entry details for lookup tables
    entries = entry.get("entries")
    if entries:
        verified = sum(1 for v in entries.values() if v.get("status") == "verified")
        print(f"\nVerified:   {verified}/{len(entries)} entries")
        print(f"\n{'Key':<20} {'Value':<12} {'Status':<12} {'Source'}")
        print("-" * 70)
        for k, v in sorted(entries.items()):
            val = v.get("value", "?")
            st = v.get("status", "unverified")
            src = v.get("source") or ""
            print(f"{k:<20} {str(val):<12} {st:<12} {src}")


# ---------------------------------------------------------------------------
# CLI: verify
# ---------------------------------------------------------------------------

def cmd_verify(args):
    """Mark a constant or entry as verified."""
    registry = load_registry()
    entry = None
    for e in registry.get("constants", []):
        if e.get("id") == args.const_id:
            entry = e
            break

    if not entry:
        print(f"Not found: {args.const_id}", file=sys.stderr)
        sys.exit(1)

    if args.entry:
        # Verify a specific entry in a lookup table
        entries = entry.get("entries")
        if not entries:
            print(f"{args.const_id} has no per-entry data", file=sys.stderr)
            sys.exit(1)
        if args.entry not in entries:
            print(f"Entry '{args.entry}' not found in {args.const_id}", file=sys.stderr)
            sys.exit(1)
        entries[args.entry]["status"] = "verified"
        entries[args.entry]["source"] = args.source
        verified = sum(1 for v in entries.values() if v.get("status") == "verified")
        entry["verified_entries"] = verified
        if verified == len(entries):
            entry["status"] = "verified"
        print(f"Verified {args.const_id} entry '{args.entry}' ({verified}/{len(entries)})")
    else:
        # Verify the whole constant
        entry["status"] = "verified"
        entry["source"] = args.source
        if entry.get("entries"):
            for v in entry["entries"].values():
                if v.get("status") != "verified":
                    v["status"] = "verified"
                    v.setdefault("source", args.source)
            entry["verified_entries"] = len(entry["entries"])
        print(f"Verified {args.const_id}: {entry['name']}")

    # Recompute risk score (verification changes it)
    vf = verified_fraction(entry)
    entry["risk_score"] = compute_risk_score(
        entry.get("impact_score", 0), entry.get("overfit_score", 0), vf)
    print(f"Risk: {risk_level(entry['risk_score'])} ({entry['risk_score']:.2f})")

    save_registry(registry)


# ---------------------------------------------------------------------------
# CLI: stats
# ---------------------------------------------------------------------------

def cmd_stats(args):
    """Print summary statistics."""
    registry = load_registry()
    entries = registry.get("constants", [])

    if not entries:
        print("No constants in registry. Run 'scan' first.")
        return

    print(f"Last scan: {registry.get('last_scan', 'never')}")
    print(f"Total constants: {len(entries)}\n")

    # By type
    by_type = {}
    for e in entries:
        t = e.get("type", "unknown")
        by_type[t] = by_type.get(t, 0) + 1
    print("By type:")
    for t, n in sorted(by_type.items()):
        print(f"  {t:<20} {n}")

    # By category
    print()
    by_cat = {}
    for e in entries:
        c = e.get("category", "unknown")
        by_cat[c] = by_cat.get(c, 0) + 1
    print("By category:")
    for c, n in sorted(by_cat.items()):
        print(f"  {c:<25} {n}")

    # By file
    print()
    by_file = {}
    for e in entries:
        f = e.get("file", "unknown")
        by_file[f] = by_file.get(f, 0) + 1
    print("By file:")
    for f, n in sorted(by_file.items()):
        print(f"  {f:<30} {n}")

    # Verification status
    print()
    by_status = {}
    for e in entries:
        s = e.get("status", "unverified")
        by_status[s] = by_status.get(s, 0) + 1
    print("Verification status:")
    for s, n in sorted(by_status.items()):
        print(f"  {s:<15} {n}")

    # Risk distribution (combined score)
    print()
    by_risk = {"low": 0, "medium": 0, "high": 0, "critical": 0}
    for e in entries:
        r = risk_level(e.get("risk_score", 0))
        by_risk[r] += 1
    print("Risk (combined):")
    for r in ("critical", "high", "medium", "low"):
        print(f"  {r:<10} {by_risk[r]}")

    # Per-entry verification for lookup tables
    total_entries = 0
    verified_entries = 0
    for e in entries:
        if e.get("entries"):
            total_entries += len(e["entries"])
            verified_entries += e.get("verified_entries", 0)
    if total_entries:
        print(f"\nLookup table entries: {verified_entries}/{total_entries} verified")


# ---------------------------------------------------------------------------
# CLI: report
# ---------------------------------------------------------------------------

def cmd_report(args):
    """Print a full text report to stdout."""
    registry = load_registry()
    entries = registry.get("constants", [])

    if not entries:
        print("No constants in registry. Run 'scan' first.")
        return

    print("=" * 80)
    print("CONSTANTS AUDIT REPORT")
    print(f"Generated: {datetime.now(timezone.utc).isoformat()}")
    print(f"Last scan: {registry.get('last_scan', 'never')}")
    print("=" * 80)

    # Group by file
    by_file = {}
    for e in entries:
        f = e.get("file", "unknown")
        by_file.setdefault(f, []).append(e)

    for fname, file_entries in sorted(by_file.items()):
        print(f"\n{'─' * 80}")
        print(f"FILE: {fname} ({len(file_entries)} constants)")
        print(f"{'─' * 80}")

        for e in file_entries:
            rscore = e.get("risk_score", 0)
            iscore = e.get("impact_score", 0)
            oscore = e.get("overfit_score", 0)
            risk = risk_level(rscore)
            status_icon = {"verified": "+", "stale": "~", "unverified": " "}.get(e.get("status"), "?")
            print(f"\n  [{status_icon}] {e['id']} {e['name']}")
            print(f"      Line {e['line']}-{e.get('end_line', e['line'])}"
                  f"  Type: {e['type']}  Category: {e.get('category', '?')}"
                  f"  Entries: {e.get('entry_count', 0)}"
                  f"  Impact: {iscore:.1f}  Overfit: {oscore:.1f}  Risk: {risk}")
            if e.get("source"):
                print(f"      Source: {e['source']}")
            all_flags = e.get("impact_flags", []) + e.get("overfit_flags", [])
            if all_flags:
                print(f"      Flags: {', '.join(all_flags)}")

    # Summary
    verified = sum(1 for e in entries if e.get("status") == "verified")
    unverified = sum(1 for e in entries if e.get("status") == "unverified")
    critical = sum(1 for e in entries if risk_level(e.get("risk_score", 0)) == "critical")
    high_risk = sum(1 for e in entries if risk_level(e.get("risk_score", 0)) == "high")

    print(f"\n{'=' * 80}")
    print(f"SUMMARY: {len(entries)} constants, {verified} verified, "
          f"{unverified} unverified, {critical} critical, {high_risk} high-risk")
    print("=" * 80)


# ---------------------------------------------------------------------------
# CLI: render
# ---------------------------------------------------------------------------

def cmd_render(args):
    """Generate constants_registry.md from the JSON registry."""
    registry = load_registry()
    entries = registry.get("constants", [])

    if not entries:
        print("No constants in registry. Run 'scan' first.")
        return

    lines = [
        "# Constants Registry",
        "",
        f"*Auto-generated from `constants_registry.json` — do not edit manually.*",
        "",
        f"**Last scan:** {registry.get('last_scan', 'never')}",
        "",
    ]

    # Summary table
    verified = sum(1 for e in entries if e.get("status") == "verified")
    unverified = sum(1 for e in entries if e.get("status") == "unverified")
    stale = sum(1 for e in entries if e.get("status") == "stale")
    critical = sum(1 for e in entries if risk_level(e.get("risk_score", 0)) == "critical")
    high_risk = sum(1 for e in entries if risk_level(e.get("risk_score", 0)) == "high")

    lines.extend([
        "## Summary",
        "",
        f"| Metric | Count |",
        f"|--------|-------|",
        f"| Total constants | {len(entries)} |",
        f"| Verified | {verified} |",
        f"| Unverified | {unverified} |",
        f"| Stale (changed since verification) | {stale} |",
        f"| Critical risk | {critical} |",
        f"| High risk | {high_risk} |",
        "",
    ])

    # Group by file
    by_file = {}
    for e in entries:
        f = e.get("file", "unknown")
        by_file.setdefault(f, []).append(e)

    for fname, file_entries in sorted(by_file.items()):
        lines.append(f"## {fname}")
        lines.append("")
        lines.append(f"| ID | Name | Category | # | Status | Impact | Overfit | Risk |")
        lines.append(f"|---|---|---|---|---|---|---|---|")

        for e in file_entries:
            cid = e.get("id", "?")
            name = e.get("name", "?")
            cat = e.get("category", "?")
            count = e.get("entry_count", 0)
            status = e.get("status", "unverified")
            iscore = e.get("impact_score", 0)
            oscore = e.get("overfit_score", 0)
            rscore = e.get("risk_score", 0)
            risk = risk_level(rscore)

            # Escape pipe characters in names
            name = name.replace("|", "\\|")
            lines.append(f"| {cid} | `{name}` | {cat} | {count} | {status} | {iscore:.1f} | {oscore:.1f} | **{risk}** ({rscore:.1f}) |")

        lines.append("")

    # Write
    content = "\n".join(lines) + "\n"
    MARKDOWN_PATH.parent.mkdir(parents=True, exist_ok=True)
    MARKDOWN_PATH.write_text(content)
    print(f"Rendered {MARKDOWN_PATH} ({len(entries)} constants)")


# ---------------------------------------------------------------------------
# CLI: corpus — cross-reference constants against analyzer outputs
# ---------------------------------------------------------------------------

def _iter_schematic_outputs():
    """Iterate all schematic JSON output files. Yields (repo_name, path)."""
    sch_dir = OUTPUTS_DIR / "schematic"
    if not sch_dir.exists():
        return
    for repo_dir in sorted(sch_dir.iterdir()):
        if not repo_dir.is_dir():
            continue
        for jf in sorted(repo_dir.glob("*.json")):
            yield repo_dir.name, jf


def _load_json_quiet(path):
    """Load JSON, returning None on error."""
    try:
        return json.loads(path.read_text())
    except Exception:
        return None


def _match_vref_prefix(value_str, prefix_table):
    """Given a component value string, find which _REGULATOR_VREF prefix matches.

    Returns the matched prefix key or None.
    """
    candidates = [value_str.upper()]
    for candidate in candidates:
        for prefix in prefix_table:
            if candidate.startswith(prefix.upper()):
                return prefix
    return None


def _ref_prefix(ref):
    """Extract the alphabetic prefix from a reference designator."""
    prefix = ""
    for c in ref:
        if c.isalpha() or c == "#":
            prefix += c
        else:
            break
    return prefix


# Map signal_analysis section names to the constant names (in signal_detectors.py
# or kicad_utils.py) that drive their detection.  This lets us measure which
# detector functions fire across the corpus.
_SECTION_TO_CONSTANTS = {
    "power_regulators": [
        "_REGULATOR_VREF", "reg_lib_keywords", "_non_reg_exclude",
        "_switching_kw",
    ],
    "crystal_circuits": ["_osc_keywords", "_osc_exclude", "_xtal_pin_re"],
    "current_sense": ["_SENSE_PIN_PREFIXES", "_SENSE_IC_KEYWORDS", "_integrated_csa_pins"],
    "voltage_dividers": [],
    "rc_filters": [],
    "lc_filters": [],
    "opamp_circuits": ["opamp_lib_keywords"],
    "protection_devices": ["tvs_keywords"],
    "transistor_circuits": [
        "_GENERIC_TRANSISTOR_PREFIXES", "_GENERIC_TYPE_LABELS", "_PIN_LETTER_NAMES",
    ],
    "ethernet_interfaces": ["_eth_tx_rx_re", "_eth_net_re"],
    "memory_interfaces": ["memory_keywords"],
    "key_matrices": [],
    "addressable_led_chains": [],
    "buzzer_speaker_circuits": ["_LOAD_TYPE_KEYWORDS"],
    "decoupling_analysis": ["esl_by_pkg", "esr_base_by_pkg"],
}


def cmd_corpus(args):
    """Cross-reference constants against analyzer outputs to measure corpus coverage."""
    registry = load_registry()
    entries = registry.get("constants", [])

    if not entries:
        print("No constants in registry. Run 'scan' first.")
        return

    # Build lookup of registry entries by name for fast access
    by_name = {}
    for e in entries:
        by_name.setdefault(e["name"], []).append(e)

    # Get the _REGULATOR_VREF entry to extract its prefix keys
    vref_entries = {}
    vref_entry = None
    for e in entries:
        if e["name"] == "_REGULATOR_VREF" and e.get("entries"):
            vref_entry = e
            vref_entries = e["entries"]
            break

    # Get type_map entry
    type_map_entry = None
    for e in entries:
        if e["name"] == "type_map":
            type_map_entry = e
            break

    # Accumulators
    vref_hits = {}       # prefix -> set of repos
    type_hits = {}       # type_map key -> set of repos
    section_hits = {}    # section name -> set of repos
    total_repos = set()
    files_scanned = 0

    print("Scanning schematic outputs...")
    for repo, jf in _iter_schematic_outputs():
        data = _load_json_quiet(jf)
        if not data:
            continue
        files_scanned += 1
        total_repos.add(repo)

        # --- Regulator Vref lookup hits ---
        for reg in data.get("signal_analysis", {}).get("power_regulators", []):
            if reg.get("vref_source") == "lookup":
                value = reg.get("value", "")
                prefix = _match_vref_prefix(value, vref_entries)
                if prefix:
                    vref_hits.setdefault(prefix, set()).add(repo)

        # --- Component type_map hits ---
        for comp in data.get("components", []):
            ref = comp.get("reference", "")
            ctype = comp.get("type", "")
            if ref and ctype:
                prefix = _ref_prefix(ref)
                if prefix:
                    type_hits.setdefault(prefix, set()).add(repo)

        # --- Signal analysis section hits ---
        for section, items in data.get("signal_analysis", {}).items():
            if isinstance(items, list) and len(items) > 0:
                section_hits.setdefault(section, set()).add(repo)

    print(f"Scanned {files_scanned} files across {len(total_repos)} repos\n")

    # --- Update registry with corpus data ---
    total_repo_count = len(total_repos)

    # Update _REGULATOR_VREF per-entry hits
    if vref_entry and vref_entries:
        total_vref_repos = set()
        for prefix, repos in vref_hits.items():
            total_vref_repos |= repos
            if prefix in vref_entry["entries"]:
                vref_entry["entries"][prefix]["corpus_hits"] = len(repos)
                vref_entry["entries"][prefix]["corpus_repos"] = sorted(repos)
        # Zero out entries with no hits
        for prefix in vref_entry["entries"]:
            if prefix not in vref_hits:
                vref_entry["entries"][prefix]["corpus_hits"] = 0
                vref_entry["entries"][prefix].pop("corpus_repos", None)
        vref_entry["corpus_hits"] = {
            "repos": len(total_vref_repos),
            "total_repos_scanned": total_repo_count,
        }
        hit_count = sum(1 for p in vref_entries if vref_hits.get(p))
        zero_count = sum(1 for p in vref_entries if not vref_hits.get(p))
        print(f"_REGULATOR_VREF: {hit_count} prefixes matched in {len(total_vref_repos)} repos, "
              f"{zero_count} prefixes with 0 hits")

    # Update type_map corpus hits
    if type_map_entry:
        total_type_repos = set()
        for prefix, repos in type_hits.items():
            total_type_repos |= repos
        type_map_entry["corpus_hits"] = {
            "repos": len(total_type_repos),
            "total_repos_scanned": total_repo_count,
        }
        # type_map doesn't have per-entry tracking (entries is None for
        # string->string maps), so just log the summary
        used_types = len(type_hits)
        print(f"type_map: {used_types} ref prefixes used across {len(total_type_repos)} repos")

    # Update signal-analysis-linked constants
    for section, const_names in _SECTION_TO_CONSTANTS.items():
        repo_set = section_hits.get(section, set())
        for cname in const_names:
            for e in by_name.get(cname, []):
                e["corpus_hits"] = {
                    "repos": len(repo_set),
                    "section": section,
                    "total_repos_scanned": total_repo_count,
                }

    # --- Recompute overfit scores with corpus data ---
    updated = 0
    for entry in entries:
        ch = entry.get("corpus_hits")
        if not ch:
            continue
        repo_count = ch.get("repos", 0)
        old_score = entry.get("overfit_score", 0)
        old_flags = entry.get("overfit_flags", [])

        # Remove old corpus-based flags
        new_flags = [f for f in old_flags if not f.startswith("corpus_")]
        new_score = old_score

        # Subtract old corpus contribution (if any) — we'll recompute
        # The structural heuristics are small (0.0-0.2), corpus data is additive
        if repo_count == 0 and entry.get("entry_count", 0) > 0:
            new_score = min(new_score + 0.5, 1.0)
            new_flags.append("corpus_zero_hits")
        elif 0 < repo_count <= 2:
            new_score = min(new_score + 0.3, 1.0)
            new_flags.append(f"corpus_narrow:{repo_count}_repos")
        elif repo_count >= total_repo_count * 0.1:
            # Well-exercised — no overfit penalty
            new_flags.append(f"corpus_broad:{repo_count}_repos")

        # Per-entry overfit for lookup tables with per-entry corpus data
        if entry.get("entries"):
            zero_entries = sum(1 for k, v in entry["entries"].items()
                              if v.get("corpus_hits", -1) == 0)
            if zero_entries > 0:
                ratio = zero_entries / len(entry["entries"])
                new_score = min(new_score + ratio * 0.3, 1.0)
                new_flags.append(f"corpus_unused_entries:{zero_entries}/{len(entry['entries'])}")

        if new_score != old_score or new_flags != old_flags:
            entry["overfit_score"] = round(new_score, 2)
            entry["overfit_flags"] = new_flags
            updated += 1

    # Recompute combined risk scores
    for entry in entries:
        vf = verified_fraction(entry)
        entry["risk_score"] = compute_risk_score(
            entry.get("impact_score", 0), entry.get("overfit_score", 0), vf)

    save_registry(registry)

    # Print section summary
    print()
    print(f"{'Section':<30} {'Repos':<6}")
    print("-" * 40)
    for section in sorted(section_hits, key=lambda s: -len(section_hits[s])):
        print(f"{section:<30} {len(section_hits[section])}")

    # Print Vref entries with 0 hits
    if vref_entry:
        zero_prefixes = sorted(k for k in vref_entries if not vref_hits.get(k))
        if zero_prefixes:
            print(f"\nVref prefixes with 0 corpus hits ({len(zero_prefixes)}):")
            for p in zero_prefixes:
                val = vref_entries[p].get("value", "?")
                print(f"  {p:<15} Vref={val}")

    print(f"\nUpdated overfit scores for {updated} constants")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Audit hardcoded constants in kicad-happy analyzer scripts"
    )
    sub = parser.add_subparsers(dest="command")

    # scan
    p_scan = sub.add_parser("scan", help="Scan scripts, update registry")
    p_scan.add_argument("--diff", action="store_true", help="Show what changed")

    # list
    p_list = sub.add_parser("list", help="List constants")
    p_list.add_argument("--unverified", action="store_true", help="Unverified only")
    p_list.add_argument("--risk", choices=["low", "medium", "high", "critical"],
                        help="Min risk level")
    p_list.add_argument("--category", help="Filter by category")
    p_list.add_argument("--file", help="Filter by source file")
    p_list.add_argument("--type", help="Filter by constant type")

    # show
    p_show = sub.add_parser("show", help="Show detail for one constant")
    p_show.add_argument("const_id", help="Constant ID (e.g., CONST-001)")

    # verify
    p_verify = sub.add_parser("verify", help="Mark constant as verified")
    p_verify.add_argument("const_id", help="Constant ID")
    p_verify.add_argument("--source", required=True, help="Verification source")
    p_verify.add_argument("--entry", help="Specific entry key (for lookup tables)")

    # stats
    sub.add_parser("stats", help="Summary statistics")

    # report
    sub.add_parser("report", help="Full text report")

    # render
    sub.add_parser("render", help="Generate constants_registry.md")

    # corpus
    sub.add_parser("corpus", help="Cross-reference constants against outputs")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    cmds = {
        "scan": cmd_scan,
        "list": cmd_list,
        "show": cmd_show,
        "verify": cmd_verify,
        "stats": cmd_stats,
        "report": cmd_report,
        "render": cmd_render,
        "corpus": cmd_corpus,
    }
    cmds[args.command](args)


if __name__ == "__main__":
    main()
