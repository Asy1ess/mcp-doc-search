"""PDF text extraction."""

from __future__ import annotations

from pathlib import Path

import pdfplumber

from src.extractors._utils import make_document


def extract_pdf(path: Path) -> ExtractedDocument:
    pages: list[str] = []
    with pdfplumber.open(path) as pdf:
        for index, page in enumerate(pdf.pages, start=1):
            text = page.extract_text()
            if text and text.strip():
                pages.append(text.strip())

    body = "\n\n".join(pages)
    return make_document(
        path,
        body,
        format="pdf",
        page_count=str(len(pages)),
    )
