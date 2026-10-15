"""Cross-repo path bridge for the harness contract suite.

Thin re-export of :mod:`tests.product_root` — the one required product-root
bridge for every suite (review A1). ``MAIN_REPO_ROOT`` is the historical name
the contract tests use for ``PRODUCT_ROOT``.
"""
from __future__ import annotations

from tests.product_root import HARNESS_ROOT, PRODUCT_ROOT, ProductRootError  # noqa: F401

MAIN_REPO_ROOT = PRODUCT_ROOT
