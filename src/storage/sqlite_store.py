"""SQLite metadata store for indexed files."""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


@dataclass(frozen=True)
class FileIndexRow:
    path: str
    content_hash: str
    size: int
    modified_at: float
    chunk_count: int
    indexed_at: str
    status: str


_SCHEMA = """
CREATE TABLE IF NOT EXISTS files (
    path TEXT PRIMARY KEY,
    content_hash TEXT NOT NULL,
    size INTEGER NOT NULL,
    modified_at REAL NOT NULL,
    chunk_count INTEGER NOT NULL DEFAULT 0,
    indexed_at TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'indexed'
);
"""


class SqliteIndexStore:
    def __init__(self, db_path: Path) -> None:
        self._db_path = db_path
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as conn:
            conn.execute(_SCHEMA)
            conn.commit()

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self._db_path)

    def get(self, path: str) -> FileIndexRow | None:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT path, content_hash, size, modified_at, chunk_count, indexed_at, status "
                "FROM files WHERE path = ?",
                (path,),
            ).fetchone()
        if row is None:
            return None
        return FileIndexRow(*row)

    def is_unchanged(self, path: str, content_hash: str) -> bool:
        row = self.get(path)
        return row is not None and row.content_hash == content_hash

    def upsert(
        self,
        *,
        path: str,
        content_hash: str,
        size: int,
        modified_at: float,
        chunk_count: int,
        status: str = "indexed",
    ) -> None:
        indexed_at = datetime.now(timezone.utc).isoformat()
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO files (path, content_hash, size, modified_at, chunk_count, indexed_at, status)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(path) DO UPDATE SET
                    content_hash = excluded.content_hash,
                    size = excluded.size,
                    modified_at = excluded.modified_at,
                    chunk_count = excluded.chunk_count,
                    indexed_at = excluded.indexed_at,
                    status = excluded.status
                """,
                (path, content_hash, size, modified_at, chunk_count, indexed_at, status),
            )
            conn.commit()

    def count_indexed(self) -> int:
        with self._connect() as conn:
            row = conn.execute("SELECT COUNT(*) FROM files WHERE status = 'indexed'").fetchone()
        return int(row[0]) if row else 0
