from pathlib import Path

from src.crawler.walker import iter_document_files


def test_iter_document_files_filters_extensions(tmp_path: Path) -> None:
    (tmp_path / "a.pdf").write_text("pdf", encoding="utf-8")
    (tmp_path / "b.tmp").write_text("tmp", encoding="utf-8")
    (tmp_path / "c.txt").write_text("txt", encoding="utf-8")
    (tmp_path / ".hidden").write_text("hidden", encoding="utf-8")

    found = {p.name for p in iter_document_files(tmp_path)}
    assert found == {"a.pdf", "c.txt"}
