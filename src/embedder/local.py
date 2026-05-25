"""Local embedding via sentence-transformers (BGE-M3)."""

from __future__ import annotations

from typing import ClassVar

_QUERY_PREFIX = "Represent this sentence for searching relevant passages: "


class LocalEmbedder:
    """Lazy-loaded SentenceTransformer backend."""

    _models: ClassVar[dict[str, object]] = {}

    def __init__(self, model_name: str) -> None:
        self._model_name = model_name

    def _model(self):
        if self._model_name not in LocalEmbedder._models:
            from sentence_transformers import SentenceTransformer

            LocalEmbedder._models[self._model_name] = SentenceTransformer(
                self._model_name
            )
        return LocalEmbedder._models[self._model_name]

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        vectors = self._model().encode(
            texts,
            normalize_embeddings=True,
            show_progress_bar=False,
        )
        return vectors.tolist()

    def embed_query(self, text: str) -> list[float]:
        prefixed = _QUERY_PREFIX + text.strip()
        vector = self._model().encode(
            [prefixed],
            normalize_embeddings=True,
            show_progress_bar=False,
        )[0]
        return vector.tolist()
