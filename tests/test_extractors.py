from pathlib import Path

import pytest

from src.extractors.router import ExtractionError, extract_text, supported_extensions


def test_supported_extensions() -> None:
    assert ".pdf" in supported_extensions()
    assert ".txt" in supported_extensions()


def test_extract_plain_utf8(tmp_path: Path) -> None:
    path = tmp_path / "note.txt"
    path.write_text("안녕하세요 MCP", encoding="utf-8")
    doc = extract_text(path)
    assert "안녕하세요" in doc.text
    assert doc.metadata["format"] == "txt"


def test_extract_plain_euc_kr(tmp_path: Path) -> None:
    path = tmp_path / "legacy.txt"
    path.write_bytes("한글 테스트".encode("euc-kr"))
    doc = extract_text(path)
    assert "한글" in doc.text


def test_extract_empty_txt_raises(tmp_path: Path) -> None:
    path = tmp_path / "empty.txt"
    path.write_text("   \n  ", encoding="utf-8")
    with pytest.raises(ExtractionError):
        extract_text(path)


def test_unsupported_extension_raises(tmp_path: Path) -> None:
    path = tmp_path / "image.png"
    path.write_bytes(b"\x89PNG")
    with pytest.raises(ExtractionError):
        extract_text(path)
