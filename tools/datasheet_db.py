#!/usr/bin/env python3
"""Datasheet database/registry CLI. Sub-project A of v1.3 roadmap.

Usage:
    datasheet_db insert --url URL [--mpn MPN] [--manufacturer MFR]
    datasheet_db insert --file PATH [--mpn MPN] [--url URL]
    datasheet_db find MPN [--json | --open]
    datasheet_db fetch-missing [...]
    datasheet_db verify [...]
    datasheet_db stats
    datasheet_db list [--manufacturer MFR] [...]
    datasheet_db migrate [--dry-run]

Env:
    DATASHEET_DB_STORE_DIR     override datasheets/ store path
    DATASHEET_DB_MANIFEST_DIR  override reference/datasheet_manifest/ path
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from validate.datasheet_db.cli import main

if __name__ == "__main__":
    sys.exit(main())
