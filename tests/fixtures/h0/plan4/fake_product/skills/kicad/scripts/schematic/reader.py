"""Nested package module — must be found by the recursive walker."""
from ..finding_schema import make_finding

SHEET_DEPTH_MAX = 8


def detect_nested(ctx):
    return [make_finding(
        detector="detect_nested", rule_id="NX-001", category="hierarchy",
        summary="nested", description="x", schema_era="v3.0")]
