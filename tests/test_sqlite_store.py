from pathlib import Path

from src.storage.sqlite_store import SqliteIndexStore


def test_sqlite_unchanged_and_upsert(tmp_path: Path) -> None:
    db = tmp_path / "index.db"
    store = SqliteIndexStore(db)

    store.upsert(
        path="/docs/a.txt",
        content_hash="hash1",
        size=10,
        modified_at=1.0,
        chunk_count=3,
    )
    assert store.is_unchanged("/docs/a.txt", "hash1")
    assert not store.is_unchanged("/docs/a.txt", "hash2")
    assert store.count_indexed() == 1
