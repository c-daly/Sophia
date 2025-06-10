"""
Default parser implementation for general web content.

This parser provides a generic approach to extracting and scoring content
from web pages, suitable for most general websites.
"""

import re
from typing import List, Dict, Any, Optional
from datetime import datetime
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup, Tag
from .page_parser import PageParser, ContentChunk, ParsedContent


class DefaultParser(PageParser):
    """Default parser for general web content."""
    
    def __init__(self, max_chunks: int = 50, max_chunk_size: int = 1000):
        """
        Initialize the default parser.
        
        Args:
            max_chunks: Maximum number of content chunks to extract
            max_chunk_size: Maximum size of each chunk in characters
        """
        self.max_chunks = max_chunks
        self.max_chunk_size = max_chunk_size
    
    @property
    def name(self) -> str:
        return "DefaultParser"
    
    @property
    def description(self) -> str:
        return "Generic parser for extracting content from web pages"
    
    def can_parse(self, url: str, html_content: str, mime_type: str = None) -> bool:
        """Default parser can handle any HTML content."""
        return True  # Default parser handles everything
    
    def parse(self, url: str, html_content: str, title: str = "", 
              user_query: Optional[str] = None) -> ParsedContent:
        """
        Parse HTML content using BeautifulSoup and extract structured information.
        
        Args:
            url: The source URL
            html_content: The HTML content to parse
            title: The page title (if already extracted)
            user_query: Optional user query for relevance scoring
            
        Returns:
            ParsedContent object with extracted and scored content
        """
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Extract title if not provided
            if not title:
                title_tag = soup.find('title')
                title = title_tag.get_text().strip() if title_tag else "Untitled"
            
            # Extract main content areas
            visible_text_chunks = self._extract_content_chunks(soup, user_query)
            
            # Extract metadata
            metadata = self._extract_metadata(soup)
            
            # Extract links
            links = self._extract_links(soup, url)
            
            # Extract media
            media = self._extract_media(soup, url)
            
            return ParsedContent(
                title=title,
                visible_text_chunks=visible_text_chunks,
                metadata=metadata,
                links=links,
                media=media,
                source_url=url,
                timestamp=datetime.now().isoformat(),
                parser_used=self.name
            )
            
        except Exception as e:
            return ParsedContent(
                title="Error",
                visible_text_chunks=[],
                metadata={},
                links=[],
                media=[],
                source_url=url,
                timestamp=datetime.now().isoformat(),
                parser_used=self.name,
                error=str(e)
            )
    
    def _extract_content_chunks(self, soup: BeautifulSoup, 
                              user_query: Optional[str] = None) -> List[ContentChunk]:
        """Extract and score content chunks from the page."""
        # Remove unwanted elements
        for element in soup(['script', 'style', 'nav', 'header', 'footer', 
                           'sidebar', 'noscript', 'iframe']):
            element.decompose()
        
        chunks = []
        
        # Priority content areas
        priority_selectors = [
            ('main', 'main'),
            ('article', 'article'),
            ('[role="main"]', 'main'),
            ('.content', 'content'),
            ('#content', 'content')
        ]
        
        # Try to find main content area first
        main_content = None
        for selector, section_name in priority_selectors:
            main_content = soup.select_one(selector)
            if main_content:
                chunks.extend(self._process_element(main_content, section_name, user_query))
                break
        
        # If no main content found, process body
        if not main_content:
            body = soup.find('body')
            if body:
                chunks.extend(self._process_element(body, 'body', user_query))
        
        # Sort by length (as a simple heuristic) and limit
        chunks = sorted(chunks, key=lambda x: len(x.text), reverse=True)
        return chunks[:self.max_chunks]
    
    def _process_element(self, element: Tag, section: str, 
                        user_query: Optional[str] = None) -> List[ContentChunk]:
        """Process a BeautifulSoup element and extract content chunks."""
        chunks = []
        
        # Process headings separately (they're important)
        for heading in element.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
            text = heading.get_text().strip()
            if text:
                chunks.append(ContentChunk(
                    text=text,
                    document_score=0.0,  # Will be calculated by the tool
                    query_score=None,    # Will be calculated by the tool
                    section=section,
                    tag=heading.name
                ))
        
        # Process paragraphs and other text containers
        for para in element.find_all(['p', 'div', 'section', 'article', 'blockquote']):
            # Skip if this element is deeply nested - only check for immediate parent relationship
            parent = para.parent
            if parent and parent != element and parent.name in ['p', 'blockquote']:
                continue
                
            text = para.get_text().strip()
            if text and len(text) > 50:  # Skip very short text
                # Chunk long text
                text_chunks = self.chunk_text(text, self.max_chunk_size)
                
                for chunk_text in text_chunks:
                    chunks.append(ContentChunk(
                        text=chunk_text,
                        document_score=0.0,  # Will be calculated by the tool
                        query_score=None,    # Will be calculated by the tool
                        section=section,
                        tag=para.name
                    ))
        
        return chunks
    
    def _extract_metadata(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract metadata from the page."""
        metadata = {}
        
        # Meta tags
        for meta in soup.find_all('meta'):
            name = meta.get('name') or meta.get('property') or meta.get('http-equiv')
            content = meta.get('content')
            if name and content:
                metadata[name.lower()] = content
        
        # Language
        html_tag = soup.find('html')
        if html_tag and html_tag.get('lang'):
            metadata['language'] = html_tag.get('lang')
        
        # Word count estimate
        text = soup.get_text()
        metadata['estimated_word_count'] = len(text.split())
        
        return metadata
    
    def _extract_links(self, soup: BeautifulSoup, base_url: str) -> List[Dict[str, str]]:
        """Extract links from the page."""
        links = []
        
        for link in soup.find_all('a', href=True):
            href = link.get('href')
            text = link.get_text().strip()
            
            if href:
                # Convert relative URLs to absolute
                absolute_url = urljoin(base_url, href)
                
                # Skip anchor links and javascript
                if not href.startswith('#') and not href.startswith('javascript:'):
                    links.append({
                        'url': absolute_url,
                        'text': text,
                        'title': link.get('title', '')
                    })
        
        return links[:50]  # Limit number of links
    
    def _extract_media(self, soup: BeautifulSoup, base_url: str) -> List[Dict[str, str]]:
        """Extract media elements from the page."""
        media = []
        
        # Images
        for img in soup.find_all('img', src=True):
            src = img.get('src')
            absolute_url = urljoin(base_url, src)
            
            media.append({
                'type': 'image',
                'url': absolute_url,
                'alt': img.get('alt', ''),
                'title': img.get('title', '')
            })
        
        # Videos
        for video in soup.find_all('video'):
            src = video.get('src')
            if src:
                absolute_url = urljoin(base_url, src)
                media.append({
                    'type': 'video',
                    'url': absolute_url,
                    'title': video.get('title', '')
                })
            
            # Check for source tags
            for source in video.find_all('source', src=True):
                src = source.get('src')
                absolute_url = urljoin(base_url, src)
                media.append({
                    'type': 'video',
                    'url': absolute_url,
                    'mime_type': source.get('type', '')
                })
        
        return media[:20]  # Limit number of media items