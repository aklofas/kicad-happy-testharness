"""Contract tests for skills/kicad/review/scripts/build_review_plan.py."""

from tests.contract._paths import MAIN_REPO_ROOT, HARNESS_ROOT

import json
import sys
from pathlib import Path

sys.path.insert(0, str(MAIN_REPO_ROOT / "skills" / "kicad" / "review" / "scripts"))


def test_build_review_plan_has_two_tasks(tmp_path):
    from build_review_plan import build_plan
    plan = build_plan(analysis_dir=tmp_path)
    task_ids = sorted(t["task_id"] for t in plan["tasks"])
    assert task_ids == ["design_context", "reviewer"]


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


def test_build_review_plan_reviewer_task_paths(tmp_path):
    from build_review_plan import build_plan
    plan = build_plan(analysis_dir=tmp_path)
    rv = next(t for t in plan["tasks"] if t["task_id"] == "reviewer")
    assert "reviewer.md" in rv["prompt_path"]
    assert rv["result_path"].endswith("review_annotations.json")
    assert rv["result_schema"].endswith("review_annotations.schema.json")
