"""Common extractor interface."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol


@dataclass(frozen=True)
class ExtractedDocument:
    path: Path
    text: str
    metadata: dict[str, str]


class BaseExtractor(Protocol):
    def extract(self, path: Path) -> ExtractedDocument: ...
