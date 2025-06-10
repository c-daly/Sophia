# BrowseUrlTool and Parser Interface Documentation

## Overview

The `BrowseUrlTool` is a sophisticated web browsing tool that can fetch URLs, render pages (including JavaScript), extract human-readable content using pluggable parsers, and return structured JSON data. The tool supports extensible content extraction strategies through a pluggable parser interface.

## Key Features

- **JavaScript Rendering**: Optional JavaScript execution using Selenium WebDriver
- **Pluggable Parsers**: Extensible parser interface for specialized content extraction
- **Query Relevance Scoring**: Score content chunks for relevance to user queries
- **Security**: Built-in domain blacklisting and content size limits
- **Structured Output**: Standardized JSON output format
- **Error Handling**: Comprehensive error handling with structured error responses

## Usage

### Basic Usage

```python
from tools.browse_url_tool import BrowseUrlTool
from communication.generic_request import GenericRequest
from config import Configurator

# Initialize the tool
cfg = Configurator()
tool = BrowseUrlTool(cfg)

# Simple URL request
request = GenericRequest("https://example.com")
response = tool.run(request)
result = json.loads(response.output)
```

### Advanced Usage with JSON Request

```python
import json

# JSON request with parser and query
request_data = {
    "url": "https://example.com/article",
    "parser": "default",
    "query": "machine learning"
}
request = GenericRequest(json.dumps(request_data))
response = tool.run(request)
result = json.loads(response.output)
```

## Parser Interface

### PageParser Abstract Base Class

All parsers must inherit from the `PageParser` abstract base class and implement the following methods:

```python
from tools.parsers import PageParser, ContentChunk, ParsedContent

class CustomParser(PageParser):
    @property
    def name(self) -> str:
        return "CustomParser"
    
    @property
    def description(self) -> str:
        return "Parser for custom content extraction"
    
    def can_parse(self, url: str, html_content: str, mime_type: str = None) -> bool:
        # Return True if this parser can handle the content
        return "custom-site.com" in url
    
    def parse(self, url: str, html_content: str, title: str = "", 
              user_query: Optional[str] = None) -> ParsedContent:
        # Implement custom parsing logic
        # Return ParsedContent object with extracted data
        pass
```

### Required Methods

#### `name` (property)
Returns the name of the parser as a string.

#### `description` (property)
Returns a description of what this parser does.

#### `can_parse(url, html_content, mime_type=None)`
Determines if this parser can handle the given content.
- **url**: The URL of the page
- **html_content**: The raw HTML content
- **mime_type**: The MIME type (optional)
- **Returns**: Boolean indicating if this parser can handle the content

#### `parse(url, html_content, title="", user_query=None)`
Parses HTML content and extracts structured information.
- **url**: The source URL
- **html_content**: The HTML content to parse
- **title**: The page title (if already extracted)
- **user_query**: Optional user query for relevance scoring
- **Returns**: `ParsedContent` object with extracted data

### Data Structures

#### ContentChunk
Represents a chunk of extracted content with relevance scores:

```python
@dataclass
class ContentChunk:
    text: str                           # The extracted text
    document_score: float               # Relevance to overall document (0.0-1.0)
    query_score: Optional[float]        # Relevance to user query (0.0-1.0)
    section: Optional[str]              # HTML section this came from
    tag: Optional[str]                  # Specific HTML tag
```

#### ParsedContent
Container for all parsed content from a web page:

```python
@dataclass
class ParsedContent:
    title: str                          # Page title
    visible_text_chunks: List[ContentChunk]  # Extracted content chunks
    metadata: Dict[str, Any]            # Page metadata
    links: List[Dict[str, str]]         # Extracted links
    media: List[Dict[str, str]]         # Media elements (images, videos)
    source_url: str                     # Source URL
    timestamp: str                      # Processing timestamp (ISO format)
    parser_used: str                    # Name of parser used
    error: Optional[str]                # Error message if any
```

## Output Format

The tool returns a JSON object with the following structure:

```json
{
    "title": "Page Title",
    "visible_text_chunks": [
        {
            "text": "Content chunk text",
            "document_score": 0.85,
            "query_score": 0.62,
            "section": "main",
            "tag": "p"
        }
    ],
    "metadata": {
        "description": "Page description",
        "keywords": "keyword1, keyword2",
        "language": "en",
        "estimated_word_count": 450
    },
    "links": [
        {
            "url": "https://example.com/link",
            "text": "Link text",
            "title": "Link title"
        }
    ],
    "media": [
        {
            "type": "image",
            "url": "https://example.com/image.jpg",
            "alt": "Image description",
            "title": "Image title"
        }
    ],
    "source_url": "https://example.com",
    "timestamp": "2024-01-15T10:30:00",
    "parser_used": "DefaultParser",
    "error": null
}
```

## Creating Custom Parsers

### Example: News Article Parser

```python
from tools.parsers import PageParser, ContentChunk, ParsedContent
from bs4 import BeautifulSoup
from datetime import datetime

class NewsArticleParser(PageParser):
    @property
    def name(self) -> str:
        return "NewsArticleParser"
    
    @property
    def description(self) -> str:
        return "Specialized parser for news articles"
    
    def can_parse(self, url: str, html_content: str, mime_type: str = None) -> bool:
        # Check if this looks like a news article
        soup = BeautifulSoup(html_content, 'html.parser')
        return bool(soup.find('article') or soup.find('.article') or 
                   soup.find('[itemtype*="Article"]'))
    
    def parse(self, url: str, html_content: str, title: str = "", 
              user_query: Optional[str] = None) -> ParsedContent:
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Extract article content specifically
        article = soup.find('article') or soup.find('.article-content')
        
        if article:
            chunks = self._extract_article_chunks(article, user_query)
        else:
            # Fallback to default extraction
            chunks = self._extract_default_chunks(soup, user_query)
        
        return ParsedContent(
            title=title or soup.find('title').get_text(),
            visible_text_chunks=chunks,
            metadata=self._extract_news_metadata(soup),
            links=self._extract_links(soup, url),
            media=self._extract_media(soup, url),
            source_url=url,
            timestamp=datetime.now().isoformat(),
            parser_used=self.name
        )
```

### Registering Custom Parsers

```python
# Register a custom parser with the tool
tool = BrowseUrlTool(cfg)
custom_parser = NewsArticleParser()
tool.register_parser("news", custom_parser)

# List available parsers
parsers = tool.list_parsers()
print(parsers)  # {'default': '...', 'news': 'Specialized parser for news articles'}
```

## Configuration Options

### BrowseUrlTool Constructor Parameters

- **cfg**: Configuration object (required)
- **enable_javascript**: Enable JavaScript rendering with Selenium (default: True)
- **timeout**: Request timeout in seconds (default: 30)
- **max_page_size**: Maximum page size in bytes (default: 10MB)
- **user_agent**: User agent string for requests

### DefaultParser Constructor Parameters

- **max_chunks**: Maximum number of content chunks to extract (default: 50)
- **max_chunk_size**: Maximum size of each chunk in characters (default: 1000)

## Security Features

### Domain Blacklisting
The tool includes built-in protection against accessing internal/private networks:
- localhost, 127.0.0.1, private IP ranges
- Configurable blacklist can be extended

### Content Size Limits
- Maximum page size limit (default 10MB)
- Maximum number of content chunks
- Request timeouts

### URL Validation
- Only HTTP and HTTPS schemes allowed
- URL format validation
- Domain blacklist enforcement

## Error Handling

All errors are returned in a standardized format:

```json
{
    "title": "Error",
    "visible_text_chunks": [],
    "metadata": {},
    "links": [],
    "media": [],
    "source_url": "https://failed-url.com",
    "timestamp": "2024-01-15T10:30:00",
    "parser_used": "DefaultParser",
    "error": "Failed to fetch URL: Connection timeout"
}
```

## Best Practices

### Parser Design
1. **Specific can_parse() logic**: Only claim compatibility when you can genuinely improve extraction
2. **Fallback behavior**: Handle edge cases gracefully
3. **Performance**: Avoid expensive operations in can_parse()
4. **Scoring**: Provide meaningful document and query scores

### Tool Usage
1. **JavaScript rendering**: Enable only when necessary (slower but more complete)
2. **Query optimization**: Use specific queries for better relevance scoring
3. **Parser selection**: Choose appropriate parsers for your content type
4. **Error handling**: Always check for errors in the response

### Extension Points
1. **Custom scoring algorithms**: Override scoring methods in parsers
2. **Domain-specific extraction**: Create parsers for specific websites/content types
3. **Multi-language support**: Add language-specific processing
4. **Content filtering**: Implement content quality filters