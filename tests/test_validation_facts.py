"""Pins the validators' deliberately different guards, and that the design-intent
facts and PCB output naming come from one place (harnesslib.validation)."""

TIER = "unit"

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "validate"))

import cross_analyzer
import validate_design_intent as vdi
import validate_emc
import validate_outputs as vo


def _di(**over):
    di = {"product_class": "prototype", "ipc_class": 2, "target_market": "hobby",
          "confidence": 0.5, "detection_signals": [], "source": {}}
    di.update(over)
    return di


def _outputs_messages(di):
    ctx = vo.ValidationContext()
    vo.validate_design_intent(ctx, "x", {"design_intent": di})
    return sorted((cat, detail) for cat, items in ctx.anomalies.items()
                  for _, detail in items)


def test_absent_design_intent_is_ok_for_validate_outputs_and_an_issue_for_validate_design_intent():
    ctx = vo.ValidationContext()
    vo.validate_design_intent(ctx, "x", {})
    assert not ctx.anomalies
    assert vdi.validate_design_intent({}, "f") == [("f", "missing design_intent field")]


def test_float_ipc_class_passes_validate_outputs_and_fails_validate_design_intent():
    assert _outputs_messages(_di(ipc_class=2.0)) == []
    issues = vdi.validate_design_intent({"design_intent": _di(ipc_class=2.0)}, "f")
    assert issues == [("f", "design_intent.ipc_class is float, expected int")]


def test_null_fields_allowed_by_validate_outputs_reported_missing_by_validate_design_intent():
    di = _di(product_class=None, ipc_class=None, target_market=None,
             confidence=None, detection_signals=None, source=None)
    assert _outputs_messages(di) == []
    issues = vdi.validate_design_intent({"design_intent": di}, "f")
    assert sorted(m for _, m in issues) == sorted(
        f"design_intent.{k} is missing" for k in
        ("product_class", "ipc_class", "target_market", "confidence",
         "detection_signals", "source"))


def test_zero_pcb_layers_compared_by_cross_analyzer_skipped_by_validate_emc():
    pcb = {"statistics": {"copper_layers_used": 0}}
    emc = {"board_info": {"layer_count": 2}}
    rows = cross_analyzer.cross_validate_pcb_emc(pcb, emc)
    assert [(r["check"], r["status"]) for r in rows] == [("layer_count", "mismatch")]
    rows = validate_emc.cross_validate_file(None, pcb, emc)
    assert "layer_count" not in [r["check"] for r in rows]


def test_validate_emc_derives_pcb_without_size_check(tmp_path, monkeypatch):
    out = tmp_path / "outputs"
    pcb_dir = out / "pcb" / "o" / "r"
    pcb_dir.mkdir(parents=True)
    (pcb_dir / "a.kicad_pcb.json").write_text("")
    emc_dir = out / "emc" / "o" / "r"
    emc_dir.mkdir(parents=True)
    emc_json = emc_dir / "a.kicad_sch.json"
    emc_json.write_text("{}")
    sch_dir = out / "schematic" / "o" / "r"
    sch_dir.mkdir(parents=True)
    (sch_dir / "a.kicad_sch.json").write_text("{}")

    calls = []
    real_loads = json.loads

    class _Spy:
        JSONDecodeError = json.JSONDecodeError

        @staticmethod
        def loads(text):
            calls.append(text)
            return real_loads(text)

    monkeypatch.setattr(validate_emc, "OUTPUTS_DIR", out)
    monkeypatch.setattr(cross_analyzer, "OUTPUTS_DIR", out)
    monkeypatch.setattr(validate_emc, "json", _Spy)
    sch, pcb = validate_emc.find_source_json(emc_json)
    assert sch == {} and pcb is None
    assert "" in calls  # the empty file was read and parsed

    pairs = cross_analyzer.find_paired_outputs("o/r")
    assert [p["pcb"] for p in pairs] == [None]  # cross_analyzer skips zero-size


def test_validators_share_the_fact_objects():
    from harnesslib import validation
    assert vo._DESIGN_INTENT_REQUIRED is validation.DESIGN_INTENT_REQUIRED
    assert vo._PRODUCT_CLASSES is validation.PRODUCT_CLASSES
    assert vo._TARGET_MARKETS is validation.TARGET_MARKETS
    assert vdi.VALID_PRODUCT_CLASSES is validation.PRODUCT_CLASSES
    assert vdi.VALID_IPC_CLASSES is validation.IPC_CLASSES
    assert vdi.VALID_TARGET_MARKETS is validation.TARGET_MARKETS
    assert validation.IPC_CLASSES == {1, 2, 3}


def test_pcb_output_name():
    from harnesslib.validation import pcb_output_name
    assert pcb_output_name("a.kicad_sch.json") == "a.kicad_pcb.json"
    assert pcb_output_name("a.sch.json") == "a.kicad_pcb.json"
    assert pcb_output_name("a.json") is None
