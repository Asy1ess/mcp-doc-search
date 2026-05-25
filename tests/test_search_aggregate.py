from src.search.aggregate import aggregate_chunk_results


def test_aggregate_best_score_per_document() -> None:
    raw = {
        "metadatas": [
            [
                {"source_path": "/docs/report.pdf"},
                {"source_path": "/docs/report.pdf"},
                {"source_path": "/docs/other.txt"},
            ]
        ],
        "documents": [
            [
                "weaker match text",
                "strong budget proposal section",
                "unrelated",
            ]
        ],
        "distances": [[0.6, 0.1, 0.4]],
    }
    hits = aggregate_chunk_results(raw, limit=10)
    assert len(hits) == 2
    assert hits[0].path.as_posix() == "/docs/report.pdf"
    assert hits[0].score > hits[1].score
    assert "budget" in hits[0].snippet
