"""
Abstract base class for page parsers.

This module defines the pluggable parser interface that allows for extensible
and specialized content extraction strategies for the browse_url tool.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class ContentChunk:
    """Represents a chunk of extracted content with relevance scores."""
    text: str
    document_score: float  # How relevant this chunk is to the overall document
    query_score: Optional[float] = None  # How relevant this chunk is to a specific query
    section: Optional[str] = None  # HTML section/tag this came from
    tag: Optional[str] = None  # Specific HTML tag


@dataclass
class ParsedContent:
    """Container for all parsed content from a web page."""
    title: str
    visible_text_chunks: List[ContentChunk]
    metadata: Dict[str, Any]
    links: List[Dict[str, str]]
    media: List[Dict[str, str]]
    source_url: str
    timestamp: str
    parser_used: str
    error: Optional[str] = None


class PageParser(ABC):
    """
    Abstract base class for page parsers.
    
    This interface defines the contract for pluggable parsers that can extract
    and score content from web pages. Parsers can be specialized for different
    domains, content types, or user requirements.
    """
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Return the name of this parser."""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """Return a description of what this parser does."""
        pass
    
    @abstractmethod
    def can_parse(self, url: str, html_content: str, mime_type: str = None) -> bool:
        """
        Determine if this parser can handle the given content.
        
        Args:
            url: The URL of the page
            html_content: The raw HTML content
            mime_type: The MIME type of the content (if known)
            
        Returns:
            True if this parser can handle the content, False otherwise
        """
        pass
    
    @abstractmethod
    def parse(self, url: str, html_content: str, title: str = "", 
              user_query: Optional[str] = None) -> ParsedContent:
        """
        Parse HTML content and extract structured information.
        
        Args:
            url: The source URL
            html_content: The HTML content to parse
            title: The page title (if already extracted)
            user_query: Optional user query for relevance scoring
            
        Returns:
            ParsedContent object with extracted and scored content
        """
        pass
    
    def chunk_text(self, text: str, max_chunk_size: int = 1000) -> List[str]:
        """
        Break text into reasonable chunks for processing.
        
        Args:
            text: The text to chunk
            max_chunk_size: Maximum size of each chunk in characters
            
        Returns:
            List of text chunks
        """
        if not text or len(text) <= max_chunk_size:
            return [text] if text else []
        
        chunks = []
        words = text.split()
        current_chunk = []
        current_length = 0
        
        for word in words:
            word_length = len(word) + 1  # +1 for space
            if current_length + word_length > max_chunk_size and current_chunk:
                chunks.append(' '.join(current_chunk))
                current_chunk = [word]
                current_length = word_length
            else:
                current_chunk.append(word)
                current_length += word_length
        
        if current_chunk:
            chunks.append(' '.join(current_chunk))
        
        return chunks