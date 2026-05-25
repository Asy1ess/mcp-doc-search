"""Route files to the appropriate extractor by extension."""

from __future__ import annotations

import logging
from collections.abc import Callable
from pathlib import Path

from src.extractors._utils import read_plain_text
from src.extractors.base import ExtractedDocument
from src.extractors.docx_extractor import extract_docx
from src.extractors.hwpx_extractor import extract_hwpx
from src.extractors.pdf_extractor import extract_pdf
from src.extractors.pptx_extractor import extract_pptx
from src.extractors.xlsx_extractor import extract_xlsx

logger = logging.getLogger(__name__)

ExtractorFn = Callable[[Path], ExtractedDocument]

_REGISTRY: dict[str, ExtractorFn] = {
    ".txt": read_plain_text,
    ".md": read_plain_text,
    ".pdf": extract_pdf,
    ".docx": extract_docx,
    ".xlsx": extract_xlsx,
    ".pptx": extract_pptx,
    ".hwpx": extract_hwpx,
}


class ExtractionError(Exception):
    """Raised when a file cannot be extracted."""


def extract_text(path: Path) -> ExtractedDocument:
    """Extract plain text from *path* using the matching format handler."""
    suffix = path.suffix.lower()
    handler = _REGISTRY.get(suffix)
    if handler is None:
        raise ExtractionError(f"Unsupported extension: {suffix or '(none)'}")

    try:
        document = handler(path)
    except Exception as exc:  # noqa: BLE001 — log and wrap per file
        logger.warning("extraction failed path=%s error=%s", path, exc)
        raise ExtractionError(str(exc)) from exc

    if not document.text.strip():
        raise ExtractionError(f"No extractable text in file: {path}")

    return document


def supported_extensions() -> frozenset[str]:
    return frozenset(_REGISTRY.keys())
