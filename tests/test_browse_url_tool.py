"""
Tests for the browse_url tool and parser interface.
"""

import unittest
import json
from unittest.mock import Mock, patch, MagicMock

from tools.browse_url_tool import BrowseUrlTool
from tools.parsers import DefaultParser, PageParser, ContentChunk, ParsedContent
from communication.generic_request import GenericRequest
from config import Configurator


class TestPageParser(unittest.TestCase):
    """Test the PageParser base class and its methods."""
    
    def setUp(self):
        self.parser = DefaultParser()
        # Create a basic config for the tool
        class MockConfig:
            def __init__(self):
                self.logger = self
                
            def debug(self, msg):
                pass
                
            def error(self, msg):
                pass
        
        self.tool = BrowseUrlTool(MockConfig(), enable_javascript=False)
    
    def test_chunk_text(self):
        """Test text chunking functionality."""
        # Test short text (no chunking needed)
        short_text = "This is a short text."
        chunks = self.parser.chunk_text(short_text, max_chunk_size=100)
        self.assertEqual(len(chunks), 1)
        self.assertEqual(chunks[0], short_text)
        
        # Test long text (needs chunking)
        long_text = " ".join(["word"] * 50)  # 200 chars (50 words * 4 chars each)
        chunks = self.parser.chunk_text(long_text, max_chunk_size=50)
        self.assertGreater(len(chunks), 1)
        
        # Verify no chunk exceeds max size
        for chunk in chunks:
            self.assertLessEqual(len(chunk), 50)
    
    def test_document_score_calculation(self):
        """Test document score calculation."""
        # Test basic scoring
        chunk = "This is a sample text chunk for testing."
        context = {'tag': 'p', 'section': 'main'}
        score = self.tool.calculate_document_score(chunk, context)
        self.assertGreaterEqual(score, 0.0)
        self.assertLessEqual(score, 1.0)
        
        # Test heading boost
        context_heading = {'tag': 'h1', 'section': 'main'}
        score_heading = self.tool.calculate_document_score(chunk, context_heading)
        score_paragraph = self.tool.calculate_document_score(chunk, {'tag': 'p'})
        self.assertGreater(score_heading, score_paragraph)
    
    def test_query_score_calculation(self):
        """Test query relevance scoring."""
        chunk = "This article discusses machine learning algorithms and neural networks."
        
        # Test exact match
        score_exact = self.tool.calculate_query_score(chunk, "machine learning")
        self.assertGreater(score_exact, 0.0)
        
        # Test partial match
        score_partial = self.tool.calculate_query_score(chunk, "machines")
        self.assertGreaterEqual(score_partial, 0.0)
        
        # Test no match
        score_none = self.tool.calculate_query_score(chunk, "quantum physics")
        self.assertEqual(score_none, 0.0)
        
        # Test empty query
        score_empty = self.tool.calculate_query_score(chunk, "")
        self.assertEqual(score_empty, 0.0)


class TestDefaultParser(unittest.TestCase):
    """Test the DefaultParser implementation."""
    
    def setUp(self):
        self.parser = DefaultParser()
    
    def test_can_parse(self):
        """Test that DefaultParser can parse any content."""
        self.assertTrue(self.parser.can_parse("http://example.com", "<html></html>"))
        self.assertTrue(self.parser.can_parse("http://example.com", ""))
    
    def test_parse_simple_html(self):
        """Test parsing simple HTML content."""
        html = """
        <html>
        <head><title>Test Page</title></head>
        <body>
            <h1>Main Heading</h1>
            <p>This is a paragraph with some content.</p>
            <a href="http://example.com">Example Link</a>
            <img src="image.jpg" alt="Test Image">
        </body>
        </html>
        """
        
        result = self.parser.parse("http://test.com", html, user_query="content")
        
        # Check basic structure
        self.assertEqual(result.title, "Test Page")
        self.assertEqual(result.source_url, "http://test.com")
        self.assertEqual(result.parser_used, "DefaultParser")
        self.assertIsNone(result.error)
        
        # Check content chunks
        self.assertGreater(len(result.visible_text_chunks), 0)
        
        # Check that heading was extracted
        heading_found = any("Main Heading" in chunk.text for chunk in result.visible_text_chunks)
        self.assertTrue(heading_found)
        
        # Check links
        self.assertGreater(len(result.links), 0)
        self.assertEqual(result.links[0]['url'], "http://example.com")
        
        # Check media
        self.assertGreater(len(result.media), 0)
        self.assertIn("image.jpg", result.media[0]['url'])
    
    def test_parse_with_query_scoring(self):
        """Test parsing with query relevance scoring."""
        html = """
        <html>
        <body>
            <p>This paragraph talks about machine learning concepts.</p>
            <p>This paragraph discusses cooking recipes.</p>
        </body>
        </html>
        """
        
        # Parse first, then apply scoring using tool
        result = self.parser.parse("http://test.com", html, user_query="machine learning")
        
        # Create a tool instance to handle scoring
        class MockConfig:
            def __init__(self):
                self.logger = self
                
            def debug(self, msg):
                pass
                
            def error(self, msg):
                pass
        
        tool = BrowseUrlTool(MockConfig(), enable_javascript=False)
        
        # Apply scoring
        tool._apply_scoring(result, "machine learning")
        
        # Check that query scores were calculated
        for chunk in result.visible_text_chunks:
            self.assertIsNotNone(chunk.query_score)
        
        # Find chunks with different relevance
        ml_chunk = next((c for c in result.visible_text_chunks if "machine learning" in c.text), None)
        cooking_chunk = next((c for c in result.visible_text_chunks if "cooking" in c.text), None)
        
        if ml_chunk and cooking_chunk:
            self.assertGreater(ml_chunk.query_score, cooking_chunk.query_score)


class TestBrowseUrlTool(unittest.TestCase):
    """Test the BrowseUrlTool implementation."""
    
    def setUp(self):
        # Mock configuration
        self.cfg = Mock()
        self.cfg.logger = Mock()
        
        # Create tool with JavaScript disabled for testing
        self.tool = BrowseUrlTool(self.cfg, enable_javascript=False)
    
    def test_parser_registration(self):
        """Test parser registration and retrieval."""
        # Test default parser is registered
        parsers = self.tool.list_parsers()
        self.assertIn("default", parsers)
        
        # Test custom parser registration
        custom_parser = Mock(spec=PageParser)
        custom_parser.description = "Custom test parser"
        self.tool.register_parser("custom", custom_parser)
        
        parsers = self.tool.list_parsers()
        self.assertIn("custom", parsers)
        self.assertEqual(parsers["custom"], "Custom test parser")
    
    def test_url_validation(self):
        """Test URL validation."""
        # Valid URLs
        self.tool._validate_url("http://example.com")
        self.tool._validate_url("https://example.com/path")
        
        # Invalid schemes
        with self.assertRaises(ValueError):
            self.tool._validate_url("ftp://example.com")
        
        # Blacklisted domains
        with self.assertRaises(ValueError):
            self.tool._validate_url("http://localhost")
        
        with self.assertRaises(ValueError):
            self.tool._validate_url("http://127.0.0.1")
    
    @patch('tools.browse_url_tool.requests.get')
    def test_fetch_with_requests(self, mock_get):
        """Test fetching content with requests."""
        # Mock response
        mock_response = Mock()
        mock_response.headers = {'content-length': '1000'}
        mock_response.iter_content.return_value = [
            "<html><head><title>Test</title></head><body>Content</body></html>"
        ]
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        html, title = self.tool._fetch_with_requests("http://example.com")
        
        self.assertIn("<html>", html)
        self.assertEqual(title, "Test")
    
    def test_request_parsing(self):
        """Test different request formats."""
        # Test plain URL
        request = GenericRequest("http://example.com")
        
        # Mock the fetch method to avoid actual network calls
        with patch.object(self.tool, '_fetch_page') as mock_fetch:
            mock_fetch.return_value = ("<html><title>Test</title><body>Test content</body></html>", "Test")
            
            response = self.tool.run(request)
            
            # Parse response
            result = json.loads(response.output)
            self.assertEqual(result['title'], 'Test')
            self.assertEqual(result['source_url'], 'http://example.com')
            self.assertEqual(result['parser_used'], 'DefaultParser')
    
    def test_json_request_format(self):
        """Test JSON request format."""
        request_data = {
            "url": "http://example.com",
            "parser": "default",
            "query": "test query"
        }
        request = GenericRequest(json.dumps(request_data))
        
        # Mock the fetch method
        with patch.object(self.tool, '_fetch_page') as mock_fetch:
            mock_fetch.return_value = ("<html><title>Test</title><body>Test content query</body></html>", "Test")
            
            response = self.tool.run(request)
            
            # Parse response
            result = json.loads(response.output)
            self.assertEqual(result['title'], 'Test')
            self.assertEqual(result['source_url'], 'http://example.com')
            
            # Check that query scoring was applied
            for chunk in result['visible_text_chunks']:
                if chunk['query_score'] is not None:
                    self.assertGreaterEqual(chunk['query_score'], 0.0)
    
    def test_error_handling(self):
        """Test error handling in the tool."""
        # Test invalid URL
        request = GenericRequest("invalid-url")
        response = self.tool.run(request)
        result = json.loads(response.output)
        self.assertIsNotNone(result['error'])
        
        # Test empty request
        request = GenericRequest("")
        response = self.tool.run(request)
        result = json.loads(response.output)
        self.assertIsNotNone(result['error'])


if __name__ == "__main__":
    unittest.main()