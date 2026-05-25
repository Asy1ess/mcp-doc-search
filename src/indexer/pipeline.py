"""End-to-end indexing from folders to vector store."""

from __future__ import annotations

import logging
from pathlib import Path

from src.config import Settings
from src.crawler.walker import iter_document_files, to_file_record

logger = logging.getLogger(__name__)


class IndexPipeline:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    def run(self, folder: Path) -> int:
        """Index documents under *folder*. Returns number of files discovered."""
        self._settings.ensure_data_dirs()
        folder = folder.resolve()
        count = 0

        for path in iter_document_files(folder):
            record = to_file_record(path)
            count += 1
            logger.info(
                "discovered file=%s size=%s hash=%s",
                record.path,
                record.size,
                record.content_hash[:12],
            )
            # TODO: extract → chunk → embed → ChromaDB + SQLite

        logger.info("index pass finished folder=%s files=%s", folder, count)
        return count
