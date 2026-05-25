"""Route files to the appropriate extractor by extension."""

from __future__ import annotations

from pathlib import Path

from src.extractors.base import ExtractedDocument

_NOT_IMPLEMENTED = (
    "Text extraction is not implemented yet for {suffix}. "
    "Track progress in the project Notion board."
)


def extract_text(path: Path) -> ExtractedDocument:
    suffix = path.suffix.lower()
    # MVP extractors will be added per format (pdf, docx, xlsx, ...)
    raise NotImplementedError(_NOT_IMPLEMENTED.format(suffix=suffix or "(none)"))
