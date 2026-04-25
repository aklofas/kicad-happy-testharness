"""Extraction differ for v1.4 datasheet cache files (spec §9).

Compares two extractions of the same MPN with domain-aware tolerance:
  - SpecValue min/typ/max: ±5% OR ±1 LSD numeric tolerance
  - SpecValue unit, enum fields, method: exact match
  - SpecValue condition: fuzzy match (Unicode + whitespace + temp notation)
  - SpecValue notes: not diffed
  - evidence.page: ±1
  - evidence.confidence: downgrades flagged as WARNING

Aggregate gold diff score: 100 = identical, deductions per deviation.
Regression triggered by any ERROR or aggregate drop >10 points.

Usage:
    python3 regression/extraction_differ.py --gold <gold.json> \\
        --candidate <candidate.json> [--json]

Exit codes:
    0 — no regression
    1 — regression detected (>=1 ERROR or score drop >10)
    2 — error (malformed input, missing files)
"""
from __future__ import annotations

import enum
import json
import re
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional


class Severity(enum.Enum):
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"
    SILENT = "silent"


class Category(enum.Enum):
    EXACT = "exact"
    NUMERIC = "numeric"
    FUZZY = "fuzzy"
    CONFIDENCE = "confidence"
    PAGE = "page"
    IGNORED = "ignored"
    STRUCTURE = "structure"


_DEDUCTION = {
    Severity.ERROR: 25,
    Severity.WARNING: 5,
    Severity.INFO: 1,
    Severity.SILENT: 0,
}


@dataclass
class DiffEntry:
    path: str
    category: Category
    severity: Severity
    summary: str
    gold_value: Any = None
    candidate_value: Any = None
    details: dict[str, Any] = field(default_factory=dict)


@dataclass
class DiffReport:
    entries: list[DiffEntry] = field(default_factory=list)

    @property
    def gold_diff_score(self) -> int:
        deduction = sum(_DEDUCTION[e.severity] for e in self.entries)
        return max(0, 100 - deduction)

    @property
    def has_regression(self) -> bool:
        if any(e.severity is Severity.ERROR for e in self.entries):
            return True
        return self.gold_diff_score < 90

    def by_severity(self, sev: Severity) -> list[DiffEntry]:
        return [e for e in self.entries if e.severity is sev]


# ===========================================================================
# Numeric tolerance — spec §9 line 623: ±5% OR ±1 LSD whichever larger
# ===========================================================================

_PCT_TOLERANCE = 0.05  # 5%


def _compute_lsd(value: float) -> float:
    """Compute the least-significant-digit step for a value.

    Uses repr() to count decimal places. Examples:
      100   -> 1
      45    -> 1
      1.23  -> 0.01
      4.7e-4 -> 1e-5  (mantissa precision after decimal scaled by exponent)

    For value=0, returns 1 (no precision signal — fall back to absolute).
    """
    if value == 0:
        return 1.0
    s = repr(abs(value))
    if "e" in s or "E" in s:
        mantissa_str, exp_str = re.split(r"[eE]", s, maxsplit=1)
        exp = int(exp_str)
        if "." in mantissa_str:
            decimals_in_mantissa = len(mantissa_str.split(".")[1])
        else:
            decimals_in_mantissa = 0
        return 10 ** (exp - decimals_in_mantissa)
    if "." in s:
        decimals = len(s.split(".")[1])
        return 10 ** (-decimals)
    return 1.0


def _numeric_within_tolerance(gold: float, candidate: float) -> bool:
    """True if candidate is within ±5% OR ±1 LSD of gold (whichever larger).

    Special case: if gold == 0, candidate must equal 0 exactly.
    """
    if gold == 0:
        return candidate == 0
    pct_delta = abs(candidate - gold) / abs(gold)
    if pct_delta <= _PCT_TOLERANCE:
        return True
    lsd = _compute_lsd(gold)
    if abs(candidate - gold) <= lsd:
        return True
    return False


# ===========================================================================
# Condition fuzzy match — spec §9 line 625
# ===========================================================================

# Unicode equivalences spec calls out specifically.
_UNICODE_EQUIVALENCES = {
    "\u00b5": "\u03bc",   # µ MICRO SIGN → μ GREEK LETTER MU
    "\u2126": "\u03a9",   # Ω OHM SIGN → Ω GREEK CAPITAL OMEGA
}

_DEGREE_SIGN = "\u00b0"   # °


def _normalize_condition(s: str) -> str:
    """Normalize a SpecValue.condition string for fuzzy comparison.

    1. Apply Unicode NFC normalization
    2. Apply spec-called-out character equivalences (µ→μ, Ω→Ω)
    3. Strip degree signs and adjacent whitespace (25°C, 25 °C, 25 C all → 25C)
    4. Collapse all whitespace runs to a single space
    5. Strip leading/trailing whitespace
    """
    s = unicodedata.normalize("NFC", s)
    for old, new in _UNICODE_EQUIVALENCES.items():
        s = s.replace(old, new)
    # Remove degree sign and adjacent whitespace: 25°C, 25 °C → 25C
    s = re.sub(r"\s*" + re.escape(_DEGREE_SIGN) + r"\s*", "", s)
    # Normalize temperature notation: 25 C, 25C both → 25C (remove space before single-letter units)
    s = re.sub(r"(\d)\s+([CF])\b", r"\1\2", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


# ===========================================================================
# SpecValue diff — combines numeric + unit + condition + evidence
# ===========================================================================

# Confidence ordering per Track 2.4.
_CONFIDENCE_ORDER = {"low": 0, "medium": 1, "high": 2}


def _diff_numeric_field(path: str, gold: Any, cand: Any) -> list[DiffEntry]:
    """Compare a numeric field (min/typ/max). Both None or absent → no entry."""
    if gold is None and cand is None:
        return []
    if gold is None or cand is None:
        return [DiffEntry(
            path=path, category=Category.STRUCTURE, severity=Severity.ERROR,
            summary=f"presence mismatch: gold={gold!r}, cand={cand!r}",
            gold_value=gold, candidate_value=cand,
        )]
    if not isinstance(gold, (int, float)) or not isinstance(cand, (int, float)):
        return [DiffEntry(
            path=path, category=Category.EXACT, severity=Severity.ERROR,
            summary=f"non-numeric mismatch: {gold!r} vs {cand!r}",
            gold_value=gold, candidate_value=cand,
        )]
    if gold == cand:
        return []
    if _numeric_within_tolerance(gold, cand):
        delta_pct = abs(cand - gold) / abs(gold) * 100 if gold != 0 else 0
        return [DiffEntry(
            path=path, category=Category.NUMERIC, severity=Severity.SILENT,
            summary=f"{gold} vs {cand} (Δ={delta_pct:.2f}%, within tolerance)",
            gold_value=gold, candidate_value=cand,
            details={"delta_pct": round(delta_pct, 2)},
        )]
    delta_pct = abs(cand - gold) / abs(gold) * 100 if gold != 0 else float("inf")
    return [DiffEntry(
        path=path, category=Category.NUMERIC, severity=Severity.WARNING,
        summary=f"{gold} vs {cand} (Δ={delta_pct:.2f}%, OUTSIDE tolerance)",
        gold_value=gold, candidate_value=cand,
        details={"delta_pct": round(delta_pct, 2)},
    )]


def _diff_evidence(path_prefix: str, gold_ev: dict, cand_ev: dict) -> list[DiffEntry]:
    """Diff an evidence sub-dict per spec §9 lines 627-630."""
    entries = []

    g_page = gold_ev.get("page")
    c_page = cand_ev.get("page")
    if g_page is not None and c_page is not None and g_page != c_page:
        page_path = f"{path_prefix}.page"
        if abs(g_page - c_page) <= 1:
            entries.append(DiffEntry(
                path=page_path, category=Category.PAGE, severity=Severity.SILENT,
                summary=f"page {g_page} vs {c_page} (within ±1)",
                gold_value=g_page, candidate_value=c_page,
            ))
        else:
            entries.append(DiffEntry(
                path=page_path, category=Category.PAGE, severity=Severity.WARNING,
                summary=f"page {g_page} vs {c_page} (outside ±1)",
                gold_value=g_page, candidate_value=c_page,
            ))

    g_sec = gold_ev.get("section")
    c_sec = cand_ev.get("section")
    if g_sec is not None and c_sec is not None:
        if _normalize_condition(g_sec) != _normalize_condition(c_sec):
            entries.append(DiffEntry(
                path=f"{path_prefix}.section", category=Category.FUZZY,
                severity=Severity.INFO,
                summary=f"section: {g_sec!r} vs {c_sec!r}",
                gold_value=g_sec, candidate_value=c_sec,
            ))

    g_conf = gold_ev.get("confidence")
    c_conf = cand_ev.get("confidence")
    if g_conf is not None and c_conf is not None and g_conf != c_conf:
        g_rank = _CONFIDENCE_ORDER.get(g_conf, -1)
        c_rank = _CONFIDENCE_ORDER.get(c_conf, -1)
        if c_rank < g_rank:
            entries.append(DiffEntry(
                path=f"{path_prefix}.confidence", category=Category.CONFIDENCE,
                severity=Severity.WARNING,
                summary=f"confidence downgrade: {g_conf} → {c_conf}",
                gold_value=g_conf, candidate_value=c_conf,
            ))

    g_method = gold_ev.get("method")
    c_method = cand_ev.get("method")
    if g_method != c_method:
        entries.append(DiffEntry(
            path=f"{path_prefix}.method", category=Category.EXACT,
            severity=Severity.ERROR,
            summary=f"method mismatch: {g_method!r} vs {c_method!r}",
            gold_value=g_method, candidate_value=c_method,
        ))

    return entries


def _diff_specvalue(path: str, gold: dict, cand: dict) -> list[DiffEntry]:
    """Diff two SpecValue dicts. Path is the dotted path to the SpecValue."""
    entries = []

    for key in ("min", "typ", "max"):
        entries.extend(_diff_numeric_field(f"{path}.{key}",
                                           gold.get(key), cand.get(key)))

    g_unit = gold.get("unit")
    c_unit = cand.get("unit")
    if g_unit != c_unit:
        entries.append(DiffEntry(
            path=f"{path}.unit", category=Category.EXACT,
            severity=Severity.ERROR,
            summary=f"unit mismatch: {g_unit!r} vs {c_unit!r}",
            gold_value=g_unit, candidate_value=c_unit,
        ))

    g_cond = gold.get("condition")
    c_cond = cand.get("condition")
    if g_cond is not None and c_cond is not None:
        if _normalize_condition(g_cond) != _normalize_condition(c_cond):
            entries.append(DiffEntry(
                path=f"{path}.condition", category=Category.FUZZY,
                severity=Severity.INFO,
                summary=f"condition divergence: {g_cond!r} vs {c_cond!r}",
                gold_value=g_cond, candidate_value=c_cond,
            ))

    # notes: NOT DIFFED (per spec line 626)

    g_ev = gold.get("evidence") or {}
    c_ev = cand.get("evidence") or {}
    entries.extend(_diff_evidence(f"{path}.evidence", g_ev, c_ev))

    return entries


# ===========================================================================
# Top-level walker — diff_extractions
# ===========================================================================

# Fields not diffed at the top level (advisory, runtime-state, or gated elsewhere).
_IGNORED_TOP_LEVEL = {
    "extraction",   # run-time metadata: timestamps, run_id
    "source",       # PDF SHA, local path — gated by Check 4 of acceptance gate
}


def _is_specvalue(d: Any) -> bool:
    """Heuristic: a dict containing any of {min, typ, max} is a SpecValue."""
    if not isinstance(d, dict):
        return False
    return any(k in d for k in ("min", "typ", "max"))


def _diff_value(path: str, gold: Any, cand: Any) -> list[DiffEntry]:
    """Recursively diff two values. Returns a list of DiffEntry."""
    if gold is None and cand is None:
        return []
    if gold is None:
        return [DiffEntry(
            path=path, category=Category.STRUCTURE, severity=Severity.ERROR,
            summary="added field not in gold (extra in candidate)",
            gold_value=None, candidate_value=cand,
        )]
    if cand is None:
        return [DiffEntry(
            path=path, category=Category.STRUCTURE, severity=Severity.ERROR,
            summary="missing required field (present in gold)",
            gold_value=gold, candidate_value=None,
        )]
    # Type mismatch (allow int/float interop)
    if type(gold) is not type(cand):
        if not (isinstance(gold, (int, float)) and isinstance(cand, (int, float))
                and not isinstance(gold, bool) and not isinstance(cand, bool)):
            return [DiffEntry(
                path=path, category=Category.STRUCTURE, severity=Severity.ERROR,
                summary=f"type mismatch: {type(gold).__name__} vs {type(cand).__name__}",
                gold_value=gold, candidate_value=cand,
            )]
    # SpecValue dict
    if _is_specvalue(gold):
        return _diff_specvalue(path, gold, cand)
    # Generic dict — recurse keys
    if isinstance(gold, dict):
        entries = []
        all_keys = set(gold.keys()) | set(cand.keys())
        for k in sorted(all_keys):
            entries.extend(_diff_value(f"{path}.{k}" if path else k,
                                        gold.get(k), cand.get(k)))
        return entries
    # List
    if isinstance(gold, list):
        entries = []
        if len(gold) != len(cand):
            entries.append(DiffEntry(
                path=path, category=Category.STRUCTURE, severity=Severity.ERROR,
                summary=f"list length mismatch: gold={len(gold)}, cand={len(cand)}",
                gold_value=gold, candidate_value=cand,
            ))
        for i in range(min(len(gold), len(cand))):
            entries.extend(_diff_value(f"{path}[{i}]", gold[i], cand[i]))
        return entries
    # Scalar — exact equality
    if gold != cand:
        return [DiffEntry(
            path=path, category=Category.EXACT, severity=Severity.ERROR,
            summary=f"value mismatch: {gold!r} vs {cand!r}",
            gold_value=gold, candidate_value=cand,
        )]
    return []


def diff_extractions(*, gold: dict, candidate: dict) -> DiffReport:
    """Diff two v1.4 extraction dicts. Returns a DiffReport."""
    report = DiffReport()
    all_keys = (set(gold.keys()) | set(candidate.keys())) - _IGNORED_TOP_LEVEL
    for k in sorted(all_keys):
        report.entries.extend(_diff_value(k, gold.get(k), candidate.get(k)))
    return report


# ===========================================================================
# Report rendering + CLI
# ===========================================================================

def render_text_report(report: DiffReport) -> str:
    """Render a DiffReport as left-aligned text for stdout."""
    lines = []
    by_sev = {sev: report.by_severity(sev) for sev in Severity}

    for sev in (Severity.ERROR, Severity.WARNING, Severity.INFO):
        items = by_sev[sev]
        if not items:
            continue
        lines.append(f"\n=== {sev.value.upper()} ({len(items)}) ===")
        for e in items:
            lines.append(f"  {e.path}")
            lines.append(f"    {e.category.value}: {e.summary}")

    silent = by_sev[Severity.SILENT]
    if silent:
        lines.append(f"\n=== SILENT ({len(silent)} within tolerance) ===")

    score = report.gold_diff_score
    n_err = len(by_sev[Severity.ERROR])
    n_warn = len(by_sev[Severity.WARNING])
    n_info = len(by_sev[Severity.INFO])
    deduction = 100 - score
    lines.append("")
    lines.append(f"Gold diff score: {score}/100 "
                 f"({n_err} ERROR, {n_warn} WARNING, {n_info} INFO; -{deduction} pts)")
    lines.append(f"Regression: {'YES' if report.has_regression else 'NO'}")
    return "\n".join(lines)


def compute_exit_code(report: DiffReport) -> int:
    """0 = no regression, 1 = regression."""
    return 1 if report.has_regression else 0


def main(argv: Optional[list[str]] = None) -> int:
    import argparse
    parser = argparse.ArgumentParser(
        description="Diff two v1.4 datasheet extractions per spec §9 tolerance.")
    parser.add_argument("--gold", required=True, type=Path,
                        help="Path to the gold/reference extraction JSON.")
    parser.add_argument("--candidate", required=True, type=Path,
                        help="Path to the candidate extraction JSON.")
    parser.add_argument("--json", action="store_true",
                        help="Emit JSON report instead of text.")
    args = parser.parse_args(argv)

    if not args.gold.exists():
        print(f"ERROR: gold file not found: {args.gold}")
        return 2
    if not args.candidate.exists():
        print(f"ERROR: candidate file not found: {args.candidate}")
        return 2

    try:
        gold = json.loads(args.gold.read_text())
        candidate = json.loads(args.candidate.read_text())
    except (OSError, json.JSONDecodeError) as e:
        print(f"ERROR: file unreadable: {e}")
        return 2

    report = diff_extractions(gold=gold, candidate=candidate)

    if args.json:
        payload = {
            "gold_diff_score": report.gold_diff_score,
            "has_regression": report.has_regression,
            "entries": [
                {"path": e.path, "category": e.category.value,
                 "severity": e.severity.value, "summary": e.summary,
                 "gold_value": e.gold_value, "candidate_value": e.candidate_value,
                 "details": e.details}
                for e in report.entries
            ],
        }
        print(json.dumps(payload, indent=2, default=str))
    else:
        print(render_text_report(report))

    return compute_exit_code(report)


if __name__ == "__main__":
    import sys
    sys.exit(main())
