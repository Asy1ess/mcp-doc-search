"""Recursive folder traversal and file filtering."""

from __future__ import annotations

import hashlib
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator

SUPPORTED_EXTENSIONS = frozenset(
    {".pdf", ".docx", ".xlsx", ".pptx", ".txt", ".md", ".hwpx"}
)

SKIP_PREFIXES = ("~$", ".")
SKIP_SUFFIXES = (".tmp",)


@dataclass(frozen=True)
class FileRecord:
    path: Path
    size: int
    modified_at: float
    content_hash: str


def _should_skip(path: Path) -> bool:
    name = path.name
    if name.startswith(SKIP_PREFIXES):
        return True
    if name.endswith(SKIP_SUFFIXES):
        return True
    return False


def iter_document_files(root: Path) -> Iterator[Path]:
    """Yield supported document paths under *root* (recursive)."""
    root = root.resolve()
    if not root.is_dir():
        return

    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if not d.startswith(".")]
        for filename in filenames:
            path = Path(dirpath) / filename
            if _should_skip(path):
                continue
            if path.suffix.lower() in SUPPORTED_EXTENSIONS:
                yield path


def file_hash(path: Path, chunk_size: int = 65536) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as f:
        while block := f.read(chunk_size):
            digest.update(block)
    return digest.hexdigest()


def to_file_record(path: Path) -> FileRecord:
    stat = path.stat()
    return FileRecord(
        path=path.resolve(),
        size=stat.st_size,
        modified_at=stat.st_mtime,
        content_hash=file_hash(path),
    )
