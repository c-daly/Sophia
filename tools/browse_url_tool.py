"""
BrowseUrlTool - A tool for fetching and rendering web pages with pluggable parsers.

This tool can fetch URLs, render them (including JavaScript), extract human-readable
content using pluggable parsers, and return structured JSON data.
"""

import json
import time
import math
from typing import Optional, Dict, Any, Type
from urllib.parse import urlparse
from collections import Counter

import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException

from tools.abstract_tool import AbstractTool
from communication.generic_request import GenericRequest
from communication.generic_response import GenericResponse
from tools.parsers import PageParser, DefaultParser


class BrowseUrlTool(AbstractTool):
    """
    A tool for browsing URLs with JavaScript rendering and pluggable content parsing.
    """
    
    def __init__(self, cfg, 
                 enable_javascript: bool = True,
                 timeout: int = 30,
                 max_page_size: int = 10 * 1024 * 1024,  # 10MB
                 user_agent: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"):
        """
        Initialize the BrowseUrlTool.
        
        Args:
            cfg: Configuration object
            enable_javascript: Whether to enable JavaScript rendering
            timeout: Request timeout in seconds
            max_page_size: Maximum page size in bytes
            user_agent: User agent string
        """
        super().__init__("BrowseUrlTool", "Browse and extract content from web pages with pluggable parsers")
        self.cfg = cfg
        self.enable_javascript = enable_javascript
        self.timeout = timeout
        self.max_page_size = max_page_size
        self.headers = {'User-Agent': user_agent}
        
        # Registry of parsers
        self.parsers: Dict[str, PageParser] = {}
        self.default_parser = DefaultParser()
        self.register_parser("default", self.default_parser)
        
        # Domain blacklist for security
        self.domain_blacklist = set([
            'localhost', '127.0.0.1', '0.0.0.0', '::1',
            '192.168.', '10.', '172.16.', '172.17.', '172.18.', '172.19.',
            '172.20.', '172.21.', '172.22.', '172.23.', '172.24.', '172.25.',
            '172.26.', '172.27.', '172.28.', '172.29.', '172.30.', '172.31.'
        ])
    
    def register_parser(self, name: str, parser: PageParser):
        """Register a new parser."""
        self.parsers[name] = parser
        self.cfg.logger.debug(f"Registered parser: {name}")
    
    def get_parser(self, name: str) -> PageParser:
        """Get a parser by name, falling back to default."""
        return self.parsers.get(name, self.default_parser)
    
    def list_parsers(self) -> Dict[str, str]:
        """List available parsers and their descriptions."""
        return {name: parser.description for name, parser in self.parsers.items()}
    
    def calculate_document_score(self, chunk: str, context: Dict[str, Any]) -> float:
        """
        Calculate how relevant a chunk is to the overall document.
        
        Uses improved heuristics based on content length, position, and HTML structure.
        
        Args:
            chunk: The text chunk to score
            context: Additional context (e.g., position, HTML structure)
            
        Returns:
            Score between 0.0 and 1.0
        """
        # Base score from text length (longer content generally more important)
        base_score = min(len(chunk) / 500.0, 1.0)
        
        # Boost score based on HTML context
        tag = context.get('tag', '').lower()
        if tag in ['h1', 'h2', 'h3', 'title']:
            base_score *= 1.5
        elif tag in ['h4', 'h5', 'h6']:
            base_score *= 1.3
        elif tag in ['p', 'div', 'article']:
            base_score *= 1.0
        elif tag in ['span', 'small']:
            base_score *= 0.8
        
        # Boost based on section importance
        section = context.get('section', '').lower()
        if section in ['main', 'article', 'content']:
            base_score *= 1.2
        elif section == 'body':
            base_score *= 1.0
        else:
            base_score *= 0.9
        
        return min(base_score, 1.0)
    
    def calculate_query_score(self, chunk: str, query: str) -> float:
        """
        Calculate how relevant a chunk is to a specific query using cosine similarity.
        
        This implementation uses a simple bag-of-words approach with TF-IDF-like weighting
        and cosine similarity for better semantic matching than simple keyword counting.
        
        Args:
            chunk: The text chunk to score
            query: The user query
            
        Returns:
            Score between 0.0 and 1.0
        """
        if not query or not chunk:
            return 0.0
        
        # Normalize text
        chunk_words = self._normalize_text(chunk).split()
        query_words = self._normalize_text(query).split()
        
        if not chunk_words or not query_words:
            return 0.0
        
        # Create term frequency vectors
        chunk_tf = Counter(chunk_words)
        query_tf = Counter(query_words)
        
        # Get all unique terms
        all_terms = set(chunk_words + query_words)
        
        # Calculate cosine similarity
        return self._cosine_similarity(chunk_tf, query_tf, all_terms)
    
    def _normalize_text(self, text: str) -> str:
        """Normalize text for better matching."""
        import re
        # Convert to lowercase and remove punctuation
        text = re.sub(r'[^\w\s]', ' ', text.lower())
        # Remove extra whitespace
        text = ' '.join(text.split())
        return text
    
    def _cosine_similarity(self, vec1: Counter, vec2: Counter, all_terms: set) -> float:
        """Calculate cosine similarity between two term frequency vectors."""
        # Calculate dot product
        dot_product = sum(vec1.get(term, 0) * vec2.get(term, 0) for term in all_terms)
        
        # Calculate magnitudes
        magnitude1 = math.sqrt(sum(vec1.get(term, 0) ** 2 for term in all_terms))
        magnitude2 = math.sqrt(sum(vec2.get(term, 0) ** 2 for term in all_terms))
        
        # Avoid division by zero
        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0
        
        return dot_product / (magnitude1 * magnitude2)
    
    def _apply_scoring(self, parsed_content, user_query: Optional[str]):
        """Apply scoring to content chunks using the tool's scoring methods."""
        for chunk in parsed_content.visible_text_chunks:
            # Calculate document score
            context = {
                'tag': chunk.tag,
                'section': chunk.section
            }
            chunk.document_score = self.calculate_document_score(chunk.text, context)
            
            # Calculate query score if query provided
            if user_query:
                chunk.query_score = self.calculate_query_score(chunk.text, user_query)
            else:
                chunk.query_score = None
        
        # Sort chunks by document score (and query score if available)
        if user_query:
            # Sort by combined score: 70% query relevance + 30% document score
            parsed_content.visible_text_chunks.sort(
                key=lambda x: (x.query_score or 0) * 0.7 + x.document_score * 0.3,
                reverse=True
            )
        else:
            # Sort by document score only
            parsed_content.visible_text_chunks.sort(
                key=lambda x: x.document_score,
                reverse=True
            )
    
    def run(self, request: GenericRequest) -> GenericResponse:
        """
        Process a browse URL request.
        
        Request content should be either:
        - A URL string
        - A JSON object with 'url', optional 'parser', and optional 'query' fields
        
        Returns:
            GenericResponse with JSON output containing parsed web content
        """
        try:
            # Parse request
            if isinstance(request.content, str):
                try:
                    # Try to parse as JSON first
                    request_data = json.loads(request.content)
                    url = request_data.get('url')
                    parser_name = request_data.get('parser', 'default')
                    user_query = request_data.get('query')
                except json.JSONDecodeError:
                    # Treat as plain URL
                    url = request.content.strip()
                    parser_name = 'default'
                    user_query = None
            else:
                raise ValueError("Request content must be a string")
            
            if not url:
                raise ValueError("URL is required")
            
            self.cfg.logger.debug(f"BrowseUrlTool: Processing URL: {url}")
            
            # Validate URL
            self._validate_url(url)
            
            # Get parser
            parser = self.get_parser(parser_name)
            
            # Fetch and render the page
            html_content, title = self._fetch_page(url)
            
            # Parse content
            parsed_content = parser.parse(url, html_content, title, user_query)
            
            # Apply scoring using the tool's scoring methods
            self._apply_scoring(parsed_content, user_query)
            
            # Convert to JSON output
            output = self._format_output(parsed_content)
            
            return GenericResponse(output=json.dumps(output, indent=2))
            
        except Exception as e:
            self.cfg.logger.error(f"BrowseUrlTool error: {str(e)}")
            error_output = {
                "title": "Error",
                "visible_text_chunks": [],
                "metadata": {},
                "links": [],
                "media": [],
                "source_url": url if 'url' in locals() else "",
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
                "parser_used": parser_name if 'parser_name' in locals() else "unknown",
                "error": str(e)
            }
            return GenericResponse(output=json.dumps(error_output, indent=2))
    
    def _validate_url(self, url: str):
        """Validate URL for security and format."""
        try:
            parsed = urlparse(url)
            
            # Check scheme
            if parsed.scheme not in ['http', 'https']:
                raise ValueError(f"Unsupported URL scheme: {parsed.scheme}")
            
            # Check for blacklisted domains/IPs
            hostname = parsed.hostname or ""
            for blocked in self.domain_blacklist:
                if hostname.startswith(blocked):
                    raise ValueError(f"Access to {hostname} is not allowed")
            
        except Exception as e:
            raise ValueError(f"Invalid URL: {str(e)}")
    
    def _fetch_page(self, url: str) -> tuple[str, str]:
        """
        Fetch page content, optionally rendering JavaScript.
        
        Returns:
            Tuple of (html_content, title)
        """
        if self.enable_javascript:
            return self._fetch_with_selenium(url)
        else:
            return self._fetch_with_requests(url)
    
    def _fetch_with_requests(self, url: str) -> tuple[str, str]:
        """Fetch page using requests (no JavaScript)."""
        try:
            response = requests.get(
                url, 
                headers=self.headers, 
                timeout=self.timeout,
                stream=True
            )
            response.raise_for_status()
            
            # Check content length
            content_length = response.headers.get('content-length')
            if content_length and int(content_length) > self.max_page_size:
                raise ValueError(f"Page too large: {content_length} bytes")
            
            # Read content with size limit
            content = ""
            total_size = 0
            for chunk in response.iter_content(chunk_size=8192, decode_unicode=True):
                if chunk:
                    total_size += len(chunk)
                    if total_size > self.max_page_size:
                        raise ValueError(f"Page too large: {total_size} bytes")
                    content += chunk
            
            # Extract title using simple parsing
            title = ""
            title_match = content.find('<title>')
            if title_match != -1:
                title_end = content.find('</title>', title_match)
                if title_end != -1:
                    title = content[title_match + 7:title_end].strip()
            
            return content, title
            
        except requests.RequestException as e:
            raise ValueError(f"Failed to fetch URL: {str(e)}")
    
    def _fetch_with_selenium(self, url: str) -> tuple[str, str]:
        """Fetch page using Selenium (with JavaScript)."""
        driver = None
        try:
            # Configure Chrome options
            chrome_options = Options()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--disable-extensions')
            chrome_options.add_argument('--disable-images')  # Skip images for faster loading
            chrome_options.add_argument(f'--user-agent={self.headers["User-Agent"]}')
            
            # Start driver
            driver = webdriver.Chrome(options=chrome_options)
            driver.set_page_load_timeout(self.timeout)
            
            # Load page
            driver.get(url)
            
            # Wait for page to be ready
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Give dynamic content a moment to load
            time.sleep(2)
            
            # Get content
            html_content = driver.page_source
            title = driver.title
            
            # Check size
            if len(html_content) > self.max_page_size:
                raise ValueError(f"Rendered page too large: {len(html_content)} bytes")
            
            return html_content, title
            
        except (TimeoutException, WebDriverException) as e:
            raise ValueError(f"Failed to render page: {str(e)}")
        finally:
            if driver:
                try:
                    driver.quit()
                except:
                    pass
    
    def _format_output(self, parsed_content) -> Dict[str, Any]:
        """Format ParsedContent into the required JSON structure."""
        return {
            "title": parsed_content.title,
            "visible_text_chunks": [
                {
                    "text": chunk.text,
                    "document_score": chunk.document_score,
                    "query_score": chunk.query_score,
                    "section": chunk.section,
                    "tag": chunk.tag
                }
                for chunk in parsed_content.visible_text_chunks
            ],
            "metadata": parsed_content.metadata,
            "links": parsed_content.links,
            "media": parsed_content.media,
            "source_url": parsed_content.source_url,
            "timestamp": parsed_content.timestamp,
            "parser_used": parsed_content.parser_used,
            "error": parsed_content.error
        }