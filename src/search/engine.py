"""Vector similarity search with document-level aggregation."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from src.config import Settings


@dataclass(frozen=True)
class SearchHit:
    path: Path
    score: float
    snippet: str


class SearchEngine:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        settings.ensure_data_dirs()

    def search(self, query: str, *, limit: int = 10) -> list[SearchHit]:
        """Semantic search over indexed chunks, aggregated by document."""
        if not query.strip():
            return []
        # TODO: embed query → ChromaDB query → aggregate by file path
        return []
