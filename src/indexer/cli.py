"""CLI entry point for indexing folders."""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from src.config import get_settings
from src.indexer.pipeline import IndexPipeline


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Index documents for MCP Doc Search")
    parser.add_argument(
        "--folder",
        required=True,
        type=Path,
        help="Root folder to crawl and index",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable debug logging",
    )
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(levelname)s %(name)s: %(message)s",
    )

    settings = get_settings()
    pipeline = IndexPipeline(settings)
    count = pipeline.run(args.folder)
    print(f"Indexed discovery pass complete: {count} file(s) under {args.folder}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
