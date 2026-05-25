"""Split document text into overlapping chunks with source metadata."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

_SENTENCE_END = re.compile(r"(?<=[.!?。])\s+|\n+")


@dataclass(frozen=True)
class TextChunk:
    text: str
    source_path: Path
    chunk_index: int
    metadata: dict[str, str]


def _split_sentences(text: str) -> list[str]:
    parts = _SENTENCE_END.split(text.strip())
    return [p.strip() for p in parts if p.strip()]


def chunk_text(
    text: str,
    source_path: Path,
    *,
    chunk_size: int = 800,
    chunk_overlap: int = 100,
    extra_metadata: dict[str, str] | None = None,
) -> list[TextChunk]:
    """Split *text* into chunks respecting sentence boundaries when possible."""
    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")
    if chunk_overlap < 0 or chunk_overlap >= chunk_size:
        raise ValueError("chunk_overlap must be in [0, chunk_size)")

    meta = dict(extra_metadata or {})
    sentences = _split_sentences(text) if text.strip() else []
    if not sentences:
        return []

    chunks: list[str] = []
    current: list[str] = []
    current_len = 0

    for sentence in sentences:
        addition = sentence if not current else " " + sentence
        if current_len + len(addition) > chunk_size and current:
            chunks.append(" ".join(current))
            overlap_text = chunks[-1][-chunk_overlap:] if chunk_overlap else ""
            current = [overlap_text, sentence] if overlap_text else [sentence]
            current_len = sum(len(s) for s in current) + max(0, len(current) - 1)
        else:
            current.append(sentence)
            current_len += len(addition)

    if current:
        chunks.append(" ".join(current))

    return [
        TextChunk(
            text=body,
            source_path=source_path,
            chunk_index=index,
            metadata={**meta, "chunk_index": str(index)},
        )
        for index, body in enumerate(chunks)
    ]
