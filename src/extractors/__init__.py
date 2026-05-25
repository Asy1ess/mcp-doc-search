"""Format-specific text extractors."""

from src.extractors.base import ExtractedDocument
from src.extractors.router import extract_text

__all__ = ["ExtractedDocument", "extract_text"]
