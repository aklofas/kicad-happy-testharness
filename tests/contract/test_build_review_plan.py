"""Contract tests for skills/kicad/review/scripts/build_review_plan.py."""

from tests.contract._paths import MAIN_REPO_ROOT, HARNESS_ROOT

import json
import sys
from pathlib import Path

sys.path.insert(0, str(MAIN_REPO_ROOT / "skills" / "kicad" / "review" / "scripts"))


# test_build_review_plan_has_two_tasks — DELETED (spec §5):
#   reviewer task removed in v2.0; plan now has 1 task (design_context only).
#   Replaced by test_build_review_plan_has_one_task below.

def test_build_review_plan_has_one_task(tmp_path):
    """v2.0 (spec §5): reviewer task retired; plan has only design_context."""
    from build_review_plan import build_plan
    plan = build_plan(analysis_dir=tmp_path)
    task_ids = sorted(t["task_id"] for t in plan["tasks"])
    assert task_ids == ["design_context"]


def test_build_review_plan_marks_tasks_with_task_type_review(tmp_path):
    from build_review_plan import build_plan
    plan = build_plan(analysis_dir=tmp_path)
    for task in plan["tasks"]:
        assert task["task_type"] == "review"


def test_build_review_plan_validates_against_amended_plan_schema(tmp_path):
    from jsonschema import Draft202012Validator
    from build_review_plan import build_plan
    plan = build_plan(analysis_dir=tmp_path)
    schema = json.loads(
        (MAIN_REPO_ROOT / "skills" / "datasheets" / "schemas" / "plan.schema.json").read_text())
    Draft202012Validator(schema).validate(plan)


def test_build_review_plan_design_context_task_paths(tmp_path):
    from build_review_plan import build_plan
    plan = build_plan(analysis_dir=tmp_path)
    dc = next(t for t in plan["tasks"] if t["task_id"] == "design_context")
    assert "design_context.md" in dc["prompt_path"]
    assert dc["result_path"].endswith("design_context.json")
    assert dc["result_schema"].endswith("design_context.schema.json")


# test_build_review_plan_reviewer_task_paths — DELETED (spec §5):
#   reviewer task (reviewer.md, review_annotations.json) removed in v2.0.

# test_build_review_plan_reviewer_input_artifacts_include_cross_analysis — DELETED (spec §5):
#   reviewer task removed in v2.0; cross_analysis input no longer in plan.
