"""Embedding backend selection (local bge-m3 vs external API)."""

from __future__ import annotations

from typing import Protocol

from src.config import Settings


class Embedder(Protocol):
    def embed_documents(self, texts: list[str]) -> list[list[float]]: ...

    def embed_query(self, text: str) -> list[float]: ...


def get_embedder(settings: Settings) -> Embedder:
    """Return an embedder for the configured provider.

    MVP default: local ``bge-m3`` (see EMBEDDING_PROVIDER / EMBEDDING_MODEL).
    """
    raise NotImplementedError(
        f"Embedding provider '{settings.embedding_provider}' is not wired yet. "
        f"Planned model: {settings.embedding_model}"
    )
