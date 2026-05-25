"""End-to-end indexing from folders to vector store."""

from __future__ import annotations

import logging
from pathlib import Path

from src.chunker.splitter import TextChunk, chunk_text
from src.config import Settings
from src.crawler.walker import iter_document_files, to_file_record
from src.embedder.factory import Embedder, get_embedder
from src.extractors.router import ExtractionError, extract_text
from src.storage.chroma_store import ChromaIndexStore
from src.storage.sqlite_store import SqliteIndexStore

logger = logging.getLogger(__name__)

_EMBED_BATCH = 32


class IndexPipeline:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._sqlite = SqliteIndexStore(settings.sqlite_path)
        self._chroma = ChromaIndexStore(settings)
        self._embedder: Embedder = get_embedder(settings)

    def run(self, folder: Path) -> int:
        """Index documents under *folder*. Returns newly indexed file count."""
        self._settings.ensure_data_dirs()
        folder = folder.resolve()
        discovered = 0
        indexed = 0
        skipped = 0
        failed = 0

        for path in iter_document_files(folder):
            discovered += 1
            record = to_file_record(path)
            source_path = str(record.path)

            logger.info(
                "discovered file=%s size=%s hash=%s",
                record.path,
                record.size,
                record.content_hash[:12],
            )

            if self._sqlite.is_unchanged(source_path, record.content_hash):
                skipped += 1
                logger.info("skip unchanged file=%s", path)
                continue

            try:
                document = extract_text(path)
            except ExtractionError as exc:
                failed += 1
                logger.warning("skip extract path=%s reason=%s", path, exc)
                continue

            chunks = chunk_text(
                document.text,
                path,
                chunk_size=self._settings.chunk_size,
                chunk_overlap=self._settings.chunk_overlap,
                extra_metadata=document.metadata,
            )
            if not chunks:
                failed += 1
                logger.warning("skip empty chunks path=%s", path)
                continue

            self._chroma.delete_by_path(source_path)
            self._index_chunks(source_path, chunks)
            self._sqlite.upsert(
                path=source_path,
                content_hash=record.content_hash,
                size=record.size,
                modified_at=record.modified_at,
                chunk_count=len(chunks),
            )
            indexed += 1
            logger.info(
                "indexed file=%s chars=%s chunks=%s",
                path,
                len(document.text),
                len(chunks),
            )

        logger.info(
            "index pass finished folder=%s discovered=%s indexed=%s "
            "skipped=%s failed=%s chroma_chunks=%s",
            folder,
            discovered,
            indexed,
            skipped,
            failed,
            self._chroma.count,
        )
        return indexed

    def _index_chunks(self, source_path: str, chunks: list[TextChunk]) -> None:
        for start in range(0, len(chunks), _EMBED_BATCH):
            batch = chunks[start : start + _EMBED_BATCH]
            texts = [c.text for c in batch]
            embeddings = self._embedder.embed_documents(texts)
            self._chroma.add_chunks(source_path, batch, embeddings)
