"""Application settings loaded from environment variables."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    embedding_provider: str
    embedding_model: str
    chroma_persist_dir: Path
    sqlite_path: Path
    index_folders: list[str]
    chunk_size: int
    chunk_overlap: int

    @classmethod
    def from_env(cls) -> Settings:
        raw_folders = os.getenv("INDEX_FOLDERS", "/documents")
        return cls(
            embedding_provider=os.getenv("EMBEDDING_PROVIDER", "local"),
            embedding_model=os.getenv("EMBEDDING_MODEL", "BAAI/bge-m3"),
            chroma_persist_dir=Path(
                os.getenv("CHROMA_PERSIST_DIR", "./data/chroma")
            ),
            sqlite_path=Path(os.getenv("SQLITE_PATH", "./data/index.db")),
            index_folders=[f.strip() for f in raw_folders.split(",") if f.strip()],
            chunk_size=int(os.getenv("CHUNK_SIZE", "800")),
            chunk_overlap=int(os.getenv("CHUNK_OVERLAP", "100")),
        )

    def ensure_data_dirs(self) -> None:
        self.chroma_persist_dir.mkdir(parents=True, exist_ok=True)
        self.sqlite_path.parent.mkdir(parents=True, exist_ok=True)


def get_settings() -> Settings:
    return Settings.from_env()
