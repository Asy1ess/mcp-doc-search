"""End-to-end indexing from folders to vector store."""

from __future__ import annotations

import logging
from pathlib import Path

from src.chunker.splitter import chunk_text
from src.config import Settings
from src.crawler.walker import iter_document_files, to_file_record
from src.extractors.router import ExtractionError, extract_text

logger = logging.getLogger(__name__)


class IndexPipeline:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    def run(self, folder: Path) -> int:
        """Index documents under *folder*.

        Returns the number of files successfully extracted (discovery always runs).
        """
        self._settings.ensure_data_dirs()
        folder = folder.resolve()
        discovered = 0
        extracted = 0

        for path in iter_document_files(folder):
            discovered += 1
            record = to_file_record(path)
            logger.info(
                "discovered file=%s size=%s hash=%s",
                record.path,
                record.size,
                record.content_hash[:12],
            )

            try:
                document = extract_text(path)
            except ExtractionError as exc:
                logger.warning("skip extract path=%s reason=%s", path, exc)
                continue

            chunks = chunk_text(
                document.text,
                path,
                chunk_size=self._settings.chunk_size,
                chunk_overlap=self._settings.chunk_overlap,
                extra_metadata=document.metadata,
            )
            extracted += 1
            logger.info(
                "extracted file=%s chars=%s chunks=%s",
                path,
                len(document.text),
                len(chunks),
            )
            # TODO: embed chunks → ChromaDB + SQLite

        logger.info(
            "index pass finished folder=%s discovered=%s extracted=%s",
            folder,
            discovered,
            extracted,
        )
        return extracted
