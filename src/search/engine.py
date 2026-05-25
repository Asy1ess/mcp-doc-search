"""Vector similarity search with document-level aggregation."""

from __future__ import annotations

from src.config import Settings
from src.embedder.factory import get_embedder
from src.search.aggregate import aggregate_chunk_results
from src.search.models import SearchHit
from src.storage.chroma_store import ChromaIndexStore
from src.storage.sqlite_store import SqliteIndexStore

# Re-export for callers
__all__ = ["SearchEngine", "SearchHit"]


class SearchEngine:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        settings.ensure_data_dirs()
        self._chroma = ChromaIndexStore(settings)
        self._sqlite = SqliteIndexStore(settings.sqlite_path)
        self._embedder = get_embedder(settings)

    def search(self, query: str, *, limit: int = 10) -> list[SearchHit]:
        """Semantic search over indexed chunks, aggregated by document."""
        if not query.strip():
            return []
        if self._chroma.count == 0 or self._sqlite.count_indexed() == 0:
            return []

        query_embedding = self._embedder.embed_query(query)
        n_chunks = min(max(limit * 8, limit), 100)
        raw = self._chroma.query(query_embedding, n_results=n_chunks)
        return aggregate_chunk_results(raw, limit=limit)
