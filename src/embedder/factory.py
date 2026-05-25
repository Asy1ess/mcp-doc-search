"""Embedding backend selection (local bge-m3 vs external API)."""

from __future__ import annotations

from typing import Protocol

from src.config import Settings
from src.embedder.local import LocalEmbedder


class Embedder(Protocol):
    def embed_documents(self, texts: list[str]) -> list[list[float]]: ...

    def embed_query(self, text: str) -> list[float]: ...


def get_embedder(settings: Settings) -> Embedder:
    provider = settings.embedding_provider.lower()
    if provider == "local":
        return LocalEmbedder(settings.embedding_model)
    raise NotImplementedError(
        f"Embedding provider '{settings.embedding_provider}' is not supported yet. "
        f"Use EMBEDDING_PROVIDER=local (model: {settings.embedding_model})."
    )
