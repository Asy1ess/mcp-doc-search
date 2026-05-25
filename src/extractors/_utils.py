"""Shared extractor helpers."""

from __future__ import annotations

from pathlib import Path

import chardet

from src.extractors.base import ExtractedDocument


def decode_bytes(data: bytes) -> str:
    if not data:
        return ""
    detected = chardet.detect(data)
    encoding = detected.get("encoding") or "utf-8"
    try:
        return data.decode(encoding)
    except (LookupError, UnicodeDecodeError):
        return data.decode("utf-8", errors="replace")


def make_document(path: Path, text: str, **metadata: str) -> ExtractedDocument:
    return ExtractedDocument(
        path=path.resolve(),
        text=text.strip(),
        metadata={"source": str(path.resolve()), **metadata},
    )


def read_plain_text(path: Path) -> ExtractedDocument:
    raw = path.read_bytes()
    text = decode_bytes(raw)
    return make_document(path, text, format=path.suffix.lstrip(".").lower() or "txt")
