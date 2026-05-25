"""Search result types."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class SearchHit:
    path: Path
    score: float
    snippet: str
