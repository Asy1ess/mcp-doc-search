"""Indexing pipeline: crawl → extract → chunk → embed → store."""

from src.indexer.pipeline import IndexPipeline

__all__ = ["IndexPipeline"]
