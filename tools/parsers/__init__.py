"""
Parser package for browse_url tool.

This package provides pluggable parser interfaces for extracting and scoring
content from web pages.
"""

from .page_parser import PageParser, ContentChunk, ParsedContent
from .default_parser import DefaultParser

__all__ = ['PageParser', 'DefaultParser', 'ContentChunk', 'ParsedContent']