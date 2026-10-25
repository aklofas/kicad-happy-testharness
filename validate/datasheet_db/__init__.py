"""Datasheet database/registry package.

Provides a content-addressed PDF store (L0) + git-tracked sharded manifest (L1)
plus a CLI (`tools/datasheet_db.py`) for insert/find/fetch-missing/migrate/
verify/stats/list operations.

Architecture and schemas are documented at
`docs/superpowers/specs/2026-04-10-datasheet-store-design.md`.
"""
