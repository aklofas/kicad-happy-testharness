"""PDF + cache-dir fixture helper — ported from main-repo's
kicad-happy/tests/contract/test_datasheet_lookup.py:192 per §9 of the
A3/A4 test plan and main-repo's approval note.

The port is verbatim in intent: write a cache_dir + PDF + cache JSON,
with the cache JSON's source.sha256 computed from the PDF bytes (or
overridden to simulate staleness).
"""
import hashlib
import json
from pathlib import Path
from typing import Optional

from . import FIXTURE_DIR


def _load_json(path: Path) -> dict:
    with path.open() as f:
        return json.load(f)


def write_cache_with_pdf(
    tmp_path: Path,
    *,
    mpn: str = "LM2596-ADJ",
    pdf_bytes: bytes = b"%PDF-1.4\n%%EOF\n",
    pdf_sha_override: Optional[str] = None,
    write_pdf: bool = True,
    fixture_template: str = "lm2596-adj.example.json",
) -> tuple[Path, Path]:
    """Build cache_dir + PDF + cache JSON under tmp_path.

    Layout mirrors the real datasheets convention:
      tmp_path/
        datasheets/
          {mpn}.pdf           (unless write_pdf=False — simulates missing PDF)
          extracted/
            {sanitize_mpn(mpn)}.json

    The cache JSON's source.sha256 is computed from pdf_bytes UNLESS
    pdf_sha_override is provided (used to simulate a hash-mismatch stale).

    Returns (cache_dir, pdf_path). pdf_path is returned even when
    write_pdf=False so callers can assert its non-existence.
    """
    datasheets_dir = tmp_path / "datasheets"
    datasheets_dir.mkdir(exist_ok=True)
    cache_dir = datasheets_dir / "extracted"
    cache_dir.mkdir(exist_ok=True)

    pdf_path = datasheets_dir / f"{mpn}.pdf"
    if write_pdf:
        pdf_path.write_bytes(pdf_bytes)

    actual_sha = hashlib.sha256(pdf_bytes).hexdigest()
    cached_sha = pdf_sha_override if pdf_sha_override is not None else actual_sha

    fixture = _load_json(FIXTURE_DIR / fixture_template)
    fixture["source"]["mpn"] = mpn
    fixture["source"]["sha256"] = f"sha256:{cached_sha}"
    fixture["source"]["local_path"] = f"{mpn}.pdf"

    # sanitize_mpn convention: [A-Za-z0-9_-] kept, else → _
    from datasheet_lookup import sanitize_mpn
    (cache_dir / f"{sanitize_mpn(mpn)}.json").write_text(json.dumps(fixture))
    return cache_dir, pdf_path
