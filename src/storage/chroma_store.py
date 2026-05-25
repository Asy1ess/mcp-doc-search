"""ChromaDB vector store for text chunks."""

from __future__ import annotations

from typing import Any

import chromadb

from src.config import Settings
from src.chunker.splitter import TextChunk

COLLECTION_NAME = "mcp_doc_chunks"


class ChromaIndexStore:
    def __init__(self, settings: Settings) -> None:
        settings.ensure_data_dirs()
        self._client = chromadb.PersistentClient(path=str(settings.chroma_persist_dir))
        self._collection = self._client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},
        )

    @property
    def count(self) -> int:
        return self._collection.count()

    def delete_by_path(self, source_path: str) -> None:
        existing = self._collection.get(where={"source_path": source_path})
        if existing["ids"]:
            self._collection.delete(ids=existing["ids"])

    def add_chunks(
        self,
        source_path: str,
        chunks: list[TextChunk],
        embeddings: list[list[float]],
    ) -> None:
        if not chunks:
            return
        if len(chunks) != len(embeddings):
            raise ValueError("chunks and embeddings length mismatch")

        ids = [f"{source_path}::{chunk.chunk_index}" for chunk in chunks]
        documents = [chunk.text for chunk in chunks]
        metadatas = [
            {
                "source_path": source_path,
                "chunk_index": str(chunk.chunk_index),
                **{k: str(v) for k, v in chunk.metadata.items()},
            }
            for chunk in chunks
        ]
        self._collection.add(
            ids=ids,
            documents=documents,
            metadatas=metadatas,
            embeddings=embeddings,
        )

    def query(
        self,
        query_embedding: list[float],
        *,
        n_results: int,
    ) -> dict[str, Any]:
        return self._collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            include=["documents", "metadatas", "distances"],
        )
