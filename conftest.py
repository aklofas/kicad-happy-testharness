"""Root pytest configuration: tier markers, default selection, product-root header.

Marker derivation (review B9, TH-053): explicit markers win; else module
``TIER == "online"`` → online; else ``tests/contract/`` → offline_contract;
``integration/`` → online; everything else → unit. Default selection with no
``-m`` is ``unit or offline_contract``; pass ``--all-tiers`` or an explicit
``-m`` expression to change it.
"""
from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

HARNESS_ROOT = Path(__file__).resolve().parent
TIER_MARKERS = ("unit", "offline_contract", "corpus", "online", "perf")
DEFAULT_EXPR = "unit or offline_contract"

# Script-style online check: its body runs at import and ends in sys.exit, so
# collecting it crashes pytest. Run it as `python3 integration/test_datasheet_extraction.py`;
# converting it to pytest functions is a deferred item.
collect_ignore = ["integration/test_datasheet_extraction.py"]


def pytest_addoption(parser):
    parser.addoption("--all-tiers", action="store_true", default=False,
                     help="collect every tier (disables the default "
                          f"'{DEFAULT_EXPR}' selection)")
    parser.addoption("--manifest-out", default=None, metavar="PATH",
                     help="write {node_id: [markers]} for the collected items")


def _derived_tier(item) -> str:
    module = getattr(item, "module", None)
    tier_attr = getattr(module, "TIER", None) if module is not None else None
    if tier_attr == "online":
        return "online"
    parts = Path(str(item.fspath)).resolve().parts
    if "integration" in parts:
        return "online"
    if "contract" in parts and "tests" in parts:
        return "offline_contract"
    return "unit"


def pytest_collection_modifyitems(config, items):
    for item in items:
        if not any(item.get_closest_marker(m) for m in TIER_MARKERS):
            item.add_marker(getattr(pytest.mark, _derived_tier(item)))

    if config.getoption("-m") or config.getoption("--all-tiers"):
        return
    keep, drop = [], []
    for item in items:
        (keep if (item.get_closest_marker("unit") or item.get_closest_marker("offline_contract"))
         else drop).append(item)
    if drop:
        config.hook.pytest_deselected(items=drop)
        items[:] = keep


def pytest_collection_finish(session):
    manifest_out = session.config.getoption("--manifest-out")
    if manifest_out:
        data = {item.nodeid: sorted(m.name for m in item.iter_markers()
                                    if m.name in TIER_MARKERS) for item in session.items}
        Path(manifest_out).write_text(json.dumps(data, indent=2, sort_keys=True) + "\n",
                                      encoding="utf-8")


def pytest_report_header(config):
    lines = []
    if not (config.getoption("-m") or config.getoption("--all-tiers")):
        lines.append(f"default selection: {DEFAULT_EXPR} (use -m EXPR or --all-tiers)")
    try:
        from tests.product_root import PRODUCT_ROOT, product_sha, product_is_dirty
        lines.append(f"product_root: {PRODUCT_ROOT} sha={product_sha()}"
                     f"{' DIRTY' if product_is_dirty() else ''}")
    except Exception as e:  # noqa: BLE001 — header must never hide the real error
        lines.append(f"product_root: UNRESOLVED ({e})")
    return lines


_REQUIRED = ("unit", "offline_contract")


def _known_skips_path() -> Path:
    return Path(os.environ.get("HARNESS_KNOWN_SKIPS", HARNESS_ROOT / "tests" / "known_skips.json"))


def pytest_configure(config):
    config._harness_unlisted_skips = []
    try:
        config._harness_known_skips = json.loads(_known_skips_path().read_text(encoding="utf-8"))
    except FileNotFoundError:
        config._harness_known_skips = {}


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    if rep.skipped and not hasattr(rep, "wasxfail") \
            and any(item.get_closest_marker(m) for m in _REQUIRED) \
            and item.nodeid not in item.config._harness_known_skips:
        reason = rep.longrepr[2] if isinstance(rep.longrepr, tuple) else str(rep.longrepr)
        item.config._harness_unlisted_skips.append((item.nodeid, reason))


def pytest_sessionfinish(session, exitstatus):
    unlisted = getattr(session.config, "_harness_unlisted_skips", [])
    if unlisted:
        tr = session.config.pluginmanager.get_plugin("terminalreporter")
        if tr is not None:
            tr.write_line("")
            tr.write_line(f"unlisted skips in required tiers ({len(unlisted)}) — add to "
                          f"{_known_skips_path()} with a reason, or fix the test:", red=True)
            for nodeid, reason in unlisted:
                tr.write_line(f"  {nodeid}: {reason}")
        if session.exitstatus == 0:
            session.exitstatus = 1
