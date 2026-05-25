"""CLI for manual semantic search tests."""

from __future__ import annotations

import argparse
import json
import sys

from src.config import get_settings
from src.search.engine import SearchEngine


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Search indexed documents")
    parser.add_argument("query", help="Natural language search query")
    parser.add_argument("-n", "--limit", type=int, default=10)
    args = parser.parse_args(argv)

    engine = SearchEngine(get_settings())
    hits = engine.search(args.query, limit=args.limit)
    print(json.dumps(
        [
            {
                "path": str(h.path),
                "score": round(h.score, 4),
                "snippet": h.snippet,
            }
            for h in hits
        ],
        ensure_ascii=False,
        indent=2,
    ))
    return 0


if __name__ == "__main__":
    sys.exit(main())
