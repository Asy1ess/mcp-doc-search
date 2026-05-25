"""MCP server — stdio transport for Claude Desktop and other hosts."""

from __future__ import annotations

import json
from pathlib import Path

from fastmcp import FastMCP

from src.config import get_settings
from src.indexer.pipeline import IndexPipeline
from src.search.engine import SearchEngine

mcp = FastMCP(
    name="MCP Doc Search",
    instructions=(
        "Search the user's locally indexed documents by meaning, not exact filenames. "
        "Use search_documents for queries; get_document_content for full text when needed."
    ),
)


def _settings():
    return get_settings()


@mcp.tool()
def search_documents(query: str, limit: int = 10) -> str:
    """Search indexed documents by semantic similarity to the query.

    Args:
        query: Natural language search query (Korean or English).
        limit: Maximum number of document results (default 10).
    """
    settings = _settings()
    engine = SearchEngine(settings)
    hits = engine.search(query, limit=limit)
    if not hits:
        return (
            "No matching documents yet. "
            "Run indexing first (reindex tool or `docker compose run --rm app "
            "python -m src.indexer.cli --folder /documents`)."
        )
    payload = [
        {
            "path": str(h.path),
            "score": round(h.score, 4),
            "snippet": h.snippet,
        }
        for h in hits
    ]
    return json.dumps(payload, ensure_ascii=False, indent=2)


@mcp.tool()
def get_document_content(path: str, max_chars: int = 8000) -> str:
    """Return extracted text from a file at the given path.

    Args:
        path: Absolute or indexed file path.
        max_chars: Truncate output to this many characters (default 8000).
    """
    from src.extractors.router import extract_text

    file_path = Path(path)
    if not file_path.is_file():
        return f"File not found: {path}"
    doc = extract_text(file_path)
    text = doc.text[:max_chars]
    if len(doc.text) > max_chars:
        text += "\n\n[... truncated ...]"
    return text


@mcp.tool()
def list_indexed_folders() -> str:
    """List folders configured for indexing (INDEX_FOLDERS env)."""
    settings = _settings()
    return json.dumps(settings.index_folders, ensure_ascii=False, indent=2)


@mcp.tool()
def reindex(folder: str | None = None) -> str:
    """Run an indexing pass on a folder (default: first INDEX_FOLDERS entry).

    Args:
        folder: Root directory to index; uses INDEX_FOLDERS[0] when omitted.
    """
    settings = _settings()
    target = Path(folder) if folder else Path(settings.index_folders[0])
    if not target.is_dir():
        return f"Folder does not exist or is not a directory: {target}"
    count = IndexPipeline(settings).run(target)
    return f"Discovery pass indexed {count} supported file(s) under {target}"


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
