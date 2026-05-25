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

    folder = args.folder
    if not folder.exists():
        print(
            f"ERROR: Folder does not exist inside the container: {folder}\n"
            "Check DOCUMENTS_PATH in .env — /documents maps to that host folder.\n"
            "Example: DOCUMENTS_PATH=C:\\Users\\user1\\Documents and "
            "--folder /documents/test",
            file=sys.stderr,
        )
        return 1
    if not folder.is_dir():
        print(f"ERROR: Not a directory: {folder}", file=sys.stderr)
        return 1

    settings = get_settings()
    pipeline = IndexPipeline(settings)
    count = pipeline.run(folder)
    print(f"Indexing complete: {count} file(s) newly indexed under {folder}")
    if count == 0:
        print(
            "No new files indexed (folder empty, unsupported types, or all unchanged). "
            "First run downloads the embedding model and may take several minutes.",
            file=sys.stderr,
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
