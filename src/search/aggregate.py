"""Aggregate chunk-level vector hits into document-level results."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from src.search.models import SearchHit

_SNIPPET_LEN = 320


def _distance_to_score(distance: float) -> float:
    """Convert Chroma cosine distance to a higher-is-better similarity score."""
    return max(0.0, 1.0 - distance)


def aggregate_chunk_results(
    chroma_result: dict[str, Any],
    *,
    limit: int,
) -> list[SearchHit]:
    metadatas = (chroma_result.get("metadatas") or [[]])[0]
    documents = (chroma_result.get("documents") or [[]])[0]
    distances = (chroma_result.get("distances") or [[]])[0]

    best: dict[str, SearchHit] = {}

    for meta, document, distance in zip(metadatas, documents, distances, strict=True):
        source = meta.get("source_path")
        if not source:
            continue
        score = _distance_to_score(float(distance))
        snippet = (document or "").strip().replace("\n", " ")
        if len(snippet) > _SNIPPET_LEN:
            snippet = snippet[:_SNIPPET_LEN] + "…"

        current = best.get(source)
        if current is None or score > current.score:
            best[source] = SearchHit(path=Path(source), score=score, snippet=snippet)

    hits = sorted(best.values(), key=lambda h: h.score, reverse=True)
    return hits[:limit]
