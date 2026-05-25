"""HWPX (Hancom Word) text extraction via OWPML XML in ZIP."""

from __future__ import annotations

import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

from src.extractors._utils import make_document


def _collect_element_text(element: ET.Element) -> str:
    parts: list[str] = []
    if element.text and element.text.strip():
        parts.append(element.text.strip())
    for child in element:
        child_text = _collect_element_text(child)
        if child_text:
            parts.append(child_text)
        if child.tail and child.tail.strip():
            parts.append(child.tail.strip())
    return " ".join(parts)


def extract_hwpx(path: Path) -> ExtractedDocument:
    texts: list[str] = []

    with zipfile.ZipFile(path, "r") as archive:
        for name in sorted(archive.namelist()):
            if not name.lower().endswith(".xml"):
                continue
            if "Contents/" not in name and "content" not in name.lower():
                continue
            try:
                raw = archive.read(name)
                root = ET.fromstring(raw)
            except (ET.ParseError, KeyError, zipfile.BadZipFile):
                continue
            body = _collect_element_text(root)
            if body:
                texts.append(body)

    return make_document(path, "\n\n".join(texts), format="hwpx")
