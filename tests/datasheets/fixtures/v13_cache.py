"""v1.3 extraction cache fixture helper.

v1.3 layout uses `datasheets/extracted/manifest.json` as an index keyed by
sanitized MPN → {file: <filename>.json, ...metadata}. Individual extraction
files live alongside the manifest. Track 2.5's `get_regulator_features`
falls back to this cache when no v1.4 cache exists for an MPN (or when v1.4
returns a topology outside the v1.3 enum).
"""
import json
from pathlib import Path
from typing import Optional

# Imports resolved via the sys.path setup in tests/datasheets/fixtures/__init__.py.
from datasheet_extract_cache import (
    EXTRACTION_VERSION, MIN_SCORE, _sanitize_mpn,
)


def write_v13_cache(
    extract_dir: Path,
    *,
    mpn: str = "LM2596-ADJ",
    topology: str = "buck",
    pins: Optional[list[dict]] = None,
    features: Optional[dict] = None,
    extraction_version: int = EXTRACTION_VERSION,
    extraction_score: float = 9.0,
) -> Path:
    """Write a minimal v1.3 extraction into extract_dir.

    Creates (or appends to) manifest.json and writes the extraction file.
    Returns the extraction file path.

    pins format (v1.3):   [{"number": "1", "name": "VIN", "function": "VIN",
                           "threshold_high_v": 1.4, "threshold_low_v": 0.4}]
    features format:      {"has_pg": True, "has_soft_start": True, "iss_time_us": 500}

    Defaults to a 'buck' regulator with minimal metadata; callers override
    as needed for divergence tests.
    """
    extract_dir.mkdir(parents=True, exist_ok=True)

    # Use the canonical v1.3 sanitizer (MD5-suffixed) so the manifest key
    # matches what get_cached_extraction() looks up.
    key = _sanitize_mpn(mpn)
    extraction_file_name = f"{key}.json"
    extraction_path = extract_dir / extraction_file_name

    extraction = {
        "extraction_metadata": {
            "extraction_version": extraction_version,
            "extraction_score": extraction_score,
            "source": "v13-fixture",
        },
        "topology": topology,
        "pins": pins or [],
        "features": features or {},
    }
    extraction_path.write_text(json.dumps(extraction))

    manifest_path = extract_dir / "manifest.json"
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text())
    else:
        manifest = {
            "version": EXTRACTION_VERSION,
            "last_updated": "",
            "extractions": {},
        }
    manifest["extractions"][key] = {"file": extraction_file_name}
    manifest_path.write_text(json.dumps(manifest))
    return extraction_path
