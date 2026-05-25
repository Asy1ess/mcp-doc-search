from pathlib import Path

from src.chunker.splitter import chunk_text


def test_chunk_text_respects_overlap_and_metadata() -> None:
    text = "First sentence here. Second sentence follows. Third ends the doc."
    chunks = chunk_text(
        text,
        Path("/docs/sample.txt"),
        chunk_size=40,
        chunk_overlap=5,
        extra_metadata={"page": "1"},
    )
    assert len(chunks) >= 2
    assert chunks[0].metadata["page"] == "1"
    assert chunks[0].source_path == Path("/docs/sample.txt")
